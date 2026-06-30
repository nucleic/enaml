#!/usr/bin/env python
# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""Benchmark: Attribute access performance for Color and Font."""
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pyperf

from enaml import colorext, fontext


def main():
    runner = pyperf.Runner()
    
    # Create test objects once
    if hasattr(colorext, 'Color'):
        color = colorext.Color(255, 128, 64)
        runner.bench_func(
            'color_attribute_read',
            lambda: (color.red, color.green, color.blue, color.alpha, color.argb)
        )
    
    # Font attribute access
    if hasattr(fontext, 'Font'):
        font = fontext.Font('Arial', 12)
        runner.bench_func(
            'font_attribute_read',
            lambda: (font.family, font.pointsize, font.weight, font.style)
        )


if __name__ == '__main__':
    main()
