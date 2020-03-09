#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from textwrap import dedent

import pytest

from utils import compile_source


#------------------------------------------------------------------------------
# Template Syntax
#------------------------------------------------------------------------------
def test_syntax_1():
    source = dedent("""\
    template Main():
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_2():
    source = dedent("""\
    template Main(): pass

    """)
    compile_source(source, 'Main')


def test_syntax_3():
    source = dedent("""\
    template Main():
        const value = 12

    """)
    compile_source(source, 'Main')


def test_syntax_4():
    source = dedent("""\
    template Main(): const value = 12

    """)
    compile_source(source, 'Main')


def test_syntax_5():
    source = dedent("""\
    template Main(A):
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_6():
    source = dedent("""\
    template Main(A, B):
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_7():
    source = dedent("""\
    template Main(A, B, *C):
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_8():
    source = dedent("""\
    template Main(A, B: 12):
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_9():
    source = dedent("""\
    template Main(A, B: 12, *C):
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_10():
    source = dedent("""\
    template Main(A=None):
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_11():
    source = dedent("""\
    template Main(A, B=None):
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_12():
    source = dedent("""\
    template Main(A, B=None, *C):
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_13():
    source = dedent("""\
    template Main(A, B: 12, C=None):
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_14():
    source = dedent("""\
    template Main(A, B: 12, C=None, *D):
        pass

    """)
    compile_source(source, 'Main')


def test_syntax_15():
    source = dedent("""\
    template Main(A, B, C):
        Field:
            pass
        PushButton:
            pass

    """)
    compile_source(source, 'Main')


def test_syntax_16():
    source = dedent("""\
    template Other(*Args):
        Slider:
            pass

    template Main(A, B, C):
        Field:
            pass
        PushButton:
            pass
        Other(A, B, C):
            pass

    """)
    compile_source(source, 'Main')


def test_syntax_17():
    source = dedent("""\
    template Other(*Args):
        Slider:
            pass

    template Main(A, B, C):
        Field:
            pass
        PushButton:
            pass
        Other(A, B, C): a:
            pass

    """)
    compile_source(source, 'Main')


def test_syntax_18():
    source = dedent("""\
    template Other(*Args):
        Slider:
            pass

    template Main(A, B, C):
        Field:
            pass
        PushButton:
            pass
        Other(A, B, C): a, b, c:
            pass

    """)
    compile_source(source, 'Main')


def test_syntax_19():
    source = dedent("""\
    template Other(*Args):
        Slider:
            pass

    template Main(A, B, C):
        Field:
            pass
        PushButton:
            pass
        Other(A, B, C): a, *b:
            pass

    """)
    compile_source(source, 'Main')


def test_syntax_20():
    source = dedent("""\
    template Other(*Args):
        Slider:
            pass

    template Main(A, B, C):
        Field:
            pass
        PushButton:
            pass
        Other(A, B, C): *all:
            pass

    """)
    compile_source(source, 'Main')


#------------------------------------------------------------------------------
# Bad Template Syntax
#------------------------------------------------------------------------------
def test_bad_syntax_1():
    source = dedent("""\
    template Main()
        pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_2():
    source = dedent("""\
    template Main() pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_3():
    source = dedent("""\
    template Main:
        pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_4():
    source = dedent("""\
    template Main: pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_5():
    source = dedent("""\
    template Main():
        const value

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_6():
    source = dedent("""\
    template Main():
        const value 12

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_7():
    source = dedent("""\
    template Main():
        attr value

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_8():
    source = dedent("""\
    template Main():
        event value

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_9():
    source = dedent("""\
    template Main():
        alias value

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_10():
    source = dedent("""\
    template Main(A B):
        pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_11():
    source = dedent("""\
    template Main(A=None, B):
        pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_12():
    source = dedent("""\
    template Main(A, B=None, C):
        pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_13():
    source = dedent("""\
    template Main(*C, A)
        pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_14():
    source = dedent("""\
    template Main(*C, A=None)
        pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_15():
    source = dedent("""\
    template Main():
        Foo(): a

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_16():
    source = dedent("""\
    template Main():
        Foo(): a, b

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_17():
    source = dedent("""\
    template Main():
        Foo(): a, *c

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_18():
    source = dedent("""\
    template Main():
        Field: a: pass
        Foo(): a: pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_19():
    source = dedent("""\
    template Main(Arg):
        const Arg = 12

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


def test_bad_syntax_20():
    source = dedent("""\
    template Main(Arg):
        const Args = 12
        Field: Args: pass

    """)
    with pytest.raises(SyntaxError):
        compile_source(source, 'Main')


#------------------------------------------------------------------------------
# Template Instantiation
#------------------------------------------------------------------------------
def test_instantiation_1():
    source = dedent("""\
    from enaml.widgets.api import *

    template Main():
        Field: pass

    """)
    from enaml.widgets.api import Field
    main = compile_source(source, 'Main')
    items = main()()
    assert len(items) == 1
    assert all(isinstance(item, Field) for item in items)


def test_instantiation_2():
    source = dedent("""\
    from enaml.widgets.api import *

    template Main():
        Field: pass
        Field: pass
        Field: pass

    """)
    from enaml.widgets.api import Field
    main = compile_source(source, 'Main')
    items = main()()
    assert len(items) == 3
    assert all(isinstance(item, Field) for item in items)


def test_instantiation_3():
    source = dedent("""\
    from enaml.widgets.api import *

    template Main(Text):
        Field: text = Text

    """)
    main = compile_source(source, 'Main')
    field = main('foo')()[0]
    assert field.text == 'foo'


def test_instantiation_4():
    source = dedent("""\
    template Main(Content):
        Content: pass

    """)
    from enaml.widgets.api import Field
    main = compile_source(source, 'Main')
    item = main(Field)()[0]
    assert isinstance(item, Field)


def test_instantiation_5():
    source = dedent("""\
    template Main(Content):
        Content:
            text = 'foo'

    """)
    from enaml.widgets.api import Field
    main = compile_source(source, 'Main')
    item = main(Field)()[0]
    assert item.text == 'foo'


def test_instantiation_6():
    source = dedent("""\
    template ForEach(N, Item):
        ForEach(N - 1, Item):
            pass
        Item:
            pass

    template ForEach(N: 0, Item):
        pass

    template Main(N, Item):
        ForEach(N, Item):
            pass

    """)
    from enaml.widgets.api import Field
    main = compile_source(source, 'Main')
    items = main(10, Field)()
    assert len(items) == 10
    assert all(isinstance(item, Field) for item in items)


def test_instantiation_7():
    source = dedent("""\
    from enaml.widgets.api import *

    template Main(Content):
        Container:
            alias content
            Content: content:
                pass

    """)
    from enaml.widgets.api import Field
    main = compile_source(source, 'Main')
    item = main(Field)()[0]
    assert isinstance(item.content, Field)


def test_instantiation_8():
    source = dedent("""\
    from enaml.widgets.api import *

    template Main():
        Container:
            alias text: field.text
            Field: field:
                name = 'field'
                text = 'bar'

    """)
    main = compile_source(source, 'Main')
    item = main()()[0]
    field = item.find('field')
    assert field.text == 'bar'
    item.text = 'foo'
    assert field.text == 'foo'


def test_instantiation_9():
    source = dedent("""\
    from enaml.widgets.api import *

    template Main(Content):
        Label: pass

    template Main(Content: 12):
        Field: pass

    """)
    from enaml.widgets.api import Field, Label
    main = compile_source(source, 'Main')
    item = main(None)()[0]
    assert isinstance(item, Label)
    item = main(12)()[0]
    assert isinstance(item, Field)


def test_instantiation_10():
    source = dedent("""\
    from enaml.widgets.api import *

    template Spam():
        Field: pass
        Label: pass
        Field: pass

    enamldef Main(Window):
        alias a
        alias b
        alias c
        attr rest = rest
        Spam(): a, b, c:
            pass
        Spam(): *rest:
            pass

    """)
    from enaml.widgets.api import Field, Label
    main = compile_source(source, 'Main')()
    assert isinstance(main.a, Field)
    assert isinstance(main.b, Label)
    assert isinstance(main.c, Field)
    types = (Field, Label, Field)
    rtypes = tuple(type(r) for r in main.rest)
    assert rtypes == types


def test_instantiation_11():
    source = dedent("""\
    from enaml.widgets.api import *

    template Spam(Item=Field):
        Item: pass

    enamldef Main(Window):
        Spam():
            pass
        Spam(Label):
            pass

    """)
    from enaml.widgets.api import Field, Label
    main = compile_source(source, 'Main')()
    types = (Field, Label)
    rtypes = tuple(type(child) for child in main.children)
    assert rtypes == types


def test_instantiation_12():
    source = dedent("""\
    template Unroll(Item, *Items):
        Item: pass
        Unroll(*Items): pass

    template Unroll():
        pass

    """)
    from enaml.widgets.api import Field
    Unroll = compile_source(source, 'Unroll')
    items = Unroll(Field, Field, Field, Field, Field)()
    assert len(items) == 5


def test_instantiation_13():
    source = dedent("""\
    from enaml.widgets.api import *

    template Unroll(First, Second=Label, *Rest):
        First: pass
        Second: pass
        Unroll(*Rest): pass

    template Unroll():
        pass

    """)
    from enaml.widgets.api import Field, Label
    Unroll = compile_source(source, 'Unroll')
    items = Unroll(Field, Field, Field, Field, Field)()
    assert len(items) == 6
    assert isinstance(items[-1], Label)


def test_instantiation_14():
    source = dedent("""\
    from enaml.widgets.api import *

    template Other(Content):
        Content:
            pass

    template Invoke(Item, Arg):
        Item(Arg):
            pass

    template Main(Which):
        Invoke(Other, Which):
            pass

    """)
    from enaml.widgets.api import Field
    Main = compile_source(source, 'Main')
    item = Main(Field)()[0]
    assert isinstance(item, Field)


def test_instantiation_15():
    source = dedent("""\
    from enaml.widgets.api import *

    template Main():
        Field: pass
        Field: pass
        Field: pass

    """)
    from enaml.core.api import Declarative
    Main = compile_source(source, 'Main')
    parent = Declarative()
    Main()(parent)
    assert len(parent.children) == 3


def test_instantiation_16():
    source = dedent("""\
    template Main():
        const Value = 15

    """)
    Main = compile_source(source, 'Main')
    assert Main().Value == 15


def test_instantiation_17():
    source = dedent("""\
    template Main():
        const Value = 15

    """)
    Main = compile_source(source, 'Main')
    assert Main() is Main()


# regression: https://github.com/nucleic/enaml/issues/78
def test_instantiation_18():
    source = dedent("""\
    from enaml.widgets.api import *

    template Foo():
        Field:
            placeholder = 'foo'

    enamldef Main(Window):
        Container:
            Foo(): f:
                f.text = f.placeholder
    """)
    main = compile_source(source, 'Main')()
    field = main.children[0].children[0]
    assert field.text == u'foo'


#------------------------------------------------------------------------------
# Bad Template Instantiation
#------------------------------------------------------------------------------
def test_bad_instantiation_1():
    source = dedent("""\
    from enaml.widgets.api import *

    template Other():
        Boo: pass

    enamldef Main(Window):
        Other(): pass

    """)
    with pytest.raises(NameError):
        compile_source(source, 'Main')


def test_bad_instantiation_2():
    source = dedent("""\
    from enaml.widgets.api import *

    template Other(A, B, C):
        Field: pass

    enamldef Main(Window):
        Other(): pass

    """)
    with pytest.raises(TypeError):
        compile_source(source, 'Main')


def test_bad_instantiation_3():
    source = dedent("""\
    template Other(*A):
        pass

    template Other():
        pass

    """)
    with pytest.raises(TypeError):
        compile_source(source, 'Main')


def test_bad_instantiation_4():
    source = dedent("""\
    template Other(A):
        pass

    template Other(A):
        pass

    """)
    with pytest.raises(TypeError):
        compile_source(source, 'Main')


def test_bad_instantiation_5():
    source = dedent("""\
    from enaml.widgets.api import *

    template Other(A, B: 12):
        pass

    template Other(A: 0, B):
        pass

    enamldef Main(Window):
        Other(0, 12):
            pass

    """)
    with pytest.raises(TypeError):
        compile_source(source, 'Main')


def test_bad_instantiation_6():
    source = dedent("""\
    from enaml.widgets.api import *

    template Foo():
        Field: pass
        Field: pass
        Field: pass

    enamldef Main(Window):
        Foo(): a:
            pass

    """)
    with pytest.raises(ValueError):
        compile_source(source, 'Main')


def test_bad_instantiation_7():
    source = dedent("""\
    from enaml.widgets.api import *

    template Foo():
        Field: pass
        Field: pass
        Field: pass

    enamldef Main(Window):
        Foo(): a, b:
            pass

    """)
    with pytest.raises(ValueError):
        compile_source(source, 'Main')


def test_bad_instantiation_8():
    source = dedent("""\
    from enaml.widgets.api import *

    template Foo():
        Field: pass
        Field: pass
        Field: pass

    enamldef Main(Window):
        Foo(): a, b, c, d:
            pass

    """)
    with pytest.raises(ValueError):
        compile_source(source, 'Main')
