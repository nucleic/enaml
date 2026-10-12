// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2026, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::class::{PyTraverseError, PyVisit};
use pyo3::exceptions::{PyAttributeError, PyKeyError, PyTypeError, PyValueError};
use pyo3::sync::critical_section::with_critical_section;
use pyo3::types::{PyAny, PyDict, PyList, PyMapping, PyMappingMethods, PyString, PyTuple};
use pyo3::{intern, prelude::*};

/// User key error exception for missing scope keys.
#[pyclass(immutable_type, extends = PyKeyError, module = "enaml._rust")]
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
) -> PyResult<Bound<'py, PyAny>> {
    match owner.getattr(name) {
        Ok(value) => Ok(value),
        Err(err) => {
            if err.is_instance_of::<PyAttributeError>(py) {
                let parent = owner.getattr("_parent")?;
                if parent.is_none() {
                    Err(PyAttributeError::new_err(format!(
                        "attribute '{}' not found",
                        name.to_string()
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

fn locate_owner_for_assignment<'py>(
    py: Python<'py>,
    owner: &Bound<'py, PyAny>,
    name: &Bound<'py, PyString>,
) -> PyResult<Bound<'py, PyAny>> {
    let mut current = Some(owner.clone());
    while let Some(obj) = current {
        if let Ok(_) = obj.getattr(name) {
            return Ok(obj);
        }

        current = match obj.getattr(intern!(py, "_parent")) {
            Ok(parent) if !parent.is_none() => Some(parent),
            _ => None,
        };
    }

    Ok(owner.clone())
}

/// Wrapper for accessing owner attributes through the nonlocals mechanism.
#[pyclass(immutable_type, module = "enaml._rust")]
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
    ) -> PyResult<Bound<'py, PyAny>> {
        let owner = self.owner_obj.bind(py);
        match resolve_owner_attribute(py, &owner, name) {
            Ok(value) => {
                let tracer = self.tracer_obj.bind(py);
                if !tracer.is_none() && tracer.hasattr(intern!(py, "dynamic_load"))? {
                    let _ = tracer.call_method1(
                        "dynamic_load",
                        (self.owner_obj.clone_ref(py), name.clone(), value.clone()),
                    );
                }
                Ok(value)
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
    ) -> PyResult<Bound<'py, PyAny>> {
        let owner = self.owner_obj.bind(py);
        match resolve_owner_attribute(py, &owner, key) {
            Ok(value) => {
                let tracer = self.tracer_obj.bind(py);
                if !tracer.is_none() && tracer.hasattr(intern!(py, "dynamic_load"))? {
                    let _ = tracer.call_method1(
                        "dynamic_load",
                        (self.owner_obj.clone_ref(py), key.clone(), value.clone()),
                    );
                }
                Ok(value)
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
        owner.setattr(key, value)?;
        Ok(())
    }

    pub fn __delitem__<'py>(&self, py: Python<'py>, key: &Bound<'py, PyString>) -> PyResult<()> {
        let owner = locate_owner_for_assignment(py, &self.owner_obj.bind(py), key)?;
        owner.delattr(key)?;
        Ok(())
    }

    pub fn __setattr__<'py>(
        &self,
        py: Python<'py>,
        name: &Bound<'py, PyString>,
        value: &Bound<'py, PyAny>,
    ) -> PyResult<()> {
        let owner = locate_owner_for_assignment(py, &self.owner_obj.bind(py), name)?;
        owner.setattr(name, value)?;
        Ok(())
    }

    pub fn __delattr__<'py>(&self, py: Python<'py>, name: &Bound<'py, PyString>) -> PyResult<()> {
        let owner = locate_owner_for_assignment(py, &self.owner_obj.bind(py), name)?;
        owner.delattr(name)?;
        Ok(())
    }

    pub fn __call__<'py>(
        &self,
        py: Python<'py>,
        level: Option<usize>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let level = level.unwrap_or(1);
        if level != 1 {
            return Err(PyValueError::new_err("level must be 1"));
        }

        let owner = self.owner_obj.clone_ref(py);
        let parent = owner.bind(py).getattr("_parent")?;
        let parent = if parent.is_none() {
            py.None()
        } else {
            parent.unbind()
        };
        let nonlocals = Bound::new(
            py,
            Nonlocals::new(py, parent, Some(self.tracer_obj.clone_ref(py))),
        )?;
        Ok(nonlocals.into_any())
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

fn collect_scope_keys(py: Python<'_>, scope: &Bound<'_, DynamicScope>) -> PyResult<Vec<String>> {
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

    let writes_keys = with_critical_section(scope, || {
        let scope_borrow = scope.borrow();
        let mut cached_keys = Vec::new();
        unsafe {
            if let Some(writes) = &*scope_borrow.f_writes.get() {
                let writes_dict = writes.bind(py);
                for key_result in writes_dict.keys() {
                    if let Ok(k) = key_result.extract::<&str>() {
                        cached_keys.push(k.to_string());
                    }
                }
            }
        }
        Ok::<Vec<String>, PyErr>(cached_keys)
    })?;

    for key in writes_keys {
        push_key(&mut keys, &mut seen, key);
    }

    for special in ["self", "change", "__scope__", "_[tracer]", "nonlocals"] {
        push_key(&mut keys, &mut seen, special.to_string());
    }

    let scope_borrow = scope.borrow();
    for mapping in [
        &scope_borrow.f_locals,
        &scope_borrow.f_globals,
        &scope_borrow.f_builtins,
    ] {
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

    let mut current = Some(scope_borrow.owner.clone_ref(py));
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
#[pyclass(immutable_type, mapping, module = "enaml._rust")]
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
        owner: &Bound<'_, PyAny>,
        f_locals: &Bound<'_, PyMapping>,
        f_globals: &Bound<'_, PyMapping>,
        f_builtins: &Bound<'_, PyMapping>,
        change: Option<&Bound<'_, PyAny>>,
        tracer: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
        let change = if let Some(c) = change {
            c.clone()
        } else {
            py.None().into_bound(py)
        };
        let tracer = if let Some(t) = tracer {
            t.clone()
        } else {
            py.None().into_bound(py)
        };

        Ok(DynamicScope {
            owner: owner.clone().unbind(),
            f_locals: f_locals.clone().unbind(),
            f_globals: f_globals.clone().unbind(),
            f_builtins: f_builtins.clone().unbind(),
            change: change.clone().unbind(),
            tracer: tracer.clone().unbind(),
            f_writes: std::cell::UnsafeCell::new(None),
        })
    }

    pub fn __getitem__<'py>(
        slf: &Bound<'py, Self>,
        py: Python<'py>,
        key: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        // Validate key is a string
        if !key.is_instance_of::<PyString>() {
            return Err(PyTypeError::new_err("expected string key"));
        }

        let key_str = key.extract::<&str>()?;

        let scope_borrow = slf.borrow();

        // 1. Check special keys
        match key_str {
            "self" => return Ok(scope_borrow.owner.bind(py).clone()),
            "change" => return Ok(scope_borrow.change.bind(py).clone()),
            "__scope__" => {
                let cloned_scope = DynamicScope {
                    owner: scope_borrow.owner.clone_ref(py),
                    f_locals: scope_borrow.f_locals.clone_ref(py),
                    f_globals: scope_borrow.f_globals.clone_ref(py),
                    f_builtins: scope_borrow.f_builtins.clone_ref(py),
                    change: scope_borrow.change.clone_ref(py),
                    tracer: scope_borrow.tracer.clone_ref(py),
                    f_writes: std::cell::UnsafeCell::new(None),
                };
                return Bound::new(py, cloned_scope).map(|p| p.into_any());
            }
            "_[tracer]" => return Ok(scope_borrow.tracer.bind(py).clone()),
            "nonlocals" => {
                return Bound::new(
                    py,
                    Nonlocals::new(
                        py,
                        scope_borrow.owner.clone_ref(py),
                        Some(scope_borrow.tracer.clone_ref(py)),
                    ),
                )
                .map(|p| p.into_any());
            }
            _ => {}
        }

        // 2. Check f_writes
        if let Some(val) = with_critical_section(slf, || -> PyResult<Option<Bound<'_, PyAny>>> {
            let scope_borrow = slf.borrow();
            unsafe {
                if let Some(writes) = &*scope_borrow.f_writes.get() {
                    if writes.bind(py).contains(key)? {
                        if let Some(val) = writes.bind(py).get_item(key)? {
                            return Ok(Some(val));
                        }
                    }
                }
            }
            Ok(None)
        })? {
            return Ok(val);
        }

        let scope_borrow = slf.borrow();

        // 3. Check f_locals
        if scope_borrow.f_locals.bind(py).contains(key)? {
            let val = scope_borrow.f_locals.bind(py).get_item(key)?;
            return Ok(val);
        }

        // 4. Check f_globals
        if scope_borrow.f_globals.bind(py).contains(key)? {
            let val = scope_borrow.f_globals.bind(py).get_item(key)?;
            return Ok(val);
        }

        // 5. Check f_builtins
        if scope_borrow.f_builtins.bind(py).contains(key)? {
            let val = scope_borrow.f_builtins.bind(py).get_item(key)?;
            return Ok(val);
        }

        // 6. Check owner hierarchy
        let mut current = Some(scope_borrow.owner.clone_ref(py));
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
        slf: &Bound<'_, Self>,
        py: Python<'_>,
        key: &Bound<'_, PyAny>,
        value: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        // Validate key is a string
        if !key.is_instance_of::<PyString>() {
            return Err(PyTypeError::new_err("expected string key"));
        }

        with_critical_section(slf, || {
            let scope_borrow = slf.borrow_mut();
            unsafe {
                // Create f_writes if needed
                if (*scope_borrow.f_writes.get()).is_none() {
                    *scope_borrow.f_writes.get() = Some(PyDict::new(py).into());
                }

                // Set in f_writes
                if let Some(writes) = &*scope_borrow.f_writes.get() {
                    writes.bind(py).set_item(key, value)?;
                }
            }

            Ok(())
        })
    }

    pub fn __delitem__(
        slf: &Bound<'_, Self>,
        py: Python<'_>,
        key: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        // Validate key is a string
        if !key.is_instance_of::<PyString>() {
            return Err(PyTypeError::new_err("expected string key"));
        }

        with_critical_section(slf, || {
            let scope_borrow = slf.borrow();
            unsafe {
                // Delete from f_writes only
                if let Some(writes) = &*scope_borrow.f_writes.get() {
                    writes.bind(py).del_item(key)?;
                } else {
                    let key_str = key.extract::<&str>().unwrap_or("<unknown>");
                    return Err(PyKeyError::new_err(key_str.to_string()));
                }
            }

            Ok(())
        })
    }

    pub fn __len__(slf: &Bound<'_, Self>, py: Python<'_>) -> PyResult<usize> {
        let keys = collect_scope_keys(py, slf)?;
        Ok(keys.len())
    }

    pub fn __contains__(
        slf: &Bound<'_, Self>,
        py: Python<'_>,
        key: &Bound<'_, PyString>,
    ) -> PyResult<bool> {
        let key_str = key.extract::<&str>()?;

        // Check special keys
        if matches!(
            key_str,
            "self" | "change" | "__scope__" | "_[tracer]" | "nonlocals"
        ) {
            return Ok(true);
        }

        if with_critical_section(slf, || -> PyResult<bool> {
            let scope_borrow = slf.borrow();
            // Check f_writes
            unsafe {
                if let Some(writes) = &*scope_borrow.f_writes.get() {
                    if writes.bind(py).contains(key)? {
                        return Ok(true);
                    }
                }
            }
            Ok(false)
        })? {
            return Ok(true);
        }

        let scope_borrow = slf.borrow();
        // Check f_locals, f_globals, f_builtins
        if scope_borrow.f_locals.bind(py).contains(key)?
            || scope_borrow.f_globals.bind(py).contains(key)?
            || scope_borrow.f_builtins.bind(py).contains(key)?
        {
            return Ok(true);
        }

        // Check owner hierarchy
        let mut current = Some(scope_borrow.owner.clone_ref(py));
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
    pub fn get<'py>(
        slf: &Bound<'py, Self>,
        py: Python<'py>,
        key: &Bound<'py, PyString>,
        default: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        match DynamicScope::__getitem__(slf, py, key) {
            Ok(val) => Ok(val),
            Err(err) => {
                if err.is_instance_of::<PyKeyError>(py) {
                    if let Some(default) = default {
                        Ok(default.clone())
                    } else {
                        Ok(py.None().into_bound(py))
                    }
                } else {
                    Err(err)
                }
            }
        }
    }

    pub fn __iter__<'py>(slf: &Bound<'py, Self>, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let key_list = collect_scope_keys(py, slf)?;
        let key_list_obj = PyList::new(py, key_list)?;
        key_list_obj
            .call_method0("__iter__")
            .map(|iter| iter.into_any())
    }

    pub fn keys<'py>(slf: &Bound<'py, Self>, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let key_list = collect_scope_keys(py, slf)?;
        Ok(PyList::new(py, key_list)?.into_any())
    }

    pub fn values<'py>(slf: &Bound<'py, Self>, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let keys = collect_scope_keys(py, slf)?;
        let mut values = Vec::new();

        for key in keys {
            let key_obj = PyString::new(py, &key);
            let key_any = key_obj.clone().into_any();
            if let Ok(value) = DynamicScope::__getitem__(slf, py, &key_any) {
                values.push(value);
            }
        }

        Ok(pyo3::types::PyList::new(py, values)?.into_any())
    }

    pub fn items<'py>(slf: &Bound<'py, Self>, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let keys = collect_scope_keys(py, slf)?;
        let mut items = Vec::new();

        for key in keys {
            let key_obj = PyString::new(py, &key);
            let key_any = key_obj.clone().into_any();
            if let Ok(value) = DynamicScope::__getitem__(slf, py, &key_any) {
                items.push((key_obj.unbind(), value));
            }
        }

        Ok(pyo3::types::PyList::new(py, items)?.into_any())
    }

    pub fn update(
        slf: &Bound<'_, Self>,
        py: Python<'_>,
        other: &Bound<'_, PyMapping>,
    ) -> PyResult<()> {
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
                with_critical_section(slf, || -> PyResult<()> {
                    let scope_borrow = slf.borrow_mut();
                    unsafe {
                        if (*scope_borrow.f_writes.get()).is_none() {
                            *scope_borrow.f_writes.get() = Some(PyDict::new(py).into());
                        }
                        if let Some(writes) = &*scope_borrow.f_writes.get() {
                            writes.bind(py).set_item(&k, &v)?;
                        }
                    }
                    Ok(())
                })?;
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
        borrow.owner = py.None();
        unsafe {
            borrow.f_locals = PyDict::new(py).cast_into_unchecked::<PyMapping>().unbind();
            borrow.f_globals = PyDict::new(py).cast_into_unchecked::<PyMapping>().unbind();
            borrow.f_builtins = PyDict::new(py).cast_into_unchecked::<PyMapping>().unbind();
        }
        borrow.change = py.None();
        borrow.tracer = py.None();
        borrow.f_writes = std::cell::UnsafeCell::new(None);
    }

    pub fn __repr__(&self) -> String {
        format!("<DynamicScope object at {:p}>", self as *const _)
    }
}
