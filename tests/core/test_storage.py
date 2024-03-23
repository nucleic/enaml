#------------------------------------------------------------------------------
# Copyright (c) 2019-2023, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from textwrap import dedent

import pytest

from utils import compile_source, wait_for_window_displayed


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


#------------------------------------------------------------------------------
# Const Syntax
#------------------------------------------------------------------------------
def test_const_syntax_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        const editing = False
    """)
    compile_source(source, 'Main')


def test_const_syntax_2():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        const message: str = "Hello world"
    """)
    compile_source(source, 'Main')


def test_const_syntax_3():
    # ChildDef const
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        Label:
            const show_extra = False
    """)
    compile_source(source, 'Main')


def test_bad_const_syntax_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        const enabled
    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_const_syntax_2():
    # Must have an expr
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        const enabled: bool
    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_const_syntax_3():
    # Invalid op
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        const message: str << str(self)
    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_const_expr_1(enaml_qtbot, enaml_sleep):
    import datetime
    source = dedent("""\
    import datetime
    from enaml.widgets.api import *

    enamldef Main(Window):
        const d: datetime.date = datetime.date.today()
        Container:
            Label:
                text << str(d)
    """)
    tester = compile_source(source, 'Main')()
    tester.show()
    wait_for_window_displayed(enaml_qtbot, tester)

    # const cannot be changed
    with pytest.raises(TypeError):
        tester.d = (datetime.datetime.now() - datetime.timedelta(days=1)).date()


def test_const_expr_2(enaml_qtbot, enaml_sleep):
    import datetime
    source = dedent("""\
    import datetime
    from enaml.widgets.api import *

    enamldef Main(Window):
        const d: datetime.date = "1970-1-1"
    """)
    tester = compile_source(source, 'Main')()
    tester.show()
    wait_for_window_displayed(enaml_qtbot, tester)

    # const type expr invalid
    with pytest.raises(TypeError):
        tester.d


def test_const_expr_3(enaml_qtbot, enaml_sleep):
    from datetime import datetime
    source = dedent("""\
    import datetime
    from enaml.widgets.api import *

    enamldef Main(Window):
        const d: datetime.date = None
    """)
    today = datetime.now().date()
    tester = compile_source(source, 'Main')(d=today)
    tester.show()
    wait_for_window_displayed(enaml_qtbot, tester)

    # const initial value can be passed in
    assert tester.d == today

