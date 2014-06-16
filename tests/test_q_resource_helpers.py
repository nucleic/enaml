#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.fontext import Font
from enaml.qt.q_resource_helpers import QFont_from_Font


def test_QFont_from_Font():
    # Regression test for PySide: QFont_from_Font was raising a TypeError
    # in its call to qfont.setStyle(font.style).  This test passes if it
    # does not raise an exception.
    f = Font(family="bold")
    qf = QFont_from_Font(f)
