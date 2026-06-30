# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""Benchmarks for attribute access and manipulation performance.

These benchmarks measure the performance of getting and setting attributes
on enaml extension objects like Color and Font.
"""
import pytest


class TestColorAttributeAccess:
    """Benchmark Color attribute access performance."""
    
    def test_color_attribute_get_red(self, benchmark, sample_color):
        """Benchmark Color.red property getter."""
        benchmark(lambda: sample_color.red if hasattr(sample_color, 'red') else None)
    
    def test_color_attribute_get_green(self, benchmark, sample_color):
        """Benchmark Color.green property getter."""
        benchmark(lambda: sample_color.green if hasattr(sample_color, 'green') else None)
    
    def test_color_attribute_get_blue(self, benchmark, sample_color):
        """Benchmark Color.blue property getter."""
        benchmark(lambda: sample_color.blue if hasattr(sample_color, 'blue') else None)
    
    def test_color_attribute_get_alpha(self, benchmark, sample_color):
        """Benchmark Color.alpha property getter."""
        benchmark(lambda: sample_color.alpha if hasattr(sample_color, 'alpha') else None)
    
    def test_color_argb(self, benchmark, sample_color):
        """Benchmark Color.argb property getter."""
        benchmark(lambda: sample_color.argb)


class TestFontAttributeAccess:
    """Benchmark Font attribute access performance."""
    
    def test_font_attribute_get_pointsize(self, benchmark, sample_font):
        """Benchmark Font.pointsize property getter."""
        benchmark(lambda: sample_font.pointsize if hasattr(sample_font, 'pointsize') else None)
    
    def test_font_attribute_get_bold(self, benchmark, sample_font):
        """Benchmark Font.bold property getter."""
        benchmark(lambda: sample_font.bold if hasattr(sample_font, 'bold') else None)
    
    def test_font_attribute_get_italic(self, benchmark, sample_font):
        """Benchmark Font.italic property getter."""
        benchmark(lambda: sample_font.italic if hasattr(sample_font, 'italic') else None)
    
    def test_font_attribute_get_family(self, benchmark, sample_font):
        """Benchmark Font.family property getter."""
        benchmark(lambda: sample_font.family if hasattr(sample_font, 'family') else None)
