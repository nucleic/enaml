#------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from textwrap import dedent
from utils import compile_source


def test_tracer_load_attr():
    source = dedent("""\
    from atom.api import Atom, Str
    from enaml.widgets.api import Window, Container, Label

    class Model(Atom):
        value = Str("foo")

    enamldef Main(Window):
        alias lbl
        attr model = Model()
        Container:
            Label: lbl:
                text << model.value
    """)
    Main = compile_source(source, 'Main')
    window = Main()
    assert window.lbl.text == "foo"
    window.model.value = "bar"
    assert window.lbl.text == "bar"


def test_tracer_call_func():
    source = dedent("""\
    from atom.api import Atom, Int
    from enaml.widgets.api import Window, Container, Label

    class Model(Atom):
        value = Int(1)

    enamldef Main(Window):
        alias lbl
        attr model = Model()
        Container:
            Label: lbl:
                text << str(model.value)
    """)
    Main = compile_source(source, 'Main')
    window = Main()
    assert window.lbl.text == "1"
    window.model.value = 2
    assert window.lbl.text == "2"


def test_tracer_binary_subscr():
    source = dedent("""\
    from atom.api import Atom, ContainerList
    from enaml.widgets.api import Window, Container, SpinBox

    class Model(Atom):
        items = ContainerList(default=[1])

    enamldef Main(Window):
        alias sb
        attr model = Model()
        Container:
            SpinBox: sb:
                value << model.items[0]
    """)
    Main = compile_source(source, 'Main')
    window = Main()
    window.model.items[0] = 3
    assert window.sb.value == 3


def test_inverter_load_attr():
    source = dedent("""\
    from atom.api import Atom, Int
    from enaml.widgets.api import Window, Container, Label, SpinBox

    class Model(Atom):
        value = Int(0)

    enamldef Main(Window):
        alias sb
        attr model = Model()
        Container:
            SpinBox: sb:
                value := model.value
    """)
    Main = compile_source(source, 'Main')
    window = Main()
    assert window.sb.value == 0
    window.sb.value = 2
    assert window.model.value == 2
    window.model.value = 3
    assert window.sb.value == 3


def test_inverter_call_func():
    source = dedent("""\
    from atom.api import Atom, Int
    from enaml.widgets.api import Window, Container, Label, SpinBox

    class Model(Atom):
        value = Int(0)

    enamldef Main(Window):
        alias sb
        attr model = Model()
        Container:
            SpinBox: sb:
                value := getattr(model, "value")
    """)
    Main = compile_source(source, 'Main')
    window = Main()
    assert window.sb.value == 0
    window.sb.value = 2
    assert window.model.value == 2
    window.model.value = 3
    assert window.sb.value == 3


def test_inverter_binary_subscr():
    source = dedent("""\
    from atom.api import Atom, ContainerList
    from enaml.widgets.api import Window, Container, SpinBox

    class Model(Atom):
        items = ContainerList(default=[1])

    enamldef Main(Window):
        alias sb
        attr model = Model()
        Container:
            SpinBox: sb:
                value := model.items[0]
    """)
    Main = compile_source(source, 'Main')
    window = Main()
    assert window.sb.value == 1
    window.sb.value = 2
    assert window.model.items[0] == 2
    window.model.items[0] = 3
    assert window.sb.value == 3
