// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;
use pyo3::types::PyType;

/// WeakMethod is a descriptor that stores weak references to bound methods.
/// When the underlying object is garbage collected, the weak reference becomes invalid.
#[pyclass]
pub struct WeakMethod {
    weak_ref: Py<PyAny>,
}

#[pymethods]
impl WeakMethod {
    #[new]
    fn new(py: Python<'_>, method: &Bound<'_, PyAny>) -> PyResult<Self> {
        // Import weakref module and get WeakMethod
        let weakref = py.import("weakref")?;
        
        // Get or create the weak reference
        // For bound methods, we use a WeakMethod (Python 3.4+) which handles them properly
        let weak_ref = if let Ok(weakmethod_cls) = weakref.getattr("WeakMethod") {
            weakmethod_cls.call1((method,))?
        } else {
            // Fallback for older Python versions
            let ref_cls = weakref.getattr("ref")?;
            ref_cls.call1((method,))?
        };

        Ok(WeakMethod {
            weak_ref: weak_ref.unbind(),
        })
    }

    fn __get__<'s>(
        &'s self,
        _obj: Option<&'s Bound<'_, PyAny>>,
        _obj_type: Option<&'s Bound<'_, PyType>>,
        py: Python<'s>,
    ) -> PyResult<Bound<'s, PyAny>> {
        // Check if the weak reference is still valid
        let method_ref = self.weak_ref.bind(py);
        let method = method_ref.call0()?;
        
        if method.is_none() {
            return Err(pyo3::exceptions::PyReferenceError::new_err(
                "weakly-referenced object no longer exists",
            ));
        }
        
        Ok(method)
    }

    fn __repr__(&self) -> String {
        format!("<WeakMethod object>")
    }
}
