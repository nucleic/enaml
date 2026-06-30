// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;
use pyo3::types::PyTuple;

/// Declarative function descriptor for Enaml DSL.
///
/// Wraps a function with a scope key for use in declarative blocks.
#[pyclass]
pub struct DeclarativeFunction {
    #[pyo3(get)]
    func: Py<PyAny>,
    #[pyo3(get)]
    key: Py<PyAny>,
}

#[pymethods]
impl DeclarativeFunction {
    #[new]
    pub fn new(func: Py<PyAny>, key: Py<PyAny>) -> PyResult<Self> {
        Ok(DeclarativeFunction { func, key })
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

    pub fn __get__(
        slf: PyRef<'_, Self>,
        obj: Option<Py<PyAny>>,
        _owner: Option<Py<PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let py = slf.py();
        if let Some(obj) = obj {
            // Return a BoundDeclarativeMethod
            Ok(Py::new(
                py,
                BoundDeclarativeMethod::new(slf.func.clone_ref(py), obj.clone_ref(py), slf.key.clone_ref(py)),
            )?
            .into())
        } else {
            // Return the descriptor itself by extracting from the existing PyRef
            Ok(Py::new(py, DeclarativeFunction {
                func: slf.func.clone_ref(py),
                key: slf.key.clone_ref(py),
            })?
            .into())
        }
    }

    pub fn __call__(
        &self,
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        // Call the wrapped function with the provided arguments
        let func = self.func.bind(py);
        // Try to use kwargs as PyDict, otherwise try to cast
        let kwargs_dict = if let Some(k) = kwargs {
            // Try to extract to PyDict
            if let Ok(d) = k.extract::<Bound<'_, pyo3::types::PyDict>>() {
                Some(d.clone())
            } else {
                None
            }
        } else {
            None
        };
        
        let result = if let Some(d) = &kwargs_dict {
            func.call(args, Some(d))?
        } else {
            func.call(args, None)?
        };
        Ok(result.into())
    }

    pub fn __repr__(&self) -> String {
        format!("<declarative function object at {:p}>", self as *const _)
    }
}

/// Bound declarative method for Enaml DSL.
///
/// Represents a declarative function bound to an instance.
#[pyclass]
pub struct BoundDeclarativeMethod {
    #[pyo3(get)]
    func: Py<PyAny>,
    #[pyo3(get)]
    obj: Py<PyAny>,
    #[pyo3(get)]
    key: Py<PyAny>,
}

#[pymethods]
impl BoundDeclarativeMethod {
    #[new]
    pub fn new(func: Py<PyAny>, obj: Py<PyAny>, key: Py<PyAny>) -> Self {
        BoundDeclarativeMethod { func, obj, key }
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

    pub fn __call__(
        &self,
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        // Prepend self to the arguments by creating a new tuple
        let self_bound = self.obj.bind(py);
        let mut new_args_vec = vec![self_bound.into()];
        for arg in args.iter() {
            new_args_vec.push(arg);
        }
        let new_tuple = PyTuple::new(py, new_args_vec)?;
        
        // Call the wrapped function with self as first argument
        let func = self.func.bind(py);
        // Try to use kwargs as PyDict, otherwise None
        let kwargs_dict = if let Some(k) = kwargs {
            // Try to extract to PyDict
            if let Ok(d) = k.extract::<Bound<'_, pyo3::types::PyDict>>() {
                Some(d.clone())
            } else {
                None
            }
        } else {
            None
        };
        
        let result = if let Some(d) = &kwargs_dict {
            func.call(&new_tuple, Some(d))?
        } else {
            func.call(&new_tuple, None)?
        };
        Ok(result.into())
    }

    pub fn __repr__(&self) -> String {
        format!("<bound declarative method object at {:p}>", self as *const _)
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
