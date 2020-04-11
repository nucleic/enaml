#------------------------------------------------------------------------------
# Copyright (c) 2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Test winutil icon loading on windows.

"""
import sys
import pytest


@pytest.mark.skipif(sys.platform != "win32", reason="Limited to Windows")
def test_winutil_load_icon():
    from enaml import winutil
    winutil.load_icon(winutil.OIC_INFORMATION)
