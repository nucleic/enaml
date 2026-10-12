// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2026, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;

#[cfg(windows)]
use std::ffi::c_void;
#[cfg(windows)]
use std::mem::size_of;
#[cfg(windows)]
use windows_sys::Win32::Foundation::{HINSTANCE, HWND};
#[cfg(windows)]
use windows_sys::Win32::Graphics::Gdi::{
    CreateCompatibleDC, CreateDIBSection, DeleteDC, DeleteObject, GetDC, ReleaseDC, SelectObject,
    BITMAPINFO, BITMAPINFOHEADER, BI_RGB, DIB_RGB_COLORS, HBITMAP, HBRUSH, HDC, HGDIOBJ,
};
#[cfg(windows)]
use windows_sys::Win32::UI::WindowsAndMessaging::{
    DrawIconEx, GetIconInfo, LoadImageW, DI_NORMAL, HICON, ICONINFO, IMAGE_ICON, LR_SHARED,
};

#[cfg(windows)]
fn make_int_resource(value: u32) -> *const u16 {
    value as usize as *const u16
}

/// WinEnum class for Windows icon constants
#[pyclass(immutable_type, module = "enaml._rust")]
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
pub fn load_icon(
    py: Python<'_>,
    icon_enum: &Bound<'_, WinEnum>,
) -> PyResult<(Vec<u8>, (i32, i32))> {
    #[cfg(not(windows))]
    {
        let _ = py;
        let _ = icon_enum;
        return Ok((vec![], (-1, -1)));
    }

    #[cfg(windows)]
    {
        let value = icon_enum.borrow().value;
        let icon_handle = unsafe {
            LoadImageW(
                0 as HINSTANCE,
                make_int_resource(value) as *const u16,
                IMAGE_ICON,
                0,
                0,
                LR_SHARED,
            )
        } as HICON;
        if icon_handle.is_null() {
            return Ok((vec![], (-1, -1)));
        }

        let mut icon_info = unsafe { std::mem::zeroed::<ICONINFO>() };
        if unsafe { GetIconInfo(icon_handle as HICON, &mut icon_info) } == 0 {
            return Ok((vec![], (-1, -1)));
        }

        let width = if icon_info.xHotspot > 0 {
            icon_info.xHotspot as i32
        } else {
            32
        };
        let height = if icon_info.yHotspot > 0 {
            icon_info.yHotspot as i32
        } else {
            32
        };
        if width <= 0 || height <= 0 {
            unsafe {
                if !icon_info.hbmMask.is_null() {
                    DeleteObject(icon_info.hbmMask as HGDIOBJ);
                }
                if !icon_info.hbmColor.is_null() {
                    DeleteObject(icon_info.hbmColor as HGDIOBJ);
                }
            }
            return Ok((vec![], (-1, -1)));
        }

        let screen_device = unsafe { GetDC(0 as HWND) };
        if screen_device.is_null() {
            unsafe {
                if !icon_info.hbmMask.is_null() {
                    DeleteObject(icon_info.hbmMask as HGDIOBJ);
                }
                if !icon_info.hbmColor.is_null() {
                    DeleteObject(icon_info.hbmColor as HGDIOBJ);
                }
            }
            return Ok((vec![], (-1, -1)));
        }

        let hdc = unsafe { CreateCompatibleDC(screen_device) };
        if hdc.is_null() {
            unsafe {
                ReleaseDC(0 as HWND, screen_device);
                if !icon_info.hbmMask.is_null() {
                    DeleteObject(icon_info.hbmMask as HGDIOBJ);
                }
                if !icon_info.hbmColor.is_null() {
                    DeleteObject(icon_info.hbmColor as HGDIOBJ);
                }
            }
            return Ok((vec![], (-1, -1)));
        }

        let mut bmi = unsafe { std::mem::zeroed::<BITMAPINFO>() };
        bmi.bmiHeader.biSize = size_of::<BITMAPINFOHEADER>() as u32;
        bmi.bmiHeader.biWidth = width;
        bmi.bmiHeader.biHeight = -height;
        bmi.bmiHeader.biPlanes = 1;
        bmi.bmiHeader.biBitCount = 32;
        bmi.bmiHeader.biCompression = BI_RGB;

        let mut bits: *mut c_void = std::ptr::null_mut();
        let win_bitmap = unsafe {
            CreateDIBSection(
                hdc,
                &bmi,
                DIB_RGB_COLORS as u32,
                &mut bits,
                std::ptr::null_mut(),
                0,
            )
        };
        if win_bitmap.is_null() {
            unsafe {
                DeleteDC(hdc);
                ReleaseDC(0 as HWND, screen_device);
                if !icon_info.hbmMask.is_null() {
                    DeleteObject(icon_info.hbmMask as HGDIOBJ);
                }
                if !icon_info.hbmColor.is_null() {
                    DeleteObject(icon_info.hbmColor as HGDIOBJ);
                }
            }
            return Ok((vec![], (-1, -1)));
        }

        let old_hdc = unsafe { SelectObject(hdc, win_bitmap as HGDIOBJ) };
        unsafe {
            DrawIconEx(
                hdc,
                0,
                0,
                icon_handle as HICON,
                width,
                height,
                0,
                0 as HBRUSH,
                DI_NORMAL,
            );
        }

        let len = (width * height * 4) as usize;
        let mut buffer = vec![0u8; len];
        if !bits.is_null() {
            unsafe {
                std::ptr::copy_nonoverlapping(bits as *const u8, buffer.as_mut_ptr(), len);
            }
        }

        unsafe {
            SelectObject(hdc, old_hdc);
            DeleteObject(win_bitmap as HGDIOBJ);
            DeleteDC(hdc);
            ReleaseDC(0 as HWND, screen_device);
            if !icon_info.hbmMask.is_null() {
                DeleteObject(icon_info.hbmMask as HGDIOBJ);
            }
            if !icon_info.hbmColor.is_null() {
                DeleteObject(icon_info.hbmColor as HGDIOBJ);
            }
        }

        Ok((buffer, (width, height)))
    }
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
