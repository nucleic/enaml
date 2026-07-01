// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;

mod alias;
mod colorext;
mod declarative_function;
mod dynamicscope;
mod fontext;
mod funchelper;
mod subscription_observer;
mod winutil;

use alias::Alias;
use colorext::Color;
use declarative_function::{BoundDeclarativeMethod, DeclarativeFunction};
use dynamicscope::{DynamicScope, UserKeyError};
use fontext::Font;
use funchelper::call_func;
use subscription_observer::SubscriptionObserver;
use winutil::WinEnum;

/// Python module entry point for enaml Rust extensions
#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Color class
    m.add_class::<Color>()?;

    // Font class and enums
    m.add_class::<Font>()?;
    m.add_class::<fontext::FontStyle>()?;
    m.add_class::<fontext::FontStretch>()?;
    m.add_class::<fontext::FontCaps>()?;

    // Alias descriptor class
    m.add_class::<Alias>()?;

    // SubscriptionObserver class
    m.add_class::<SubscriptionObserver>()?;

    // DeclarativeFunction classes
    m.add_class::<DeclarativeFunction>()?;
    m.add_class::<BoundDeclarativeMethod>()?;

    // DynamicScope class
    m.add_class::<DynamicScope>()?;
    m.add("UserKeyError", m.py().get_type::<UserKeyError>())?;

    // funchelper function for call with dynamic scope
    m.add_function(wrap_pyfunction!(call_func, m)?)?;

    // WinUtil classes and functions
    m.add_class::<WinEnum>()?;
    m.add_function(wrap_pyfunction!(winutil::load_icon, m)?)?;
    m.add_function(wrap_pyfunction!(winutil::create_oic_sample, m)?)?;
    m.add_function(wrap_pyfunction!(winutil::create_oic_hand, m)?)?;
    m.add_function(wrap_pyfunction!(winutil::create_oic_ques, m)?)?;
    m.add_function(wrap_pyfunction!(winutil::create_oic_bang, m)?)?;
    m.add_function(wrap_pyfunction!(winutil::create_oic_note, m)?)?;
    m.add_function(wrap_pyfunction!(winutil::create_oic_winlogo, m)?)?;
    m.add_function(wrap_pyfunction!(winutil::create_oic_warning, m)?)?;
    m.add_function(wrap_pyfunction!(winutil::create_oic_error, m)?)?;
    m.add_function(wrap_pyfunction!(winutil::create_oic_information, m)?)?;
    m.add_function(wrap_pyfunction!(winutil::create_oic_shield, m)?)?;

    m.add("__name__", "enaml._rust")?;
    Ok(())
}
