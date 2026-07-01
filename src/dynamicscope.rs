// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::exceptions::{PyAttributeError, PyKeyError, PyTypeError};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyString, PyTuple};

/// User key error exception for missing scope keys
#[pyclass(extends = PyKeyError)]
pub struct UserKeyError;

/// Wrapper for accessing owner attributes through the nonlocals mechanism
#[pyclass]
pub struct Nonlocals {
    owner: Py<PyAny>,
    tracer: Py<PyAny>,
}

#[pymethods]
impl Nonlocals {
    #[new]
    pub fn new(owner: Py<PyAny>, tracer: Py<PyAny>) -> Self {
        Nonlocals { owner, tracer }
    }

    pub fn __contains__(&self, py: Python<'_>, key: &Bound<'_, PyAny>) -> PyResult<bool> {
        // Validate key is a string
        if !key.is_instance_of::<PyString>() {
            return Err(PyTypeError::new_err("expected string key"));
        }

        let key_str = key.extract::<&str>()?;
        if key_str.starts_with('_') {
            return Ok(false);
        }

        let owner = self.owner.bind(py);
        Ok(owner.hasattr(key_str)?)
    }

    pub fn __getattr__(&self, py: Python<'_>, name: &str) -> PyResult<Py<PyAny>> {
        if name.starts_with('_') {
            return Err(PyAttributeError::new_err(format!(
                "'Nonlocals' object has no attribute '{}'",
                name
            )));
        }

        let owner = self.owner.bind(py);
        match owner.getattr(name) {
            Ok(value) => {
                // Convert value to Py first
                let value_py: Py<PyAny> = value.clone().into();

                // Call tracer.dynamic_load if tracer is callable
                let tracer = self.tracer.bind(py);
                if tracer.is_callable() {
                    let _ = tracer.call_method(
                        "dynamic_load",
                        (self.owner.clone_ref(py), name, value_py.clone_ref(py)),
                        None,
                    );
                }
                Ok(value_py)
            }
            Err(_) => Err(PyAttributeError::new_err(format!(
                "owner has no attribute '{}'",
                name
            ))),
        }
    }

    pub fn __repr__(&self) -> String {
        format!("Nonlocals[{:p}]", self as *const _)
    }
}

/// Dynamic scope for Enaml expressions.
///
/// Implements dynamic scoping with owner hierarchy traversal and change tracking.
#[pyclass]
pub struct DynamicScope {
    owner: Py<PyAny>,
    f_locals: Py<PyDict>,
    f_globals: Py<PyDict>,
    f_builtins: Py<PyDict>,
    change: Py<PyAny>,
    tracer: Py<PyAny>,
    f_writes: std::cell::UnsafeCell<Option<Py<PyDict>>>,
}

// SAFETY: f_writes is only modified when we hold a &mut self or through controlled access.
// Since PyO3 ensures single-threaded execution within method calls, this is safe.
unsafe impl Sync for DynamicScope {}

#[pymethods]
impl DynamicScope {
    #[new]
    pub fn new(
        py: Python<'_>,
        owner: Py<PyAny>,
        f_locals: Py<PyAny>,
        f_globals: Py<PyAny>,
        f_builtins: Py<PyAny>,
        change: Py<PyAny>,
        tracer: Py<PyAny>,
    ) -> PyResult<Self> {
        // Validate f_locals is a mapping
        let f_locals_bound = f_locals.bind(py);
        if !f_locals_bound.hasattr("__getitem__")? {
            return Err(PyTypeError::new_err("f_locals must be a mapping"));
        }

        // Extract f_globals and f_builtins as dicts
        let f_globals_dict: Bound<'_, PyDict> = match f_globals.extract(py) {
            Ok(d) => d,
            Err(_) => return Err(PyTypeError::new_err("f_globals must be a dict")),
        };

