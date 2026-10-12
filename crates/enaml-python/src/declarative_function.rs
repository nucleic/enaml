// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use crate::funchelper;
use pyo3::class::{PyTraverseError, PyVisit};
use pyo3::exceptions::{PyKeyError, PyTypeError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyFunction, PyMapping, PyTuple, PyType};

/// Declarative function descriptor for Enaml DSL.
///
/// Wraps a function with a scope key for use in declarative blocks.
#[pyclass(module = "enaml._rust")]
pub struct DeclarativeFunction {
    #[pyo3(get)]
    func: Py<PyAny>,
    #[pyo3(get)]
    key: Py<PyAny>,
    type_obj: Py<PyType>,
}

#[pymethods]
impl DeclarativeFunction {
    #[new]
    pub fn new(py: Python<'_>, func: Py<PyAny>, key: Py<PyAny>) -> PyResult<Self> {
        let func_obj = func.bind(py);
        if func_obj.cast::<PyFunction>().is_ok() {
            Ok(DeclarativeFunction {
                func,
                key,
                type_obj: py.get_type::<Self>().unbind(),
            })
        } else {
            Err(pyo3::exceptions::PyTypeError::new_err(
                "DeclarativeFunction requires a function",
            ))
        }
    }

    #[getter]
    pub fn __func__(&self, py: Python<'_>) -> Py<PyAny> {
        self.func.clone_ref(py)
    }

    #[getter]
    pub fn __key__(&self, py: Python<'_>) -> Py<PyAny> {
        self.key.clone_ref(py)
    }

    #[getter]
    pub fn _d_func(&self) -> bool {
        true
    }

    pub fn __get__<'py>(
        slf: PyRef<'py, Self>,
        obj: Option<&Bound<'py, PyAny>>,
        _owner: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let py = slf.py();
        if let Some(obj) = obj {
            // Return a BoundDeclarativeMethod
            Ok(Bound::new(
                py,
                BoundDeclarativeMethod::new(
                    py,
                    slf.func.clone_ref(py),
                    obj.clone().unbind(),
                    slf.key.clone_ref(py),
                )?,
            )?
            .into_any())
        } else {
            // Return the descriptor itself by extracting from the existing PyRef
            Ok(Bound::new(
                py,
                DeclarativeFunction {
                    func: slf.func.clone_ref(py),
                    key: slf.key.clone_ref(py),
                    type_obj: slf.type_obj.clone_ref(py),
                },
            )?
            .into_any())
        }
    }

    pub fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        visit.call(&self.func)?;
        visit.call(&self.key)?;
        visit.call(&self.type_obj)?;
        Ok(())
    }

    #[pyo3(signature = (obj, *args, **kwargs))]
    pub fn __call__<'py>(
        &self,
        py: Python<'py>,
        obj: &Bound<'py, PyAny>,
        args: &Bound<'py, PyTuple>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let func = self.func.bind(py).cast::<PyFunction>()?;
        let scope = build_scope_locals(py, obj, &self.key.bind(py))?;
        let empty_kwargs = PyDict::new(py);
        let kwargs_arg = kwargs.unwrap_or(&empty_kwargs);

        let globals = func.getattr("__globals__")?;
        let globals_dict = globals.cast::<PyDict>()?;
        if globals_dict.get_item("__builtins__")?.is_none() {
            return Err(PyKeyError::new_err("__builtins__"));
        }

        let scope_mapping = scope.cast::<PyMapping>()?;
        let result = funchelper::call_func(py, func, args, kwargs_arg, Some(scope_mapping));
        match result {
            Ok(value) => Ok(value),
            Err(err) => {
                let msg = err.to_string();
                if msg.contains("super()") {
                    Err(PyTypeError::new_err("super()"))
                } else {
                    Err(err)
                }
            }
        }
    }

    pub fn __repr__(&self) -> String {
        format!("<declarative function object at {:p}>", self as *const _)
    }
}

