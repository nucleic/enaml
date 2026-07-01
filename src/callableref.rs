// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;
use pyo3::types::{PyTuple, PyDict};

/// CallableRef is a weak reference wrapper for callable objects.
/// When the object is garbage collected, calling the ref returns None.
#[pyclass]
pub struct CallableRef {
    weak_ref: Py<PyAny>,
}

#[pymethods]
impl CallableRef {
    #[new]
    fn new(py: Python<'_>, obj: &Bound<'_, PyAny>) -> PyResult<Self> {
        // Import weakref module and create weak reference
        let weakref = py.import("weakref")?;
        let ref_cls = weakref.getattr("ref")?;
        let weak_ref = ref_cls.call1((obj,))?;

        Ok(CallableRef {
            weak_ref: weak_ref.unbind(),
        })
    }

    #[pyo3(name = "_get_ref")]
    fn _get_ref(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        // Get the weak reference (call0() dereferences it)
        let ref_obj = self.weak_ref.bind(py);
        let obj = ref_obj.call0()?;
        Ok(obj.unbind())
    }

    #[pyo3(name = "_call_with_args")]
    fn _call_with_args(&self, py: Python<'_>, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<Py<PyAny>> {
        // Dereference the weak reference to get the original callable (or None)
        let ref_obj = self.weak_ref.bind(py);
        let obj = ref_obj.call0()?;
        
        // If the weak reference is dead, obj is None - return it
        if obj.is_none() {
            return Ok(obj.unbind());
        }
        
        // Otherwise, call the original object with the provided arguments
        obj.call(args, kwargs).map(|b| b.unbind())
    }

    fn __repr__(&self) -> String {
        format!("<CallableRef object>")
    }

    fn __reduce__(&self, _py: Python<'_>) -> PyResult<Bound<'_, PyAny>> {
        // CallableRef objects cannot be pickled because they hold weak references
        Err(pyo3::exceptions::PyTypeError::new_err(
            "cannot pickle 'CallableRef' object",
        ))
    }
}