        let f_builtins_dict: Bound<'_, PyDict> = match f_builtins.extract(py) {
            Ok(d) => d,
            Err(_) => return Err(PyTypeError::new_err("f_builtins must be a dict")),
        };

        // Convert f_locals to dict
        let f_locals_dict = if let Ok(d) = f_locals.extract::<Bound<'_, PyDict>>(py) {
            d.into()
        } else {
            // Try to create dict from mapping
            let new_dict = PyDict::new(py);
            if let Ok(items_obj) = f_locals_bound.call_method0("items") {
                // Try to convert to list first to enable indexing
                if let Ok(items_list) = items_obj.extract::<Bound<'_, pyo3::types::PyList>>() {
                    for i in 0..items_list.len() {
                        if let Ok(item) = items_list.get_item(i) {
                            let tuple: Bound<'_, PyTuple> = match item.extract() {
                                Ok(t) => t,
                                Err(_) => continue,
                            };
                            if tuple.len() == 2 {
                                if let (Ok(k), Ok(v)) = (tuple.get_item(0), tuple.get_item(1)) {
                                    let _ = new_dict.set_item(&k, &v);
                                }
                            }
                        }
                    }
                }
            }
            new_dict.into()
        };

        Ok(DynamicScope {
            owner,
            f_locals: f_locals_dict,
            f_globals: f_globals_dict.into(),
            f_builtins: f_builtins_dict.into(),
            change,
            tracer,
            f_writes: std::cell::UnsafeCell::new(None),
        })
    }

    pub fn __getitem__(&self, py: Python<'_>, key: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
        // Validate key is a string
        if !key.is_instance_of::<PyString>() {
            return Err(PyTypeError::new_err("expected string key"));
        }

        let key_str = key.extract::<&str>()?;

        // 1. Check special keys
        match key_str {
            "self" => return Ok(self.owner.clone_ref(py)),
            "change" => return Ok(self.change.clone_ref(py)),
            "__scope__" => {
                // Create and return a DynamicScope instance
                return Py::new(
                    py,
                    DynamicScope {
                        owner: self.owner.clone_ref(py),
                        f_locals: self.f_locals.clone_ref(py),
                        f_globals: self.f_globals.clone_ref(py),
                        f_builtins: self.f_builtins.clone_ref(py),
                        change: self.change.clone_ref(py),
                        tracer: self.tracer.clone_ref(py),
                        f_writes: std::cell::UnsafeCell::new(None),
                    },
                )
                .map(|p| p.into());
            }
            "_[tracer]" => return Ok(self.tracer.clone_ref(py)),
            "nonlocals" => {
                return Py::new(
                    py,
                    Nonlocals::new(self.owner.clone_ref(py), self.tracer.clone_ref(py)),
                )
                .map(|p| p.into());
            }
            _ => {}
        }

        // 2. Check f_writes
        unsafe {
            if let Some(writes) = &*self.f_writes.get() {
                if writes.bind(py).contains(key)? {
                    if let Some(val) = writes.bind(py).get_item(key)? {
                        return Ok(val.into());
                    }
                }
            }
        }

        // 3. Check f_locals
        if self.f_locals.bind(py).contains(key)? {
            if let Some(val) = self.f_locals.bind(py).get_item(key)? {
                return Ok(val.into());
            }
        }

        // 4. Check f_globals
        if self.f_globals.bind(py).contains(key)? {
            if let Some(val) = self.f_globals.bind(py).get_item(key)? {
                return Ok(val.into());
            }
        }

        // 5. Check f_builtins
        if self.f_builtins.bind(py).contains(key)? {
            if let Some(val) = self.f_builtins.bind(py).get_item(key)? {
                return Ok(val.into());
            }
        }

        // 6. Check owner hierarchy
        let mut current = Some(self.owner.clone_ref(py));
        while let Some(obj) = current {
            let obj_bound = obj.bind(py);
            if obj_bound.hasattr(key_str)? {
                return Ok(obj_bound.getattr(key_str)?.into());
            }

            // Try parent
            current = if let Ok(parent) = obj_bound.getattr("_parent") {
                if !parent.is_none() {
                    Some(parent.into())
                } else {
                    None
                }
            } else {
                None
            };
        }

        // Not found
        Err(PyKeyError::new_err(key_str.to_string()))
    }

    pub fn __setitem__(
        &self,
        py: Python<'_>,
        key: &Bound<'_, PyAny>,
        value: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        // Validate key is a string
        if !key.is_instance_of::<PyString>() {
            return Err(PyTypeError::new_err("expected string key"));
        }

        unsafe {
            // Create f_writes if needed
            if (*self.f_writes.get()).is_none() {
                *self.f_writes.get() = Some(PyDict::new(py).into());
            }

            // Set in f_writes
            if let Some(writes) = &*self.f_writes.get() {
                writes.bind(py).set_item(key, value)?;
            }
        }

        Ok(())
    }

    pub fn __delitem__(&self, py: Python<'_>, key: &Bound<'_, PyAny>) -> PyResult<()> {
        // Validate key is a string
        if !key.is_instance_of::<PyString>() {
            return Err(PyTypeError::new_err("expected string key"));
        }

        unsafe {
            // Delete from f_writes only
            if let Some(writes) = &*self.f_writes.get() {
                writes.bind(py).del_item(key)?;
            } else {
                let key_str = key.extract::<&str>().unwrap_or("<unknown>");
                return Err(PyKeyError::new_err(key_str.to_string()));
            }
        }

        Ok(())
    }

    pub fn __contains__(&self, py: Python<'_>, key: &Bound<'_, PyAny>) -> PyResult<bool> {
        // Validate key is a string
        if !key.is_instance_of::<PyString>() {
            return Err(PyTypeError::new_err("expected string key"));
        }

        let key_str = key.extract::<&str>()?;

        // Check special keys
        if matches!(
            key_str,
            "self" | "change" | "__scope__" | "_[tracer]" | "nonlocals"
        ) {
            return Ok(true);
        }

        // Check f_writes
        unsafe {
            if let Some(writes) = &*self.f_writes.get() {
                if writes.bind(py).contains(key)? {
                    return Ok(true);
                }
            }
        }

        // Check f_locals, f_globals, f_builtins
        if self.f_locals.bind(py).contains(key)?
            || self.f_globals.bind(py).contains(key)?
            || self.f_builtins.bind(py).contains(key)?
        {
            return Ok(true);
        }

        // Check owner hierarchy
        let mut current = Some(self.owner.clone_ref(py));
        while let Some(obj) = current {
            let obj_bound = obj.bind(py);
            if obj_bound.hasattr(key_str)? {
                return Ok(true);
            }

            current = if let Ok(parent) = obj_bound.getattr("_parent") {
                if !parent.is_none() {
                    Some(parent.into())
                } else {
                    None
                }
            } else {
                None
            };
        }

        Ok(false)
    }

    pub fn get(
        &self,
        py: Python<'_>,
        key: &Bound<'_, PyAny>,
        default: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        match self.__getitem__(py, key) {
            Ok(val) => Ok(val),
            Err(_) => {
                if let Some(d) = default {
                    Ok(d.into())
                } else {
                    Ok(py.None())
                }
            }
        }
    }

    pub fn __iter__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let mut keys = std::collections::HashSet::new();

        // Add special keys
        keys.insert("self".to_string());
        keys.insert("change".to_string());
        keys.insert("__scope__".to_string());
        keys.insert("_[tracer]".to_string());
        keys.insert("nonlocals".to_string());

        // Add from f_writes
        unsafe {
            if let Some(writes) = &*self.f_writes.get() {
                let writes_dict = writes.bind(py);
                for key_result in writes_dict.keys() {
                    if let Ok(k) = key_result.extract::<&str>() {
                        if !k.starts_with('_') {
                            keys.insert(k.to_string());
                        }
                    }
                }
            }
        }

        // Add from f_locals
        {
            let f_locals_dict = self.f_locals.bind(py);
            for key_result in f_locals_dict.keys() {
                if let Ok(k) = key_result.extract::<&str>() {
                    if !k.starts_with('_') {
                        keys.insert(k.to_string());
                    }
                }
            }
        }

        // Add from f_globals
        {
            let f_globals_dict = self.f_globals.bind(py);
            for key_result in f_globals_dict.keys() {
                if let Ok(k) = key_result.extract::<&str>() {
                    if !k.starts_with('_') {
                        keys.insert(k.to_string());
                    }
                }
            }
        }

        // Add from f_builtins
        {
            let f_builtins_dict = self.f_builtins.bind(py);
            for key_result in f_builtins_dict.keys() {
                if let Ok(k) = key_result.extract::<&str>() {
                    if !k.starts_with('_') {
                        keys.insert(k.to_string());
                    }
                }
            }
        }

        // Add from owner hierarchy
        let mut current = Some(self.owner.clone_ref(py));
        while let Some(obj) = current {
            let obj_bound = obj.bind(py);
            if let Ok(dir_result_obj) = obj_bound.call_method0("__dir__") {
                // Try to convert to list first
                if let Ok(dir_list) = dir_result_obj.extract::<Bound<'_, pyo3::types::PyList>>() {
                    for i in 0..dir_list.len() {
                        if let Ok(attr_item) = dir_list.get_item(i) {
                            if let Ok(a) = attr_item.extract::<&str>() {
                                if !a.starts_with('_') {
                                    keys.insert(a.to_string());
                                }
                            }
                        }
                    }
                }
            }

            current = if let Ok(parent) = obj_bound.getattr("_parent") {
                if !parent.is_none() {
                    Some(parent.into())
                } else {
                    None
                }
            } else {
                None
            };
        }

        // Convert to list
        let key_list: Vec<String> = keys.into_iter().collect();
        Ok(pyo3::types::PyList::new(py, key_list)?.into())
    }

    pub fn keys(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.__iter__(py)
    }

    pub fn values(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let keys_list = self.__iter__(py)?;
        let mut values = Vec::new();

        // Convert to list and index
        if let Ok(keys_as_list) = keys_list
            .bind(py)
            .extract::<Bound<'_, pyo3::types::PyList>>()
        {
            for i in 0..keys_as_list.len() {
                if let Ok(k) = keys_as_list.get_item(i) {
                    if let Ok(v) = self.__getitem__(py, &k) {
                        values.push(v);
                    }
                }
            }
        }

        Ok(pyo3::types::PyList::new(py, values)?.into())
    }

    pub fn items(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let keys_list = self.__iter__(py)?;
        let mut items = Vec::new();

        // Convert to list and index
        if let Ok(keys_as_list) = keys_list
            .bind(py)
            .extract::<Bound<'_, pyo3::types::PyList>>()
        {
            for i in 0..keys_as_list.len() {
                if let Ok(k) = keys_as_list.get_item(i) {
                    if let Ok(v) = self.__getitem__(py, &k) {
                        let k_py: Py<PyAny> = k.into();
                        items.push((k_py, v));
                    }
                }
            }
        }

        Ok(pyo3::types::PyList::new(py, items)?.into())
    }

    pub fn update(&self, py: Python<'_>, other: &Bound<'_, PyAny>) -> PyResult<()> {
        // Validate other is a mapping
        if !other.hasattr("items")? {
            return Err(PyTypeError::new_err("expected mapping"));
        }

        unsafe {
            // Create f_writes if needed
            if (*self.f_writes.get()).is_none() {
                *self.f_writes.get() = Some(PyDict::new(py).into());
            }

            // Update from mapping
            let items_result = other.call_method0("items");
            if let Ok(items_obj) = items_result {
                // Try to convert to list first
                if let Ok(items_list) = items_obj.extract::<Bound<'_, pyo3::types::PyList>>() {
                    for i in 0..items_list.len() {
                        if let Ok(item) = items_list.get_item(i) {
                            let tuple: Bound<'_, PyTuple> = match item.extract() {
                                Ok(t) => t,
                                Err(_) => continue,
                            };
                            if tuple.len() == 2 {
                                if let (Ok(k), Ok(v)) = (tuple.get_item(0), tuple.get_item(1)) {
                                    // Validate key is string
                                    if !k.is_instance_of::<PyString>() {
                                        return Err(PyTypeError::new_err("keys must be strings"));
                                    }

                                    // Set in f_writes
                                    if let Some(writes) = &*self.f_writes.get() {
                                        writes.bind(py).set_item(&k, &v)?;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Ok(())
    }

    pub fn __repr__(&self) -> String {
        format!("<DynamicScope object at {:p}>", self as *const _)
    }
}
