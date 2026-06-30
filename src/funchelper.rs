// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple};

/// Call a function with optional locals mapping.
///
/// This allows Enaml to generate bytecode with LOAD_GLOBAL replaced with LOAD_NAME
/// and use a custom locals mapping to implement dynamic scoping.
///
/// # Arguments
/// - func: A Python function object
/// - func_args: A tuple of arguments to pass to the function
/// - func_kwargs: A dict of keyword arguments
/// - func_locals: Optional mapping for locals (defaults to None)
///
/// TODO: This is a placeholder for future implementation of custom locals support.
#[pyfunction]
#[pyo3(signature = (func, func_args, func_kwargs, func_locals = None))]
#[allow(dead_code)]
pub fn call_func(
    func: &Bound<'_, PyAny>,
    func_args: &Bound<'_, PyTuple>,
    func_kwargs: &Bound<'_, PyDict>,
    func_locals: Option<&Bound<'_, PyAny>>,
) -> PyResult<Py<PyAny>> {
    // Call the function with the provided arguments and custom locals
    // If custom locals provided, we would need bytecode manipulation
    // For now, just do a regular call without custom locals support
    let _unused = func_locals;
    
    let result = func.call(func_args, Some(func_kwargs))?.into();
    Ok(result)
}
