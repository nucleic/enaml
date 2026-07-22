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
    target: String,

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
        target: &Bound<'_, PyAny>,
        chain: &Bound<'_, PyAny>,
        key: &Bound<'_, PyAny>,
    ) -> PyResult<Self> {
        let target = target.extract::<String>()?;
        let chain = chain.extract::<Py<PyTuple>>()?;
        let key = key.clone().unbind();
        Ok(Alias {
            target,
            chain,
            key,
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

    fn resolve_target(
        &self,
        py: Python<'_>,
        obj: &Bound<'_, PyAny>,
    ) -> PyResult<(Py<PyAny>, Option<String>)> {
        let storage = obj.getattr("_d_storage")?;
        let scope = storage.call_method1("get", (self.key.bind(py), py.None()))?;
        if scope.is_none() {
            return Err(PyRuntimeError::new_err("failed to load alias"));
        }

        let target_obj = scope.call_method1("get", (PyString::new(py, &self.target), py.None()))?;
        if target_obj.is_none() {
            return Err(PyRuntimeError::new_err("failed to load alias"));
        }

        let mut current = target_obj.unbind();
        let chain = self.chain.bind(py);
        if chain.len() == 0 {
            return Ok((current, None));
        }

        for index in 0..chain.len() {
            let item = chain.get_item(index)?;
            let attr_name = item.extract::<String>()?;
            if index == chain.len() - 1 {
                return Ok((current, Some(attr_name)));
            }

            match current.bind(py).getattr(attr_name.as_str()) {
                Ok(value) => current = value.unbind(),
                Err(err) if err.is_instance_of::<PyAttributeError>(py) => {
                    return Err(err);
                }
                Err(err) => return Err(err),
            }
        }

        Ok((current, None))
    }

    fn resolve_value(&self, py: Python<'_>, obj: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
        let (target, attr_name) = self.resolve_target(py, obj)?;
        if let Some(attr_name) = attr_name {
            let value = target.bind(py).getattr(attr_name.as_str())?;
            Ok(value.unbind())
        } else {
            Ok(target)
        }
    }

    /// Descriptor get method
    pub fn __get__(
        slf: PyRef<'_, Self>,
        instance: Option<Py<PyAny>>,
        _owner: Option<Py<PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let py = slf.py();
        if instance.is_none() {
            return Ok(slf.into_pyobject(py)?.into_any().unbind().into());
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
            target.bind(py).setattr(attr_name.as_str(), value)?;
            Ok(())
        } else {
            Err(PyAttributeError::new_err("can't set attribute"))
        }
    }

    /// Get target object and attribute name
    pub fn resolve<'py>(&self, py: Python<'py>, obj: Bound<'py, PyAny>) -> PyResult<Py<PyAny>> {
        let (target, attr_name) = self.resolve_target(py, &obj)?;
        let tuple_value = match attr_name {
            Some(attr_name) if self.canset => {
                let attr_name_obj = PyString::new(py, &attr_name).into_any();
                PyTuple::new(py, [target.clone_ref(py), attr_name_obj.into()])?.unbind()
            }
            Some(attr_name) => match target.bind(py).getattr(attr_name.as_str()) {
                Ok(value) => PyTuple::new(
                    py,
                    [
                        value.unbind(),
                        py.None().into_pyobject(py)?.into_any().unbind(),
                    ],
                )?
                .unbind(),
                Err(err) if err.is_instance_of::<PyAttributeError>(py) => return Err(err),
                Err(err) => return Err(err),
            },
            None => PyTuple::new(
                py,
                [
                    target.clone_ref(py),
                    py.None().into_pyobject(py)?.into_any().unbind(),
                ],
            )?
            .unbind(),
        };

        Ok(tuple_value.into())
    }
}
