#------------------------------------------------------------------------------
# Copyright (c) 2020-2021, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import traceback as tb
from textwrap import dedent

import pytest

from utils import compile_source


def test_validate_declarative_1():
    """ Test that we reject children that are not type in enamldef.

    This also serves to test the good working of try_squash_raise.

    """
    source = dedent("""\
    from enaml.widgets.api import *

    a = 1

    enamldef Main(Window):
        a:
            pass

    """)
    with pytest.raises(TypeError) as exc:
        Main = compile_source(source, 'Main')

    ftb = "\n".join(tb.format_tb(exc.tb))
    assert " validate_declarative" not in ftb


def test_validate_declarative_2():
    """ Test that we reject children that are not declarative in enamldef.

    This also serves to test the good working of try_squash_raise.

    """
    source = dedent("""\
    from enaml.widgets.api import *

    class A:
        pass

    enamldef Main(Window):
        A:
            pass

    """)
    with pytest.raises(TypeError) as exc:
        Main = compile_source(source, 'Main')

    ftb = "\n".join(tb.format_tb(exc.tb))
    assert " validate_declarative" not in ftb


# XXX add test regarding handling of with statement
