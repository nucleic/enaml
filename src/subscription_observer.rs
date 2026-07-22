// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2026, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::types::PyString;
use pyo3::{pyclass, pymethods, types::PyAnyMethods, Bound, Py, PyAny, PyResult, Python};

/// Subscription observer for reactive updates.
///
/// Observes object subscriptions and triggers reactive updates when subscribed
/// attributes change. Stores a weak reference to the observed object and the attribute name.
#[pyclass(immutable_type, module = "enaml._rust")]
pub struct SubscriptionObserver {
    weak_ref: Py<PyAny>,
    attribute: Py<PyAny>,
}

#[pymethods]
impl SubscriptionObserver {
    #[new]
    pub fn new(
        py: Python<'_>,
        owner: &Bound<'_, PyAny>,
        attribute: &Bound<'_, PyAny>,
    ) -> PyResult<Self> {
        // Validate that attribute is a string
        if !attribute.is_instance_of::<PyString>() {
            return Err(pyo3::exceptions::PyTypeError::new_err(
                "attribute must be a string",
            ));
        }

        // Validate that owner is not None
        if owner.is_none() {
            return Err(pyo3::exceptions::PyTypeError::new_err(
                "owner must not be None",
            ));
        }

        // Create weak reference to owner
        let weakref_module = py.import("weakref")?;
        let ref_fn = weakref_module.getattr("ref")?;
        let weak_ref = ref_fn.call1((owner,))?;

        Ok(SubscriptionObserver {
            weak_ref: weak_ref.unbind(),
            attribute: attribute.into(),
        })
    }

    /// Return the attribute name
    #[getter]
    pub fn name(&self, py: Python<'_>) -> Py<PyAny> {
        self.attribute.clone_ref(py)
    }

    /// Return the weak reference to the owner (callable property)
    /// When called, returns the actual owner object
    #[getter]
    pub fn get_ref(&self, py: Python<'_>) -> Py<PyAny> {
        self.weak_ref.clone_ref(py)
    }

    /// Set the ref property - can only be set to None
    #[setter]
    pub fn set_ref(&mut self, value: &Bound<'_, PyAny>) -> PyResult<()> {
        if value.is_none() {
            self.weak_ref = value.py().None();
            Ok(())
        } else {
            Err(pyo3::exceptions::PyTypeError::new_err(
                "ref can only be set to None",
            ))
        }
    }

    /// Return True if the weak reference is valid (owner is still alive)
    pub fn __bool__(&self, py: Python<'_>) -> bool {
        !self.weak_ref.is_none(py)
    }

    /// Call the subscription observer callback
    pub fn __call__(&self, py: Python<'_>) -> PyResult<()> {
        // Dereference the weak reference to get the owner
        let weak_ref_bound = self.weak_ref.bind(py);
        let owner = weak_ref_bound.call0()?;

        // If weak reference is dead (returns None), do nothing
        if owner.is_none() {
            return Ok(());
        }

        // Try to get _d_engine attribute from owner and call its update method
        match owner.getattr("_d_engine") {
            Ok(engine) => {
                // Call engine.update(owner, attribute_name)
                let attr_bound = self.attribute.bind(py);
                engine.call_method("update", (owner, attr_bound), None)?;
                Ok(())
            }
            Err(_) => {
                // If _d_engine doesn't exist, silently ignore
                Ok(())
            }
        }
    }

    /// Return string representation
    pub fn __repr__(&self, py: Python<'_>) -> String {
        // Try to dereference to show the owner
        let weak_ref_bound = self.weak_ref.bind(py);
        let owner_str = match weak_ref_bound.call0() {
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
