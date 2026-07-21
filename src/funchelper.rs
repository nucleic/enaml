// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use core::ffi::c_int;
use pyo3::ffi;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyFunction, PyTuple};

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
    func_locals: Option<&Bound<'_, PyDict>>,
) -> PyResult<Py<PyAny>> {
    let code = func.getattr("__code__")?;
    let globals = func.getattr("__globals__")?;
    let defaults = func.getattr("__defaults__")?;
    let closure = func.getattr("__closure__")?;

    let arg_count = func_args.len();
    let mut arg_values = Vec::with_capacity(arg_count);
    for item in func_args.iter() {
        arg_values.push(item.as_ptr());
    }

    let mut kw_values = Vec::new();
    let mut pos = 0;
    let mut key_ptr: *mut ffi::PyObject = std::ptr::null_mut();
    let mut value_ptr: *mut ffi::PyObject = std::ptr::null_mut();
    unsafe {
        while ffi::PyDict_Next(func_kwargs.as_ptr(), &mut pos, &mut key_ptr, &mut value_ptr) != 0 {
            kw_values.push(key_ptr);
            kw_values.push(value_ptr);
        }
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

    let locals_ptr = match func_locals {
        Some(locals) => locals.as_ptr(),
        None => std::ptr::null_mut(),
    };

    let closure_ptr = if closure.is_none() {
        std::ptr::null_mut()
    } else {
        closure.as_ptr()
    };

    let args_ptr = if arg_values.is_empty() {
        std::ptr::null_mut()
    } else {
        arg_values.as_ptr() as *const *mut ffi::PyObject
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
            arg_count as c_int,
            kwds_ptr,
            kwdc,
            defaults_ptr,
            default_count as c_int,
            std::ptr::null_mut(),
            closure_ptr,
        );

        if result.is_null() {
            return Err(PyErr::fetch(py));
        }

        Ok(Bound::from_owned_ptr(py, result).into())
    }
}
