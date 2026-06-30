# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""Benchmarks for object creation performance (Color, Font).

These benchmarks measure the performance of creating and instantiating
enaml extension objects. They should be run before and after migration
to PyO3 to ensure no performance regressions.
"""
import pytest


class TestColorCreation:
    """Benchmark Color object creation performance."""
    
    def test_color_creation(self, benchmark, color_module):
        """Benchmark creating Color objects."""
        def create_color():
            if hasattr(color_module, 'Color'):
                return color_module.Color(255, 128, 64, 255)
            return None
        
        benchmark(create_color)
    
    def test_color_attribute_access(self, benchmark, sample_color):
        """Benchmark Color attribute access (getters)."""
        def access_attributes():
            _ = sample_color.argb
            if hasattr(sample_color, 'red'):
                _ = sample_color.red
            if hasattr(sample_color, 'green'):
                _ = sample_color.green
            if hasattr(sample_color, 'blue'):
                _ = sample_color.blue
        
        benchmark(access_attributes)


class TestFontCreation:
    """Benchmark Font object creation performance."""
    
    def test_font_creation(self, benchmark, font_module):
        """Benchmark creating Font objects."""
        def create_font():
            if hasattr(font_module, 'Font'):
                return font_module.Font()
            return None
        
        benchmark(create_font)
    
    def test_font_attribute_access(self, benchmark, sample_font):
        """Benchmark Font attribute access."""
        def access_attributes():
            if hasattr(sample_font, 'pointsize'):
                _ = sample_font.pointsize
            if hasattr(sample_font, 'bold'):
                _ = sample_font.bold
            if hasattr(sample_font, 'italic'):
                _ = sample_font.italic
        
        benchmark(access_attributes)
