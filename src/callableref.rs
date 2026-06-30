// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;

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

    fn __call__<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
        // Dereference the weak reference
        let ref_obj = self.weak_ref.bind(py);
        ref_obj.call0()
    }

    fn __repr__(&self) -> String {
        format!("<CallableRef object>")
    }
}
