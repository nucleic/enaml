#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from textwrap import dedent

from nose.tools import raises

from utils import compile_source


#------------------------------------------------------------------------------
# Alias Syntax
#------------------------------------------------------------------------------
def test_syntax_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


def test_syntax_2():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pc: pb
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


def test_syntax_3():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pc: pb.text
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


#------------------------------------------------------------------------------
# Bad Alias Syntax
#------------------------------------------------------------------------------
@raises(SyntaxError)
def test_bad_syntax_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb.text
        PushButton: pb:
            text = 'spam'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


@raises(SyntaxError)
def test_bad_syntax_2():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb text
        PushButton: pb:
            text = 'spam'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


@raises(SyntaxError)
def test_bad_syntax_3():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb: pb text
        PushButton: pb:
            text = 'spam'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


#------------------------------------------------------------------------------
# Alias References
#------------------------------------------------------------------------------
def test_ref_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    main = compile_source(source, 'Main')()
    button = main.find('button')
    content = main.find('content')
    assert content.pb is button


def test_ref_2():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb: pb
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    main = compile_source(source, 'Main')()
    button = main.find('button')
    content = main.find('content')
    assert content.pb is button


def test_ref_3():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias foo: pb
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    main = compile_source(source, 'Main')()
    button = main.find('button')
    content = main.find('content')
    assert content.foo is button


def test_ref_4():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb: pb.text
        PushButton: pb:
            text = 'spam'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    main = compile_source(source, 'Main')()
    content = main.find('content')
    assert content.pb == 'spam'


def test_ref_5():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias slider
        Slider: slider:
            name = 'slider'

    enamldef Content(Container):
        alias other
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    main = compile_source(source, 'Main')()
    slider = main.find('slider')
    content = main.find('content')
    assert content.other.slider is slider


def test_ref_6():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias value: slider.value
        Slider: slider:
            value = 50

    enamldef Content(Container):
        alias other
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    main = compile_source(source, 'Main')()
    content = main.find('content')
    assert content.other.value == 50


def test_ref_7():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias value: slider.value
        Slider: slider:
            value = 50

    enamldef Content(Container):
        alias value: other.value
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    main = compile_source(source, 'Main')()
    content = main.find('content')
    assert content.value == 50


def test_ref_8():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias slider
        Slider: slider:
            value = 50

    enamldef Content(Container):
        alias value: other.slider.value
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    main = compile_source(source, 'Main')()
    content = main.find('content')
    assert content.value == 50


#------------------------------------------------------------------------------
# Bad Alias Reference
#------------------------------------------------------------------------------
@raises(TypeError)
def test_bad_ref_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pc
        PushButton: pb:
            text = 'spam'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


@raises(TypeError)
def test_bad_ref_2():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pc: pd
        PushButton: pb:
            text = 'spam'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


@raises(TypeError)
def test_bad_ref_3():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pc: pb.tex
        PushButton: pb:
            text = 'spam'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


@raises(TypeError)
def test_bad_ref_4():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pc: pb.text.spam
        PushButton: pb:
            text = 'spam'

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


@raises(TypeError)
def test_bar_ref_5():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias value: slider.value
        Slider: slider:
            value = 50

    enamldef Content(Container):
        alias value: other.valued
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


@raises(TypeError)
def test_bad_ref_6():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias slider
        Slider: slider:
            value = 50

    enamldef Content(Container):
        alias value: other.slider.valsue
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            name = 'content'

    """)
    compile_source(source, 'Main')


#------------------------------------------------------------------------------
# Alias Binding
#------------------------------------------------------------------------------
def test_bind_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb: pb.text
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            pb = 'foo'

    """)
    main = compile_source(source, 'Main')()
    button = main.find('button')
    assert button.text == 'foo'


