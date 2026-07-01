# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""Benchmark fixtures and configuration for enaml extensions."""
import pytest


@pytest.fixture
def color_module():
    """Fixture providing the enaml.colorext module."""
    try:
        import enaml.colorext as colorext
        return colorext
    except ImportError:
        pytest.skip("enaml.colorext not available")


@pytest.fixture
def font_module():
    """Fixture providing the enaml.fontext module."""
    try:
        import enaml.fontext as fontext
        return fontext
    except ImportError:
        pytest.skip("enaml.fontext not available")


@pytest.fixture
def sample_color(color_module):
    """Fixture providing a sample Color object."""
    if hasattr(color_module, 'Color'):
        return color_module.Color(255, 128, 64, 255)
    pytest.skip("Color class not available")


@pytest.fixture
def sample_font(font_module):
    """Fixture providing a sample Font object."""
    if hasattr(font_module, 'Font'):
        return font_module.Font()
    pytest.skip("Font class not available")
