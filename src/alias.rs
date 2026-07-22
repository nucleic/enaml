// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2026, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::exceptions::{PyAttributeError, PyRuntimeError, PyTypeError};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyBool, PyString, PyTuple};

/// Alias descriptor for aliasing attributes from one object to another.
///
/// # Attributes
/// - target: The target object containing the final attribute
/// - chain: A tuple of attribute names to traverse to reach the final attribute
/// - key: The scope key for looking up in storage
/// - canset: Whether the alias can be set
#[pyclass]
pub struct Alias {
    #[pyo3(get)]
    target: Py<PyString>,

    #[pyo3(get)]
    chain: Py<PyTuple>,

    #[pyo3(get)]
    key: Py<PyAny>,

    canset: bool,
}

#[pymethods]
impl Alias {
    #[new]
    pub fn new(
        target: &Bound<'_, PyString>,
        chain: &Bound<'_, PyTuple>,
        key: &Bound<'_, PyAny>,
    ) -> PyResult<Self> {
        Ok(Alias {
            target: target.clone().unbind(),
            chain: chain.clone().unbind(),
            key: key.clone().unbind(),
            canset: false,
        })
    }

    #[getter]
    pub fn get_canset(&self) -> bool {
        self.canset
    }

    #[setter]
    pub fn set_canset(&mut self, value: &Bound<'_, PyAny>) -> PyResult<()> {
        if !value.is_instance_of::<PyBool>() {
            return Err(PyTypeError::new_err("canset must be a bool"));
        }
        self.canset = value.extract::<bool>()?;
        Ok(())
    }

    fn resolve_target<'py>(
        &self,
        py: Python<'py>,
        obj: &Bound<'py, PyAny>,
    ) -> PyResult<(Bound<'py, PyAny>, Option<Bound<'py, PyString>>)> {
        let storage = obj.getattr("_d_storage")?;
        let scope = storage.call_method1("get", (self.key.bind(py), py.None()))?;
        if scope.is_none() {
            return Err(PyRuntimeError::new_err("failed to load alias"));
        }

        let mut target_obj = scope.call_method1("get", (self.target.bind(py), py.None()))?;
        if target_obj.is_none() {
            return Err(PyRuntimeError::new_err("failed to load alias"));
        }

        let chain = self.chain.bind(py);
        if chain.len() == 0 {
            return Ok((target_obj, None));
        }

        for index in 0..chain.len() {
            let attr_name = chain.get_item(index)?.cast::<PyString>()?.clone();
            if index == chain.len() - 1 {
                return Ok((target_obj, Some(attr_name)));
            }

            match target_obj.getattr(attr_name) {
                Ok(value) => target_obj = value,
                Err(err) if err.is_instance_of::<PyAttributeError>(py) => {
                    return Err(err);
                }
                Err(err) => return Err(err),
            }
        }

        Ok((target_obj, None))
    }

    fn resolve_value<'py>(
        &self,
        py: Python<'py>,
        obj: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let (target, attr_name) = self.resolve_target(py, obj)?;
        if let Some(attr_name) = attr_name {
            let value = target.getattr(attr_name)?;
            Ok(value)
        } else {
            Ok(target)
        }
    }

    /// Descriptor get method
    pub fn __get__<'py>(
        slf: PyRef<'py, Self>,
        instance: Option<Py<PyAny>>,
        _owner: Option<Py<PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let py = slf.py();
        if instance.is_none() {
            return Ok(slf.into_pyobject(py)?.into_any());
        }

        let binding = instance.unwrap();
        let obj = binding.bind(py);
        match (*slf).resolve_value(py, obj) {
            Ok(value) => Ok(value),
            Err(err) if err.is_instance_of::<PyAttributeError>(py) => Err(err),
            Err(err) if err.is_instance_of::<PyRuntimeError>(py) => {
                Err(PyRuntimeError::new_err("failed to load alias"))
            }
            Err(err) => Err(err),
        }
    }

    pub fn __set__(
        &self,
        py: Python<'_>,
        obj: &Bound<'_, PyAny>,
        value: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        if !self.canset {
            return Err(PyAttributeError::new_err("can't set attribute"));
        }

        let (target, attr_name) = self.resolve_target(py, obj)?;
        if let Some(attr_name) = attr_name {
            target.setattr(attr_name, value)?;
            Ok(())
        } else {
            Err(PyAttributeError::new_err("can't set attribute"))
        }
    }

    /// Get target object and attribute name
    pub fn resolve<'py>(
        &self,
        py: Python<'py>,
        obj: Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let (target, attr_name) = self.resolve_target(py, &obj)?;
        let tuple_value = match attr_name {
            Some(attr_name) if self.canset => PyTuple::new(py, [target, attr_name.into_any()])?,
            Some(attr_name) => match target.getattr(attr_name) {
                Ok(value) => PyTuple::new(py, [value, py.None().into_pyobject(py)?.into_any()])?,
                Err(err) if err.is_instance_of::<PyAttributeError>(py) => return Err(err),
                Err(err) => return Err(err),
            },
            None => PyTuple::new(py, [target, py.None().into_pyobject(py)?.into_any()])?,
        };

        Ok(tuple_value.into_any())
    }
}
