// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;
use pyo3::types::{PyType, PyTuple, PyDict};

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
        // Validate that input is a bound method
        let inspect = py.import("inspect")?;
        let is_method = inspect.call_method1("ismethod", (method,))?;
        if !is_method.is_truthy()? {
            // Check what was passed for better error message
            let nargs = if method.is_none() {
                "0 arguments"
            } else {
                let builtins = py.import("builtins")?;
                let type_name = builtins.call_method1("type", (method,))?
                    .getattr("__name__")?;
                let type_str = type_name.extract::<String>()?;
                
                if type_str == "method" && method.call_method0("__self__").is_err() {
                    // Unbound method
                    return Err(pyo3::exceptions::PyTypeError::new_err(
                        "cannot create weak reference to an unbound method (MethodType required)",
                    ));
                } else {
                    "1 argument"
                }
            };
            
            return Err(pyo3::exceptions::PyTypeError::new_err(
                format!("WeakMethod() takes 1 argument but {} were given", nargs),
            ));
        }
        
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
        
        // Return the method if alive, None if dead
        Ok(method)
    }

    #[pyo3(name = "_call_with_args")]
    fn _call_with_args(&self, py: Python<'_>, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<Py<PyAny>> {
        // Dereference the weak reference to get the method (or None)
        let method_ref = self.weak_ref.bind(py);
        let method = method_ref.call0()?;
        
        // If the weak reference is dead, return None
        if method.is_none() {
            return Ok(method.unbind());
        }
        
        // Otherwise, call the method with the provided arguments
        method.call(args, kwargs).map(|b| b.unbind())
    }

    fn __repr__(&self) -> String {
        format!("<WeakMethod object>")
    }

    fn __reduce__(&self, _py: Python<'_>) -> PyResult<Bound<'_, PyAny>> {
        // WeakMethod objects cannot be pickled because they hold weak references
        Err(pyo3::exceptions::PyTypeError::new_err(
            "cannot pickle 'WeakMethod' object",
        ))
    }
}
