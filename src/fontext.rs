// --------------------------------------------------------------------------------------
// Copyright (c) 2013-2025, Nucleic Development Team.
//
// Distributed under the terms of the Modified BSD License.
//
// The full license is in the file LICENSE, distributed with this software.
// --------------------------------------------------------------------------------------
use pyo3::prelude::*;

// --------------------------------------------------------------------------------------
// FontStyle - represents text style (normal, italic, oblique)
#[pyclass(skip_from_py_object)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FontStyle {
    Normal = 0,
    Italic = 1,
    Oblique = 2,
}

// --------------------------------------------------------------------------------------
// FontStretch - represents font width variations
#[pyclass(skip_from_py_object)]
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
#[pyclass(skip_from_py_object)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FontCaps {
    MixedCase = 0,
    AllUppercase = 1,
    AllLowercase = 2,
    SmallCaps = 3,
    Capitalize = 4,
}



/// Font descriptor for Enaml UI elements
#[pyclass]
pub struct Font {
    #[pyo3(get)]
    family: String,
    
    #[pyo3(get)]
    pointsize: i32,
    
    #[pyo3(get)]
    pixelsize: i32,
    
    #[pyo3(get)]
    weight: i32,
    
    #[pyo3(get)]
    style: i32,
    
    #[pyo3(get)]
    stretch: i32,
    
    #[pyo3(get)]
    caps: i32,
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
            family,
            pointsize,
            pixelsize,
            weight,
            style,
            stretch,
            caps,
        }
    }

    pub fn __repr__(&self) -> String {
        format!(
            "Font(family='{}', pointsize={}, pixelsize={}, weight={}, style={}, stretch={}, caps={})",
            self.family, self.pointsize, self.pixelsize, self.weight, self.style, self.stretch, self.caps
        )
    }
}
