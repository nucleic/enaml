// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2026, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use core::ffi::c_int;
use pyo3::ffi;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyFunction, PyMapping, PyTuple};

/// Call a function with optional locals mapping.
///
/// This allows Enaml to generate bytecode with LOAD_GLOBAL replaced with LOAD_NAME
/// and use a custom locals mapping to implement dynamic scoping.
#[pyfunction]
#[pyo3(signature = (func, func_args, func_kwargs, func_locals = None))]
pub fn call_func(
    py: Python<'_>,
    func: &Bound<'_, PyFunction>,
    func_args: &Bound<'_, PyTuple>,
    func_kwargs: &Bound<'_, PyDict>,
    func_locals: Option<&Bound<'_, PyMapping>>,
) -> PyResult<Py<PyAny>> {
    let code = func.getattr(intern!(py, "__code__"))?;
    let globals = func.getattr(intern!(py, "__globals__"))?;
    let defaults = func.getattr(intern!(py, "__defaults__"))?;
    let kwdefaults = func.getattr(intern!(py, "__kwdefaults__"))?;
    let closure = func.getattr(intern!(py, "__closure__"))?;

    let mut kw_values = Vec::new();
    for (key, val) in func_kwargs.iter() {
        kw_values.push(key.as_ptr());
        kw_values.push(val.as_ptr());
    }

    let defaults_ptr = if defaults.is_none() {
        std::ptr::null_mut()
    } else {
        let defaults_tuple = defaults.cast::<PyTuple>()?;
        let defaults_values: Vec<*mut ffi::PyObject> =
            defaults_tuple.iter().map(|item| item.as_ptr()).collect();
        defaults_values.as_ptr() as *mut *mut ffi::PyObject
    };
    let default_count = if defaults.is_none() {
        0
    } else {
        defaults.cast::<PyTuple>()?.len()
    };

    let args_ptr = unsafe {
        // Cannot fails since we know we have a tuple,
        // so we provide an empty string for the error message.
        pyo3::ffi::PySequence_Fast_ITEMS(pyo3::ffi::PySequence_Fast(
            func_args.as_ptr(),
            c"".as_ptr(),
        ))
    };

    let locals_ptr = match func_locals {
        Some(locals) => locals.as_ptr(),
        None => std::ptr::null_mut(),
    };

    let closure_ptr = if closure.is_none() {
        std::ptr::null_mut()
    } else {
        closure.as_ptr()
    };

    let kwds_ptr = if kw_values.is_empty() {
        std::ptr::null_mut()
    } else {
        kw_values.as_ptr() as *const *mut ffi::PyObject
    };

    let kwdc = kw_values.len() as c_int / 2;

    unsafe {
        let result = ffi::PyEval_EvalCodeEx(
            code.as_ptr(),
            globals.as_ptr(),
            locals_ptr,
            args_ptr,
            func_args.len() as c_int,
            kwds_ptr,
            kwdc,
            defaults_ptr,
            default_count as c_int,
            kwdefaults.as_ptr(),
            closure_ptr,
        );

        if result.is_null() {
            return Err(PyErr::fetch(py));
        }

        Ok(Bound::from_owned_ptr(py, result).into())
    }
}
