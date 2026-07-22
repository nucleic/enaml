// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::class::{PyTraverseError, PyVisit};
use pyo3::exceptions::{PyAttributeError, PyKeyError, PyTypeError, PyValueError};
use pyo3::types::{PyAny, PyDict, PyList, PyMapping, PyMappingMethods, PyString, PyTuple};
use pyo3::{intern, prelude::*};

/// User key error exception for missing scope keys.
#[pyclass(extends = PyKeyError)]
pub struct UserKeyError;

#[pymethods]
impl UserKeyError {
    #[new]
    #[pyo3(signature = (_message=None))]
    fn new(_message: Option<String>) -> Self {
        Self
    }
}

fn resolve_owner_attribute<'py>(
    py: Python<'_>,
    owner: &Bound<'py, PyAny>,
    name: &Bound<'py, PyString>,
) -> PyResult<Py<PyAny>> {
    match owner.getattr(name) {
        Ok(value) => Ok(value.unbind()),
        Err(err) => {
            if err.is_instance_of::<PyAttributeError>(py) {
                let parent = owner.getattr("_parent")?;
                if parent.is_none() {
                    Err(PyAttributeError::new_err(format!(
                        "attribute '{}' not found",
                        name
                    )))
                } else {
                    resolve_owner_attribute(py, &parent, name)
                }
            } else if err.is_instance_of::<PyKeyError>(py) {
                Err(PyErr::new::<UserKeyError, _>(name.to_string()))
            } else {
                Err(err)
            }
        }
    }
}

fn locate_owner_for_assignment(
    py: Python<'_>,
    owner: &Bound<'_, PyAny>,
    name: &Bound<'_, PyString>,
) -> PyResult<Py<PyAny>> {
    let mut current = Some(owner.clone().unbind());
    while let Some(obj) = current {
        let obj_bound = obj.bind(py);
        if obj_bound.getattr(name).is_ok() {
            return Ok(obj);
        }

        current = match obj_bound.getattr(intern!(py, "_parent")) {
            Ok(parent) if !parent.is_none() => Some(parent.unbind()),
            _ => None,
        };
    }

    Ok(owner.clone().unbind())
}

/// Wrapper for accessing owner attributes through the nonlocals mechanism.
#[pyclass]
pub struct Nonlocals {
    owner_obj: Py<PyAny>,
    tracer_obj: Py<PyAny>,
}

#[pymethods]
impl Nonlocals {
    #[new]
    #[pyo3(signature = (owner, tracer=None))]
    pub fn new(py: Python<'_>, owner: Py<PyAny>, tracer: Option<Py<PyAny>>) -> Self {
        Nonlocals {
            owner_obj: owner,
            tracer_obj: tracer.unwrap_or_else(|| py.None().into()),
        }
    }

    pub fn __contains__(&self, py: Python<'_>, key: &Bound<'_, PyString>) -> PyResult<bool> {
        let owner = self.owner_obj.bind(py);
        match resolve_owner_attribute(py, &owner, key) {
            Ok(_) => Ok(true),
            Err(err) => {
                if err.is_instance_of::<PyAttributeError>(py) {
                    Ok(false)
                } else if err.is_instance_of::<PyKeyError>(py) {
                    Ok(true)
                } else {
                    Err(err)
                }
            }
        }
    }

