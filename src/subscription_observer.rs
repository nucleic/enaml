// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;

/// Subscription observer for reactive updates.
///
/// Observes object subscriptions and triggers reactive updates when subscribed
/// attributes change. Stores references to the observed object and attribute.
#[pyclass(module = "enaml._rust", frozen)]
pub struct SubscriptionObserver {
    owner: Py<PyAny>,
    attribute: Py<PyAny>,
}

#[pymethods]
impl SubscriptionObserver {
    #[new]
    pub fn new(owner: Py<PyAny>, attribute: Py<PyAny>) -> Self {
        SubscriptionObserver { owner, attribute }
    }

    /// Return string representation
    pub fn __repr__(&self, py: Python<'_>) -> String {
        let owner_str = self
            .owner
            .bind(py)
            .repr()
            .map(|r| r.to_string())
            .unwrap_or_default();
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
