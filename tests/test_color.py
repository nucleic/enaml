#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import pickle

from enaml.colors import Color


def test_color_initialization():
    """Test the different initialization format supported by Color.

    """
    components = [1, 2, 3, 4]
    c = Color(*components)
    for name, value in zip(['red', 'green', 'blue', 'alpha'], components):
        assert getattr(c, name) == value

    c = Color(alpha=-1)
    for name in ['red', 'green', 'blue', 'alpha']:
        assert getattr(c, name) == 0

    assert c._tkdata is None

    try:
        from enaml.qt.q_resource_helpers import get_cached_qcolor
    except Exception:
        return
    get_cached_qcolor(c)
    assert c._tkdata is not None


def test_color_repr():
    """Test the repr of Color.

    """
    c = Color(1, 2, 3)
    print(repr(c))
    cbis = eval(repr(c))
    for attr in ('red', 'green', 'blue', 'alpha', 'argb'):
        assert getattr(c, attr) == getattr(cbis, attr)


def test_color_pickle():
    """Test pickling/unpickling color.

    """
    rgba = 1, 2, 3, 4
    c = Color(*rgba)
    print(c.__reduce__())
    blob = pickle.dumps(c)
    c = pickle.loads(blob)
    assert (c.red, c.green, c.blue, c.alpha) == rgba