    pub fn __getattr__<'py>(
        &self,
        py: Python<'py>,
        name: &Bound<'py, PyString>,
    ) -> PyResult<Py<PyAny>> {
        let owner = self.owner_obj.bind(py);
        match resolve_owner_attribute(py, &owner, name) {
            Ok(value) => {
                let value_py: Py<PyAny> = value.into();
                let tracer = self.tracer_obj.bind(py);
                if !tracer.is_none() && tracer.hasattr(intern!(py, "dynamic_load"))? {
                    let _ = tracer.call_method1(
                        "dynamic_load",
                        (
                            self.owner_obj.clone_ref(py),
                            name.clone(),
                            value_py.clone_ref(py),
                        ),
                    );
                }
                Ok(value_py)
            }
            Err(err) => {
                if err.is_instance_of::<PyAttributeError>(py) {
                    Err(PyAttributeError::new_err(format!(
                        "'Nonlocals' object has no attribute '{}'",
                        name
                    )))
                } else {
                    Err(err)
                }
            }
        }
    }

    pub fn __getitem__<'py>(
        &self,
        py: Python<'py>,
        key: &Bound<'py, PyString>,
    ) -> PyResult<Py<PyAny>> {
        let owner = self.owner_obj.bind(py);
        match resolve_owner_attribute(py, &owner, key) {
            Ok(value) => {
                let value_py: Py<PyAny> = value.into();
                let tracer = self.tracer_obj.bind(py);
                if !tracer.is_none() && tracer.hasattr(intern!(py, "dynamic_load"))? {
                    let _ = tracer.call_method1(
                        "dynamic_load",
                        (
                            self.owner_obj.clone_ref(py),
                            key.clone(),
                            value_py.clone_ref(py),
                        ),
                    );
                }
                Ok(value_py)
            }
            Err(err) => {
                if err.is_instance_of::<PyAttributeError>(py) {
                    Err(PyKeyError::new_err(key.to_string()))
                } else {
                    Err(err)
                }
            }
        }
    }

    pub fn __setitem__<'py>(
        &self,
        py: Python<'py>,
        key: &Bound<'py, PyString>,
        value: &Bound<'py, PyAny>,
    ) -> PyResult<()> {
        let owner = locate_owner_for_assignment(py, &self.owner_obj.bind(py), key)?;
        owner.bind(py).setattr(key, value)?;
        Ok(())
    }

    pub fn __delitem__<'py>(&self, py: Python<'py>, key: &Bound<'py, PyString>) -> PyResult<()> {
        let owner = locate_owner_for_assignment(py, &self.owner_obj.bind(py), key)?;
        owner.bind(py).delattr(key)?;
        Ok(())
    }

    pub fn __setattr__<'py>(
        &self,
        py: Python<'py>,
        name: &Bound<'py, PyString>,
        value: &Bound<'py, PyAny>,
    ) -> PyResult<()> {
        let owner = locate_owner_for_assignment(py, &self.owner_obj.bind(py), name)?;
        owner.bind(py).setattr(name, value)?;
        Ok(())
    }

    pub fn __delattr__<'py>(&self, py: Python<'py>, name: &Bound<'py, PyString>) -> PyResult<()> {
        let owner = locate_owner_for_assignment(py, &self.owner_obj.bind(py), name)?;
        owner.bind(py).delattr(name)?;
        Ok(())
    }

    pub fn __call__(&self, py: Python<'_>, level: Option<usize>) -> PyResult<Py<PyAny>> {
        let level = level.unwrap_or(1);
        if level != 1 {
            return Err(PyValueError::new_err("level must be 1"));
        }

        let owner = self.owner_obj.clone_ref(py);
        let parent = owner.bind(py).getattr("_parent")?;
        let parent = if parent.is_none() {
            py.None().into()
        } else {
            parent.unbind().into()
        };
        Ok(Py::new(
            py,
            Nonlocals::new(py, parent, Some(self.tracer_obj.clone_ref(py))),
        )?
        .into())
    }

    pub fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        visit.call(&self.owner_obj)?;
        visit.call(&self.tracer_obj)?;
        Ok(())
    }

    fn __clear__(slf: &Bound<'_, Self>) {
        let py = slf.py();
        let mut borrow = slf.borrow_mut();
        borrow.owner_obj = py.None().into();
        borrow.tracer_obj = py.None().into();
    }

    pub fn __repr__(&self) -> String {
        format!("Nonlocals[{:p}]", self as *const _)
    }

    pub fn __eq__(&self, py: Python<'_>, other: &Bound<'_, PyAny>) -> PyResult<bool> {
        if let Ok(other_nonlocals) = other.extract::<PyRef<'_, Nonlocals>>() {
            let self_owner_ptr = self.owner_obj.bind(py).as_ptr();
            let other_owner_ptr = other_nonlocals.owner_obj.bind(py).as_ptr();
            let self_tracer_ptr = self.tracer_obj.bind(py).as_ptr();
            let other_tracer_ptr = other_nonlocals.tracer_obj.bind(py).as_ptr();
            Ok(self_owner_ptr == other_owner_ptr && self_tracer_ptr == other_tracer_ptr)
        } else {
            Ok(false)
        }
    }
}

