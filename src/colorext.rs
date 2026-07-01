// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;

/// Color class wrapping ARGB value in Qt's #AARRGGBB byte order
#[pyclass]
pub struct Color {
    #[pyo3(get, set)]
    _tkdata: Option<Py<PyAny>>,
    #[pyo3(get)]
    argb: u32,
}

#[pymethods]
impl Color {
    #[new]
    #[pyo3(signature = (red = -1, green = -1, blue = -1, alpha = 255))]
    fn new(red: i32, green: i32, blue: i32, alpha: i32) -> Self {
        let (r, g, b, a) = if red < 0 || green < 0 || blue < 0 || alpha < 0 {
            (0, 0, 0, 0)
        } else {
            (
                (red.max(0).min(255)) as u32,
                (green.max(0).min(255)) as u32,
                (blue.max(0).min(255)) as u32,
                (alpha.max(0).min(255)) as u32,
            )
        };

        let argb = (a << 24) | (r << 16) | (g << 8) | b;
        Color {
            _tkdata: None,
            argb,
        }
    }

    #[getter]
    fn alpha(&self) -> u32 {
        (self.argb >> 24) & 0xFF
    }

    #[getter]
    fn red(&self) -> u32 {
        (self.argb >> 16) & 0xFF
    }

    #[getter]
    fn green(&self) -> u32 {
        (self.argb >> 8) & 0xFF
    }

    #[getter]
    fn blue(&self) -> u32 {
        self.argb & 0xFF
    }

    fn __repr__(&self) -> String {
        format!(
            "Color(red={}, green={}, blue={}, alpha={})",
            self.red(),
            self.green(),
            self.blue(),
            self.alpha()
        )
    }

    fn __reduce__(&self, py: Python<'_>) -> PyResult<(Py<PyAny>, (u32, u32, u32, u32))> {
        // Return (_reconstruct_color, (red, green, blue, alpha))
        // _reconstruct_color is imported from enaml.colors module
        let colors_module = py.import("enaml.colors")?;
        let reconstruct = colors_module.getattr("_reconstruct_color")?;
        let args = (self.red(), self.green(), self.blue(), self.alpha());
        Ok((reconstruct.into(), args))
    }
}
