# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""
Wrapper module for WeakMethod class from Rust extension.

This module maintains backward compatibility with the C++ implementation by
re-exporting the WeakMethod class from the Rust extension.
"""

try:
    from enaml._rust import WeakMethod
except ImportError:
    # Fallback for development or if Rust extension not available
    pass

__all__ = ['WeakMethod']
