#------------------------------------------------------------------------------
# Copyright (c) 2019, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from textwrap import dedent

import pytest

from utils import compile_source, is_qt_available, wait_for_window_displayed


#------------------------------------------------------------------------------
# Attr Syntax
#------------------------------------------------------------------------------
def test_attr_syntax_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        attr d
    """)
    compile_source(source, 'Main')


def test_attr_syntax_2():
    source = dedent("""\
    from datetime import date
    from enaml.widgets.api import *

    enamldef Main(Window):
        attr d: date
    """)
    compile_source(source, 'Main')


def test_attr_syntax_3():
    source = dedent("""\
    from datetime import date
    from enaml.widgets.api import *

    enamldef Main(Window):
        attr d: date = date.today()
    """)
    compile_source(source, 'Main')


def test_attr_syntax_4():
    source = dedent("""\
    import datetime
    from enaml.widgets.api import *

    enamldef Main(Window):
        attr d = datetime.date.today()
    """)
    compile_source(source, 'Main')


def test_attr_syntax_5():
    source = dedent("""\
    import datetime
    from enaml.widgets.api import *

    enamldef Main(Window):
        attr d: datetime.date
    """)
    compile_source(source, 'Main')


def test_attr_syntax_6():
    source = dedent("""\
    import datetime
    from enaml.widgets.api import *

    enamldef Main(Window):
        attr d: datetime.date = datetime.date.today()
    """)
    compile_source(source, 'Main')


#------------------------------------------------------------------------------
# Bad attr Syntax
#------------------------------------------------------------------------------
def test_bad_attr_syntax_1():
    # Invalid type
    source = dedent("""\
    import datetime
    from enaml.widgets.api import *

    enamldef Main(Window):
        attr d: datetime.date.now()

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_attr_syntax_2():
    # Dot in attr name
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        attr a.d

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_attr_syntax_3():
    # No operator
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        attr d: object ""

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')

#------------------------------------------------------------------------------
# Typechecks
#------------------------------------------------------------------------------
@pytest.mark.skipif(not is_qt_available(), reason='Requires a Qt binding')
def test_attr_type_1(enaml_qtbot, enaml_sleep):
    import datetime
    source = dedent("""\
    import datetime
    from enaml.widgets.api import *

    enamldef Main(Window):
        attr d: datetime.date = datetime.date.today()
        Container:
            Label:
                text << str(d)
    """)
    tester = compile_source(source, 'Main')()
    tester.show()
    wait_for_window_displayed(enaml_qtbot, tester)

    # Should work
    tester.d = (datetime.datetime.now() - datetime.timedelta(days=1)).date()

    # Should raise a type error
    with pytest.raises(TypeError):
        tester.d = datetime.time(7, 0)
