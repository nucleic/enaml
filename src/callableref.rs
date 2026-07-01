// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;
use pyo3::types::{PyTuple, PyDict, IntoPyDict};

/// CallableRef is a weak reference wrapper for callable objects.
/// When the object is garbage collected, calling the ref returns None.
#[pyclass]
pub struct CallableRef {
    weak_ref: Py<PyAny>,
    callback: Option<Py<PyAny>>,
}

#[pymethods]
impl CallableRef {
    #[new]
    #[pyo3(signature = (obj, callback = None))]
    fn new(
        py: Python<'_>,
        obj: &Bound<'_, PyAny>,
        callback: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
        // Import weakref module and create weak reference with optional callback
        let weakref = py.import("weakref")?;
        let ref_cls = weakref.getattr("ref")?;
        
        // Create the weak reference with optional callback
        // weakref.ref() signature: ref(object, callback=None)
        // Pass callback as positional argument if provided
        let weak_ref = if let Some(cb) = callback {
            ref_cls.call((obj, cb), None)?
        } else {
            ref_cls.call1((obj,))?
        };

        let callback_py = callback.map(|c| c.into());

        Ok(CallableRef {
            weak_ref: weak_ref.unbind(),
            callback: callback_py,
        })
    }

    #[pyo3(signature = (*args, **kwargs))]
    fn __call__(&self, py: Python<'_>, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<Py<PyAny>> {
        // Dereference the weak reference to get the original callable (or None)
        let ref_obj = self.weak_ref.bind(py);
        let obj = ref_obj.call0()?;
        
        // If the weak reference is dead, return None
        if obj.is_none() {
            return Ok(obj.unbind());
        }
        
        // Otherwise, call the original object with the provided arguments
        obj.call(args, kwargs).map(|b| b.unbind())
    }

    fn __repr__(&self) -> String {
        format!("<CallableRef object>")
    }

    fn __eq__(&self, py: Python<'_>, other: &Bound<'_, PyAny>) -> PyResult<bool> {
        // Check if other is also a CallableRef
        if let Ok(other_cr) = other.extract::<PyRef<CallableRef>>() {
            // Compare the underlying weak references by dereferencing them
            let self_obj = self.weak_ref.bind(py).call0()?;
            let other_obj = other_cr.weak_ref.bind(py).call0()?;
            
            // Both must dereference to the same object (or both be None)
            if self_obj.is_none() && other_obj.is_none() {
                return Ok(true);
            }
            
            // Compare by identity
            return Ok(self_obj.is(&other_obj));
        }
        
        // Also compare with raw Python weakref objects
        let self_obj = self.weak_ref.bind(py).call0()?;
        let other_obj = other.call0()?;
        
        // Both must dereference to the same object (or both be None)
        if self_obj.is_none() && other_obj.is_none() {
            return Ok(true);
        }
        
        // Compare by identity
        Ok(self_obj.is(&other_obj))
    }

    fn __reduce__(&self, _py: Python<'_>) -> PyResult<Py<PyAny>> {
        // CallableRef objects cannot be pickled because they hold weak references
        Err(pyo3::exceptions::PyTypeError::new_err(
            "cannot pickle 'CallableRef' object",
        ))
    }
}
