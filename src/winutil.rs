// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;

/// WinEnum class for Windows icon constants
#[pyclass]
pub struct WinEnum {
    #[pyo3(get)]
    value: u32,
}

#[pymethods]
impl WinEnum {
    #[new]
    pub fn new(value: u32) -> Self {
        WinEnum { value }
    }

    /// Get string representation
    pub fn __repr__(&self) -> String {
        format!("WinEnum({})", self.value)
    }

    /// Get int value
    pub fn __int__(&self) -> u32 {
        self.value
    }
}

/// Load a builtin Windows icon and return its bitmap data
/// 
/// # Arguments
/// - icon_enum: A WinEnum object specifying which icon to load
///
/// # Returns
/// A tuple of (icon_bytes, (width, height)) or (empty, (-1, -1)) if not found
#[pyfunction]
pub fn load_icon(_py: Python<'_>, _icon_enum: &Bound<'_, WinEnum>) -> PyResult<(Vec<u8>, (i32, i32))> {
    // For now, return empty data as placeholder
    // Real Windows implementation would:
    // 1. Use LoadImage() to load the icon resource
    // 2. Convert HICON to ARGB32 bitmap data using GetIconInfo and CreateDIBSection
    // 3. Return the bitmap bytes and dimensions
    
    // Placeholder: return empty icon data
    Ok((vec![], (-1, -1)))
}

/// Create a WinEnum instance for OIC_SAMPLE
#[pyfunction]
pub fn create_oic_sample(py: Python<'_>) -> PyResult<Py<WinEnum>> {
    // On Windows, this would be LoadImage with OIC_SAMPLE resource ID
    // For cross-platform, we create a stub
    Py::new(py, WinEnum { value: 32512 })
}

/// Create a WinEnum instance for OIC_HAND  
#[pyfunction]
pub fn create_oic_hand(py: Python<'_>) -> PyResult<Py<WinEnum>> {
    Py::new(py, WinEnum { value: 32513 })
}

/// Create a WinEnum instance for OIC_QUES
#[pyfunction]
pub fn create_oic_ques(py: Python<'_>) -> PyResult<Py<WinEnum>> {
    Py::new(py, WinEnum { value: 32514 })
}

/// Create a WinEnum instance for OIC_BANG
#[pyfunction]
pub fn create_oic_bang(py: Python<'_>) -> PyResult<Py<WinEnum>> {
    Py::new(py, WinEnum { value: 32515 })
}

/// Create a WinEnum instance for OIC_NOTE
#[pyfunction]
pub fn create_oic_note(py: Python<'_>) -> PyResult<Py<WinEnum>> {
    Py::new(py, WinEnum { value: 32516 })
}

/// Create a WinEnum instance for OIC_WINLOGO
#[pyfunction]
pub fn create_oic_winlogo(py: Python<'_>) -> PyResult<Py<WinEnum>> {
    Py::new(py, WinEnum { value: 32517 })
}

/// Create a WinEnum instance for OIC_WARNING
#[pyfunction]
pub fn create_oic_warning(py: Python<'_>) -> PyResult<Py<WinEnum>> {
    Py::new(py, WinEnum { value: 32515 })
}

/// Create a WinEnum instance for OIC_ERROR
#[pyfunction]
pub fn create_oic_error(py: Python<'_>) -> PyResult<Py<WinEnum>> {
    Py::new(py, WinEnum { value: 32513 })
}

/// Create a WinEnum instance for OIC_INFORMATION
#[pyfunction]
pub fn create_oic_information(py: Python<'_>) -> PyResult<Py<WinEnum>> {
    Py::new(py, WinEnum { value: 32516 })
}

/// Create a WinEnum instance for OIC_SHIELD
#[pyfunction]
pub fn create_oic_shield(py: Python<'_>) -> PyResult<Py<WinEnum>> {
    Py::new(py, WinEnum { value: 32518 })
}
