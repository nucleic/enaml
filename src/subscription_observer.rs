// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2026, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;
use pyo3::types::{PyAnyMethods, PyString};

/// Small callable wrapper used when the observed owner cannot be weak-referenced.
#[pyclass(module = "enaml._rust")]
pub struct CallableRef {
    value: Py<PyAny>,
}

#[pymethods]
impl CallableRef {
    #[new]
    pub fn new(value: Py<PyAny>) -> Self {
        Self { value }
    }

    pub fn __call__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(self.value.clone_ref(py))
    }
}

/// Subscription observer for reactive updates.
///
/// Observes object subscriptions and triggers reactive updates when subscribed
/// attributes change. Stores a reference to the observed object (via weakref if
/// possible, otherwise via a callable adapter) and the attribute name.
#[pyclass(immutable_type, module = "enaml._rust")]
pub struct SubscriptionObserver {
    ref_obj: Py<PyAny>,
    attribute: Py<PyAny>,
}

fn make_ref(py: Python<'_>, owner: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    let weakref_module = py.import("weakref")?;
    let ref_fn = weakref_module.getattr("ref")?;

    match ref_fn.call1((owner,)) {
        Ok(weak_ref) => Ok(weak_ref.unbind()),
        Err(err) if err.is_instance_of::<PyTypeError>(py) => {
            let wrapper = Py::new(py, CallableRef::new(owner.clone().unbind()))?;
            Ok(wrapper.into_any())
        }
        Err(err) => Err(err),
    }
}

#[pymethods]
impl SubscriptionObserver {
    #[new]
    pub fn new(
        py: Python<'_>,
        owner: &Bound<'_, PyAny>,
        attribute: &Bound<'_, PyAny>,
    ) -> PyResult<Self> {
        if !attribute.is_instance_of::<PyString>() {
            return Err(PyTypeError::new_err("attribute must be a string"));
        }

        if owner.is_none() {
            return Err(PyTypeError::new_err("owner must not be None"));
        }

        Ok(SubscriptionObserver {
            ref_obj: make_ref(py, owner)?,
            attribute: attribute.into(),
        })
    }

    /// Return the attribute name.
    #[getter]
    pub fn name(&self, py: Python<'_>) -> Py<PyAny> {
        self.attribute.clone_ref(py)
    }

    /// Return the callable ref object used to resolve the owner.
    #[getter]
    pub fn get_ref(&self, py: Python<'_>) -> Py<PyAny> {
        self.ref_obj.clone_ref(py)
    }

    /// Set the ref property - can only be set to None.
    #[setter]
    pub fn set_ref(&mut self, value: &Bound<'_, PyAny>) -> PyResult<()> {
        if value.is_none() {
            self.ref_obj = value.py().None().unbind();
            Ok(())
        } else {
            Err(PyTypeError::new_err("ref can only be set to None"))
        }
    }

    /// Return True when the owner is still available.
    pub fn __bool__(&self, py: Python<'_>) -> bool {
        if self.ref_obj.is_none(py) {
            return false;
        }

        self.ref_obj
            .bind(py)
            .call0()
            .map_or(false, |owner| !owner.is_none())
    }

    /// Call the subscription observer callback.
    pub fn __call__(&self, py: Python<'_>) -> PyResult<()> {
        let owner = self.ref_obj.bind(py).call0()?;
        if owner.is_none() {
            return Ok(());
        }

        match owner.getattr("_d_engine") {
            Ok(engine) => {
                let attr_bound = self.attribute.bind(py);
                engine.call_method("update", (owner, attr_bound), None)?;
                Ok(())
            }
            Err(_) => Ok(()),
        }
    }

    /// Return string representation.
    pub fn __repr__(&self, py: Python<'_>) -> String {
        let owner_str = match self.ref_obj.bind(py).call0() {
            Ok(owner) if !owner.is_none() => owner
                .repr()
                .map(|r| r.to_string())
                .unwrap_or_else(|_| "<error>".to_string()),
            _ => "<dead weakref>".to_string(),
        };

        let attr_str = self
            .attribute
            .bind(py)
            .repr()
            .map(|r| r.to_string())
            .unwrap_or_default();

        format!(
            "SubscriptionObserver(owner={}, attribute={})",
            owner_str, attr_str
        )
    }
}
