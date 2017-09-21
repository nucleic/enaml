#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
"""Pytest fixtures.

"""
import os
# Make sure enaml already imported qt toavoid issues with pytest
import enaml.qt
os.environ.setdefault('PYTEST_QT_API', 'pyqt4v2')

pytest_plugins = str('enaml.testing.fixtures'),
