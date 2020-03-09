#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import pytest
from utils import is_qt_available

pytestmark = pytest.mark.skipif(not is_qt_available(),
                                reason='Requires a Qt binding')

from enaml.fontext import Font


def test_QFont_from_Font():
    # Regression test for PySide: QFont_from_Font was raising a TypeError
    # in its call to qfont.setStyle(font.style).  This test passes if it
    # does not raise an exception.
    from enaml.qt.q_resource_helpers import QFont_from_Font
    f = Font(family="bold")
    qf = QFont_from_Font(f)
