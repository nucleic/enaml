# --------------------------------------------------------------------------------------
# Copyright (c) 2026, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""Public interface to the rust accelerated declarative function implementation."""

from enaml._rust import DeclarativeFunction, BoundDeclarativeMethod

__all__ = ["DeclarativeFunction", "BoundDeclarativeMethod"]