/// Bound declarative method for Enaml DSL.
///
/// Represents a declarative function bound to an instance.
#[pyclass(module = "enaml._rust")]
pub struct BoundDeclarativeMethod {
    #[pyo3(get)]
    func: Py<PyAny>,
    #[pyo3(get)]
    obj: Py<PyAny>,
    #[pyo3(get)]
    key: Py<PyAny>,
    type_obj: Py<PyType>,
}

fn build_scope_locals<'py>(
    py: Python<'py>,
    instance: &Bound<'py, PyAny>,
    scope_key: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyDict>> {
    let storage = instance.getattr("_d_storage")?;
    let locals = PyDict::new(py);
    if let Ok(scope) = storage.get_item(scope_key) {
        if let Ok(scope_dict) = scope.cast::<PyDict>() {
            for (name, value) in scope_dict.iter() {
                locals.set_item(name, value)?;
            }
        }
    }
    locals.set_item("self", instance.clone())?;
    Ok(locals)
}

#[pymethods]
impl BoundDeclarativeMethod {
    #[new]
    pub fn new(py: Python<'_>, func: Py<PyAny>, obj: Py<PyAny>, key: Py<PyAny>) -> PyResult<Self> {
        Ok(BoundDeclarativeMethod {
            func,
            obj,
            key,
            type_obj: py.get_type::<Self>().unbind(),
        })
    }

    #[getter]
    pub fn __func__(&self, py: Python<'_>) -> Py<PyAny> {
        self.func.clone_ref(py)
    }

    #[getter]
    pub fn __self__(&self, py: Python<'_>) -> Py<PyAny> {
        self.obj.clone_ref(py)
    }

    #[getter]
    pub fn __key__(&self, py: Python<'_>) -> Py<PyAny> {
        self.key.clone_ref(py)
    }

    pub fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        visit.call(&self.func)?;
        visit.call(&self.obj)?;
        visit.call(&self.key)?;
        visit.call(&self.type_obj)?;
        Ok(())
    }

    #[pyo3(signature = (*args, **kwargs))]
    pub fn __call__<'py>(
        slf: PyRef<'py, Self>,
        py: Python<'py>,
        args: &Bound<'py, PyTuple>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let self_bound = slf.obj.bind(py);
        let scope = build_scope_locals(py, self_bound, &slf.key.bind(py))?;
        let empty_kwargs = PyDict::new(py);
        let kwargs_arg = kwargs.unwrap_or(&empty_kwargs);

        let func = slf.func.bind(py).cast::<PyFunction>()?;
        let globals = func.getattr("__globals__")?;
        let globals_dict = globals.cast::<PyDict>()?;
        if globals_dict.get_item("__builtins__")?.is_none() {
            return Err(PyKeyError::new_err("__builtins__"));
        }

        let scope_mapping = scope.cast::<PyMapping>()?;
        let result = funchelper::call_func(py, func, args, kwargs_arg, Some(scope_mapping));
        match result {
            Ok(value) => Ok(value),
            Err(err) => {
                let msg = err.to_string();
                if msg.contains("super()") {
                    Err(PyTypeError::new_err("super()"))
                } else {
                    Err(err)
                }
            }
        }
    }

    pub fn __repr__(&self) -> String {
        format!(
            "<bound declarative method object at {:p}>",
            self as *const _
        )
    }

    pub fn __eq__(&self, py: Python<'_>, other: &Bound<'_, PyAny>) -> PyResult<bool> {
        // Check if other is also a BoundDeclarativeMethod
        if let Ok(other_bdm) = other.extract::<PyRef<'_, BoundDeclarativeMethod>>() {
            // Compare func and obj using Python's equality
            let func_eq = self.func.bind(py).eq(other_bdm.func.bind(py))?;
            let obj_eq = self.obj.bind(py).eq(other_bdm.obj.bind(py))?;
            Ok(func_eq && obj_eq)
        } else {
            Ok(false)
        }
    }

    pub fn __hash__(&self, py: Python<'_>) -> PyResult<isize> {
        // Hash based on object identity
        let obj_hash = self.obj.bind(py).hash()?;
        let func_hash = self.func.bind(py).hash()?;
        Ok(obj_hash.wrapping_mul(31).wrapping_add(func_hash))
    }
}
