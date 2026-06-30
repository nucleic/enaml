#!/usr/bin/env python
# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""Benchmark: Object creation performance for Color and Font."""
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pyperf

from enaml import colorext, fontext


def main():
    runner = pyperf.Runner()
    
    # Color creation benchmark
    if hasattr(colorext, 'Color'):
        runner.bench_func('color_creation', lambda: colorext.Color(255, 128, 64, 255))
        runner.bench_func('color_creation_defaults', lambda: colorext.Color())
    
    # Font creation benchmark
    if hasattr(fontext, 'Font'):
        runner.bench_func('font_creation', lambda: fontext.Font('Helvetica'))
        runner.bench_func('font_creation_with_args', lambda: fontext.Font('Arial', 12))



if __name__ == '__main__':
    main()
