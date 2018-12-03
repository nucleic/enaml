#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import pytest

from enaml.c_compat import _fix_co_filename


def test_fix_co_filename():
    """Test fix_co_filename.

    """
    def f():
        a = [i for i in range(10)]

    _fix_co_filename(f.__code__, 'test')
    assert f.__code__.co_filename == 'test'


def test_fix_co_filename_bad_arguments():
    """Test handling bad arguments to fix_co_filename.

    """
    with pytest.raises(TypeError) as excinfo:
        _fix_co_filename(None, None)
    assert 'CodeType' in excinfo.exconly()\

    def f():
        pass

    with pytest.raises(TypeError) as excinfo:
        _fix_co_filename(f.__code__, None)
    assert 'str' in excinfo.exconly()
