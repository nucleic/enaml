// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;
use pyo3::types::iter::BoundTupleIterator;
use pyo3::types::{PyDict, PyTuple};

/// Declarative function descriptor for Enaml DSL.
///
/// Wraps a function with a scope key for use in declarative blocks.
#[pyclass(immutable_type, module = "enaml._rust")]
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
                    slf.func.clone_ref(py),
                    obj.clone().unbind(),
                    slf.key.clone_ref(py),
                ),
            )?
            .into_any())
        } else {
            // Return the descriptor itself by extracting from the existing PyRef
            Ok(Bound::new(
                py,
                DeclarativeFunction {
                    func: slf.func.clone_ref(py),
                    key: slf.key.clone_ref(py),
                },
            )?
            .into_any())
        }
    }

    pub fn __call__<'py>(
        &self,
        py: Python<'py>,
        args: &Bound<'py, PyTuple>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        // Call the wrapped function with the provided arguments
        let func = self.func.bind(py);

        Ok(func.call(args, kwargs)?)
    }

    pub fn __repr__(&self) -> String {
        format!("<declarative function object at {:p}>", self as *const _)
    }
}

/// Bound declarative method for Enaml DSL.
///
/// Represents a declarative function bound to an instance.
#[pyclass(immutable_type, module = "enaml._rust")]
pub struct BoundDeclarativeMethod {
    #[pyo3(get)]
    func: Py<PyAny>,
    #[pyo3(get)]
    obj: Py<PyAny>,
    #[pyo3(get)]
    key: Py<PyAny>,
}

struct TuplePrepender<'py> {
    py: Python<'py>,
    self_bound: Bound<'py, PyAny>,
    args: Bound<'py, PyTuple>,
    chain: std::iter::Chain<std::iter::Once<Bound<'py, PyAny>>, BoundTupleIterator<'py>>,
}

impl<'py> TuplePrepender<'py> {
    fn new(py: Python<'py>, self_bound: Bound<'py, PyAny>, args: Bound<'py, PyTuple>) -> Self {
        let chain = std::iter::once(self_bound.clone()).chain(args.iter());
        TuplePrepender {
            py,
            self_bound,
            args,
            chain,
        }
    }
}

impl<'py> Iterator for TuplePrepender<'py> {
    type Item = Bound<'py, PyAny>;

    fn next(&mut self) -> Option<Self::Item> {
        self.chain.next()
    }
}

impl ExactSizeIterator for TuplePrepender<'_> {
    fn len(&self) -> usize {
        1 + self.args.len()
    }
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

    pub fn __call__<'py>(
        slf: PyRef<'py, Self>,
        py: Python<'py>,
        args: Bound<'py, PyTuple>,
        kwargs: Option<&'py Bound<'py, PyDict>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        // Prepend self to the arguments by creating a new tuple
        let self_bound = slf.obj.bind(py).clone();
        let new_tuple = PyTuple::new(py, TuplePrepender::new(py, self_bound, args))?;

        // Call the wrapped function with self as first argument
        let func = slf.func.bind(py);

        func.call(&new_tuple, kwargs)
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
