# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""
Wrapper module for Font class and related enums from Rust extension.

This module maintains backward compatibility with the C++ implementation by
re-exporting the Font class and font-related enums from the Rust extension.
"""

try:
    from enaml._rust import Font, FontStyle, FontStretch, FontCaps
except ImportError:
    # Fallback for development or if Rust extension not available
    pass

__all__ = ['Font', 'FontStyle', 'FontStretch', 'FontCaps']
