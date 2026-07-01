// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;
use pyo3::types::{PyType, PyTuple, PyDict, IntoPyDict};

/// WeakMethod is a descriptor that stores weak references to bound methods.
/// When the underlying object is garbage collected, the weak reference becomes invalid.
#[pyclass]
pub struct WeakMethod {
    weak_ref: Py<PyAny>,
    callback: Option<Py<PyAny>>,
}

#[pymethods]
impl WeakMethod {
    #[new]
    #[pyo3(signature = (method, callback = None))]
    fn new(
        py: Python<'_>,
        method: &Bound<'_, PyAny>,
        callback: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
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
        let weakmethod_cls = weakref.getattr("WeakMethod")?;
        
        // Create weak reference with optional callback
        // weakref.WeakMethod() signature: WeakMethod(method, callback=None)
        // Pass callback as positional argument if provided
        let weak_ref = if let Some(cb) = callback {
            weakmethod_cls.call((method, cb), None)?
        } else {
            weakmethod_cls.call1((method,))?
        };

        let callback_py = callback.map(|c| c.into());

        Ok(WeakMethod {
            weak_ref: weak_ref.unbind(),
            callback: callback_py,
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

    #[pyo3(signature = (*args, **kwargs))]
    fn __call__(&self, py: Python<'_>, args: &Bound<'_, PyTuple>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<Py<PyAny>> {
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

    fn __eq__(&self, py: Python<'_>, other: &Bound<'_, PyAny>) -> PyResult<bool> {
        // Check if other is also a WeakMethod
        if let Ok(other_wm) = other.extract::<PyRef<WeakMethod>>() {
            // Compare the underlying weak references by dereferencing them
            let self_method = self.weak_ref.bind(py).call0()?;
            let other_method = other_wm.weak_ref.bind(py).call0()?;
            
            // Both must dereference to the same method (or both be None)
            if self_method.is_none() && other_method.is_none() {
                return Ok(true);
            }
            
            // Compare by identity
            Ok(self_method.is(&other_method))
        } else {
            Ok(false)
        }
    }

    fn __reduce__(&self, _py: Python<'_>) -> PyResult<Py<PyAny>> {
        // WeakMethod objects cannot be pickled because they hold weak references
        Err(pyo3::exceptions::PyTypeError::new_err(
            "cannot pickle 'WeakMethod' object",
        ))
    }
}
