// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2026, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;

// --------------------------------------------------------------------------------------
// FontStyle - represents text style (normal, italic, oblique)
#[pyclass(immutable_type, skip_from_py_object, module = "enaml._rust")]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FontStyle {
    Normal = 0,
    Italic = 1,
    Oblique = 2,
}

// --------------------------------------------------------------------------------------
// FontStretch - represents font width variations
#[pyclass(immutable_type, skip_from_py_object, module = "enaml._rust")]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FontStretch {
    UltraCondensed = 0,
    ExtraCondensed = 1,
    Condensed = 2,
    SemiCondensed = 3,
    Unstretched = 4,
    SemiExpanded = 5,
    Expanded = 6,
    ExtraExpanded = 7,
    UltraExpanded = 8,
}

// --------------------------------------------------------------------------------------
// FontCaps - represents font capitalization variants
#[pyclass(immutable_type, skip_from_py_object, module = "enaml._rust")]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FontCaps {
    MixedCase = 0,
    AllUppercase = 1,
    AllLowercase = 2,
    SmallCaps = 3,
    Capitalize = 4,
}

/// Font descriptor for Enaml UI elements
#[pyclass(immutable_type, module = "enaml._rust")]
pub struct Font {
    #[pyo3(get, set)]
    _tkdata: Option<Py<PyAny>>,

    #[pyo3(get)]
    family: String,

    #[pyo3(get)]
    pointsize: i32,

    #[pyo3(get)]
    pixelsize: i32,

    #[pyo3(get)]
    weight: i32,

    _style: i32,
    _stretch: i32,
    _caps: i32,
}

#[pymethods]
impl Font {
    #[new]
    #[pyo3(signature = (family = String::new(), pointsize = -1, pixelsize = -1, weight = 400, style = 0, stretch = 4, caps = 0))]
    pub fn new(
        family: String,
        pointsize: i32,
        pixelsize: i32,
        weight: i32,
        style: i32,
        stretch: i32,
        caps: i32,
    ) -> Self {
        Font {
            _tkdata: None,
            family,
            pointsize,
            pixelsize,
            weight,
            _style: style,
            _stretch: stretch,
            _caps: caps,
        }
    }

    #[getter]
    fn style(&self) -> FontStyle {
        match self._style {
            0 => FontStyle::Normal,
            1 => FontStyle::Italic,
            2 => FontStyle::Oblique,
            _ => FontStyle::Normal,
        }
    }

    #[getter]
    fn stretch(&self) -> FontStretch {
        match self._stretch {
            0 => FontStretch::UltraCondensed,
            1 => FontStretch::ExtraCondensed,
            2 => FontStretch::Condensed,
            3 => FontStretch::SemiCondensed,
            4 => FontStretch::Unstretched,
            5 => FontStretch::SemiExpanded,
            6 => FontStretch::Expanded,
            7 => FontStretch::ExtraExpanded,
            8 => FontStretch::UltraExpanded,
            _ => FontStretch::Unstretched,
        }
    }

    #[getter]
    fn caps(&self) -> FontCaps {
        match self._caps {
            0 => FontCaps::MixedCase,
            1 => FontCaps::AllUppercase,
            2 => FontCaps::AllLowercase,
            3 => FontCaps::SmallCaps,
            4 => FontCaps::Capitalize,
            _ => FontCaps::MixedCase,
        }
    }

    pub fn __repr__(&self) -> String {
        format!(
            "Font(family='{}', pointsize={}, pixelsize={}, weight={}, style={}, stretch={}, caps={})",
            self.family, self.pointsize, self.pixelsize, self.weight, self._style, self._stretch, self._caps
        )
    }

    fn __reduce__(
        &self,
        py: Python<'_>,
    ) -> PyResult<(Py<PyAny>, (String, i32, i32, i32, i32, i32, i32))> {
        // Return (_reconstruct_font, (family, pointsize, pixelsize, weight, style, stretch, caps))
        let fonts_module = py.import("enaml.fonts")?;
        let reconstruct = fonts_module.getattr("_reconstruct_font")?;
        let args = (
            self.family.clone(),
            self.pointsize,
            self.pixelsize,
            self.weight,
            self._style,
            self._stretch,
            self._caps,
        );
        Ok((reconstruct.into(), args))
    }
}