fn collect_scope_keys(py: Python<'_>, scope: &DynamicScope) -> PyResult<Vec<String>> {
    let mut keys = Vec::new();
    let mut seen = std::collections::HashSet::new();

    let push_key =
        |keys: &mut Vec<String>, seen: &mut std::collections::HashSet<String>, key: String| {
            if key.starts_with('_') || seen.contains(&key) {
                return;
            }
            seen.insert(key.clone());
            keys.push(key);
        };

    unsafe {
        if let Some(writes) = &*scope.f_writes.get() {
            let writes_dict = writes.bind(py);
            for key_result in writes_dict.keys() {
                if let Ok(k) = key_result.extract::<&str>() {
                    push_key(&mut keys, &mut seen, k.to_string());
                }
            }
        }
    }

    for special in ["self", "change", "__scope__", "_[tracer]", "nonlocals"] {
        push_key(&mut keys, &mut seen, special.to_string());
    }

    for mapping in [&scope.f_locals, &scope.f_globals, &scope.f_builtins] {
        let mapping_obj = mapping.bind(py);
        if let Ok(mapping) = mapping_obj.cast::<PyMapping>() {
            if let Ok(keys_obj) = mapping.keys() {
                if let Ok(items) = keys_obj.try_iter() {
                    for key_result in items {
                        if let Ok(k) = key_result.and_then(|item| item.extract::<String>()) {
                            push_key(&mut keys, &mut seen, k);
                        }
                    }
                }
            }
        } else if let Ok(keys_obj) = mapping_obj.call_method0("keys") {
            if let Ok(items) = keys_obj.try_iter() {
                for key_result in items {
                    if let Ok(k) = key_result.and_then(|item| item.extract::<String>()) {
                        push_key(&mut keys, &mut seen, k);
                    }
                }
            }
        }
    }

    let mut current = Some(scope.owner.clone_ref(py));
    while let Some(obj) = current {
        let obj_bound = obj.bind(py);
        if let Ok(dir_result_obj) = obj_bound.call_method0("__dir__") {
            if let Ok(dir_list) = dir_result_obj.extract::<Bound<'_, pyo3::types::PyList>>() {
                for i in 0..dir_list.len() {
                    if let Ok(attr_item) = dir_list.get_item(i) {
                        if let Ok(a) = attr_item.extract::<&str>() {
                            push_key(&mut keys, &mut seen, a.to_string());
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

    Ok(keys)
}

/// Dynamic scope for Enaml expressions.
///
/// Implements dynamic scoping with owner hierarchy traversal and change tracking.
#[pyclass(mapping)]
pub struct DynamicScope {
    owner: Py<PyAny>,
    f_locals: Py<PyMapping>,
    f_globals: Py<PyMapping>,
    f_builtins: Py<PyMapping>,
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
    #[pyo3(signature = (owner, f_locals, f_globals, f_builtins, change=None, tracer=None))]
    pub fn new(
        py: Python<'_>,
        owner: Py<PyAny>,
        f_locals: Py<PyMapping>,
        f_globals: Py<PyMapping>,
        f_builtins: Py<PyMapping>,
        change: Option<Py<PyAny>>,
        tracer: Option<Py<PyAny>>,
    ) -> PyResult<Self> {
        let change = change.unwrap_or_else(|| py.None().into());
        let tracer = tracer.unwrap_or_else(|| py.None().into());

        Ok(DynamicScope {
            owner,
            f_locals,
            f_globals,
            f_builtins,
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
                let cloned_scope = DynamicScope {
                    owner: self.owner.clone_ref(py),
                    f_locals: self.f_locals.clone_ref(py),
                    f_globals: self.f_globals.clone_ref(py),
                    f_builtins: self.f_builtins.clone_ref(py),
                    change: self.change.clone_ref(py),
                    tracer: self.tracer.clone_ref(py),
                    f_writes: std::cell::UnsafeCell::new(None),
                };
                return Py::new(py, cloned_scope).map(|p| p.into());
            }
            "_[tracer]" => return Ok(self.tracer.clone_ref(py)),
            "nonlocals" => {
                return Py::new(
                    py,
                    Nonlocals::new(
                        py,
                        self.owner.clone_ref(py),
                        Some(self.tracer.clone_ref(py)),
                    ),
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
            let val = self.f_locals.bind(py).get_item(key)?;
            return Ok(val.unbind());
        }

        // 4. Check f_globals
        if self.f_globals.bind(py).contains(key)? {
            let val = self.f_globals.bind(py).get_item(key)?;
            return Ok(val.unbind());
        }

        // 5. Check f_builtins
        if self.f_builtins.bind(py).contains(key)? {
            let val = self.f_builtins.bind(py).get_item(key)?;
            return Ok(val.unbind());
        }

        // 6. Check owner hierarchy
        let mut current = Some(self.owner.clone_ref(py));
        while let Some(obj) = current {
            let obj_bound = obj.bind(py);
            match resolve_owner_attribute(py, &obj_bound, &PyString::new(py, key_str)) {
                Ok(value) => return Ok(value),
                Err(err) => {
                    if err.is_instance_of::<PyAttributeError>(py) {
                        current = if let Ok(parent) = obj_bound.getattr("_parent") {
                            if !parent.is_none() {
                                Some(parent.into())
                            } else {
                                None
                            }
                        } else {
                            None
                        };
                    } else {
                        return Err(err);
                    }
                }
            }
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

    pub fn __len__(&self, py: Python<'_>) -> PyResult<usize> {
        let keys = collect_scope_keys(py, self)?;
        Ok(keys.len())
    }

    pub fn __contains__(&self, py: Python<'_>, key: &Bound<'_, PyString>) -> PyResult<bool> {
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
            if obj_bound.hasattr(key)? {
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

    #[pyo3(signature = (key, default=None))]
    pub fn get(
        &self,
        py: Python<'_>,
        key: &Bound<'_, PyString>,
        default: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        match self.__getitem__(py, key) {
            Ok(val) => Ok(val),
            Err(err) => {
                if err.is_instance_of::<PyKeyError>(py) {
                    if let Some(default) = default {
                        Ok(default.clone().unbind())
                    } else {
                        Ok(py.None())
                    }
                } else {
                    Err(err)
                }
            }
        }
    }

    pub fn __iter__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let key_list = collect_scope_keys(py, self)?;
        let key_list_obj = PyList::new(py, key_list)?;
        key_list_obj
            .call_method0("__iter__")
            .map(|obj| obj.unbind())
    }

    pub fn keys(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let key_list = collect_scope_keys(py, self)?;
        Ok(PyList::new(py, key_list)?.into_any().unbind())
    }

    pub fn values(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let keys = collect_scope_keys(py, self)?;
        let mut values = Vec::new();

        for key in keys {
            let key_obj = PyString::new(py, &key);
            let key_any = key_obj.clone().into_any();
            if let Ok(value) = self.__getitem__(py, &key_any) {
                values.push(value);
            }
        }

        Ok(pyo3::types::PyList::new(py, values)?.into_any().unbind())
    }

    pub fn items(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let keys = collect_scope_keys(py, self)?;
        let mut items = Vec::new();

        for key in keys {
            let key_obj = PyString::new(py, &key);
            let key_any = key_obj.clone().into_any();
            if let Ok(value) = self.__getitem__(py, &key_any) {
                items.push((key_obj.unbind(), value));
            }
        }

        Ok(pyo3::types::PyList::new(py, items)?.into_any().unbind())
    }

    pub fn update(&self, py: Python<'_>, other: &Bound<'_, PyAny>) -> PyResult<()> {
        if !other.hasattr("items")? {
            return Err(PyAttributeError::new_err("expected mapping"));
        }

        unsafe {
            if (*self.f_writes.get()).is_none() {
                *self.f_writes.get() = Some(PyDict::new(py).into());
            }

            let items_obj = other.call_method0("items")?;
            let items_iter = items_obj.try_iter()?;
            for item_result in items_iter {
                let item = item_result?;
                let tuple: Bound<'_, PyTuple> = match item.extract() {
                    Ok(t) => t,
                    Err(_) => continue,
                };
                if tuple.len() != 2 {
                    continue;
                }
                if let (Ok(k), Ok(v)) = (tuple.get_item(0), tuple.get_item(1)) {
                    if !k.is_instance_of::<PyString>() {
                        return Err(PyTypeError::new_err("keys must be strings"));
                    }
                    if let Some(writes) = &*self.f_writes.get() {
                        writes.bind(py).set_item(&k, &v)?;
                    }
                }
            }
        }

        Ok(())
    }

    pub fn __eq__(&self, py: Python<'_>, other: &Bound<'_, PyAny>) -> PyResult<bool> {
        if let Ok(other_scope) = other.extract::<PyRef<'_, DynamicScope>>() {
            Ok(
                self.owner.bind(py).as_ptr() == other_scope.owner.bind(py).as_ptr()
                    && self.change.bind(py).as_ptr() == other_scope.change.bind(py).as_ptr()
                    && self.tracer.bind(py).as_ptr() == other_scope.tracer.bind(py).as_ptr()
                    && self.f_locals.bind(py).as_ptr() == other_scope.f_locals.bind(py).as_ptr()
                    && self.f_globals.bind(py).as_ptr() == other_scope.f_globals.bind(py).as_ptr()
                    && self.f_builtins.bind(py).as_ptr()
                        == other_scope.f_builtins.bind(py).as_ptr(),
            )
        } else {
            Ok(false)
        }
    }

    pub fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        visit.call(&self.owner)?;
        visit.call(&self.f_locals)?;
        visit.call(&self.f_globals)?;
        visit.call(&self.f_builtins)?;
        visit.call(&self.change)?;
        visit.call(&self.tracer)?;
        unsafe {
            if let Some(writes) = &*self.f_writes.get() {
                visit.call(writes)?;
            }
        }
        Ok(())
    }

    fn __clear__(slf: &Bound<'_, Self>) {
        let py = slf.py();
        let mut borrow = slf.borrow_mut();
        borrow.owner = py.None().into();
        borrow.f_locals = PyDict::new(py)
            .into_pyobject(py)
            .unwrap()
            .cast_into::<PyMapping>()
            .unwrap()
            .unbind();
        borrow.f_globals = PyDict::new(py)
            .into_pyobject(py)
            .unwrap()
            .cast_into::<PyMapping>()
            .unwrap()
            .unbind();
        borrow.f_builtins = PyDict::new(py)
            .into_pyobject(py)
            .unwrap()
            .cast_into::<PyMapping>()
            .unwrap()
            .unbind();
        borrow.change = py.None().into();
        borrow.tracer = py.None().into();
        borrow.f_writes = std::cell::UnsafeCell::new(None);
    }

    pub fn __repr__(&self) -> String {
        format!("<DynamicScope object at {:p}>", self as *const _)
    }
}
