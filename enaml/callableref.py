# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""
Wrapper module for CallableRef class from Rust extension.

This module maintains backward compatibility with the C++ implementation by
re-exporting the CallableRef class from the Rust extension.
"""

try:
    from enaml._rust import CallableRef
except ImportError:
    # Fallback for development or if Rust extension not available
    pass

__all__ = ['CallableRef']