def test_bind_2():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias slider
        Slider: slider:
            name = 'slider'

    enamldef Content(Container):
        alias value: other.slider.value
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            value = 50

    """)
    main = compile_source(source, 'Main')()
    slider = main.find('slider')
    assert slider.value == 50


def test_bind_3():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias value: slider.value
        Slider: slider:
            name = 'slider'
            value = 50

    enamldef Content(Container):
        alias value: other.value
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            value = 42

    """)
    main = compile_source(source, 'Main')()
    slider = main.find('slider')
    assert slider.value == 42


#------------------------------------------------------------------------------
# Bad Alias Binding
#------------------------------------------------------------------------------
@raises(TypeError)
def test_bad_bind_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            pb = 'foo'

    """)
    compile_source(source, 'Main')


@raises(TypeError)
def test_bad_bind_2():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias text: pb.text
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            txt = 'foo'

    """)
    compile_source(source, 'Main')


#------------------------------------------------------------------------------
# Extended Alias Binding
#------------------------------------------------------------------------------
def test_ex_bind_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            pb.text = 'foo'

    """)
    main = compile_source(source, 'Main')()
    button = main.find('button')
    assert button.text == 'foo'


def test_ex_bind_2():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias slider
        Slider: slider:
            name = 'slider'

    enamldef Content(Container):
        alias value: other.slider
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            value.value = 50

    """)
    main = compile_source(source, 'Main')()
    slider = main.find('slider')
    assert slider.value == 50


def test_ex_bind_3():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias slider
        Slider: slider:
            name = 'slider'

    enamldef Content(Container):
        alias value: other
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            value.slider.value = 42

    """)
    main = compile_source(source, 'Main')()
    slider = main.find('slider')
    assert slider.value == 42


#------------------------------------------------------------------------------
# Bad Alias Binding
#------------------------------------------------------------------------------
@raises(TypeError)
def test_bad_ex_bind_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            pbd.text = 'foo'

    """)
    compile_source(source, 'Main')


@raises(TypeError)
def test_bad_ex_bind_2():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias pb
        PushButton: pb:
            name = 'button'

    enamldef Main(Window):
        Content:
            pb.txt = 'foo'

    """)
    compile_source(source, 'Main')


@raises(TypeError)
def test_bad_ex_bind_3():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Other(Container):
        alias slider
        Slider: slider:
            name = 'slider'

    enamldef Content(Container):
        alias value: other.slider
        Other: other:
            pass

    enamldef Main(Window):
        Content:
            value.val = 50

    """)
    compile_source(source, 'Main')


#------------------------------------------------------------------------------
# Alias Ordering
#------------------------------------------------------------------------------
def test_ordering():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        Field: field:
            alias this_text: field.text
        alias text: field.this_text

    enamldef Main(Window):
        Content:
            pass

    """)
    compile_source(source, 'Main')


#------------------------------------------------------------------------------
# Bad Alias Ordering
#------------------------------------------------------------------------------
@raises(TypeError)
def test_bar_ordering():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias text: field.this_text
        Field: field:
            alias this_text: field.text

    enamldef Main(Window):
        Content:
            pass

    """)
    compile_source(source, 'Main')


#------------------------------------------------------------------------------
# Bad Alias Override
#------------------------------------------------------------------------------
@raises(TypeError)
def test_bad_override_1():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias background
        Field: background:
            pass

    enamldef Main(Window):
        Content:
            pass

    """)
    compile_source(source, 'Main')


@raises(TypeError)
def test_bad_override_2():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias foo
        Field: foo:
            pass

    enamldef Content2(Content):
        alias foo: bar
        Field: bar:
            pass

    enamldef Main(Window):
        Content2:
            pass

    """)
    compile_source(source, 'Main')


@raises(TypeError)
def test_bad_override_3():
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Content(Container):
        alias foo
        Field: foo:
            pass

    enamldef Content2(Content):
        attr foo

    enamldef Main(Window):
        Content2:
            pass

    """)
    compile_source(source, 'Main')
