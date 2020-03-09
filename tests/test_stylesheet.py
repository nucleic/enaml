#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from textwrap import dedent

import pytest

from enaml.application import Application
from utils import compile_source


def test_setter_data():
    source = dedent("""\
    from enaml.styling import Setter

    enamldef MySetter(Setter):
        field = 'background'
        value = 'blue'

    """)
    setter = compile_source(source, 'MySetter')()
    assert setter.field == u'background'
    assert setter.value == u'blue'


def test_style_data():
    source = dedent("""\
    from enaml.styling import Style

    enamldef MyStyle(Style):
        element = 'PushButton'
        style_class = 'button'
        object_name = 'pb1'
        pseudo_class = 'pressed'
        pseudo_element = 'menu-indicator'

    """)
    style = compile_source(source, 'MyStyle')()
    assert style.element == u'PushButton'
    assert style.style_class == u'button'
    assert style.object_name == u'pb1'
    assert style.pseudo_class == u'pressed'
    assert style.pseudo_element == u'menu-indicator'


def test_style_setters():
    source = dedent("""\
    from enaml.core.declarative import Declarative
    from enaml.styling import Style, Setter

    enamldef MyStyle(Style):
        Setter:
            pass
        Declarative:
            pass
        Setter:
            pass
        Declarative:
            pass
        Setter:
            pass

    """)
    style = compile_source(source, 'MyStyle')()
    assert len(style.setters()) == 3


def test_stylesheet_styles():
    source = dedent("""\
    from enaml.core.declarative import Declarative
    from enaml.styling import StyleSheet, Style

    enamldef Sheet(StyleSheet):
        Style:
            pass
        Declarative:
            pass
        Style:
            pass
        Declarative:
            pass
        Style:
            pass

    """)
    sheet = compile_source(source, 'Sheet')()
    assert len(sheet.styles()) == 3


def test_element_selector():
    from enaml.styling import StyleCache
    source = dedent("""\
    from enaml.widgets.api import Window, Container, PushButton, Field
    from enaml.styling import StyleSheet, Style, Setter

    enamldef Sheet(StyleSheet):
        Style:
            element = 'PushButton'
            Setter:
                field = 'background'
                value = 'blue'

    enamldef SubButton(PushButton):
        pass

    enamldef Main(Window):
        alias button
        alias subbutton
        alias field
        Sheet:
            pass
        Container:
            PushButton: button:
                pass
            SubButton: subbutton:
                pass
            Field: field:
                pass

    """)
    main = compile_source(source, 'Main')()
    assert len(StyleCache.styles(main.button)) == 1
    assert len(StyleCache.styles(main.subbutton)) == 1
    assert len(StyleCache.styles(main.field)) == 0


def test_class_selector():
    from enaml.styling import StyleCache
    source = dedent("""\
    from enaml.widgets.api import Window, Container, PushButton
    from enaml.styling import StyleSheet, Style, Setter

    enamldef Sheet(StyleSheet):
        Style:
            style_class = 'button'
            Setter:
                field = 'background'
                value = 'blue'

    enamldef Main(Window):
        alias button
        alias other
        Sheet:
            pass
        Container:
            PushButton: button:
                style_class = 'button'
            PushButton: other:
                pass

    """)
    main = compile_source(source, 'Main')()
    assert len(StyleCache.styles(main.button)) == 1
    assert len(StyleCache.styles(main.other)) == 0


def test_name_selector():
    from enaml.styling import StyleCache
    source = dedent("""\
    from enaml.widgets.api import Window, Container, PushButton
    from enaml.styling import StyleSheet, Style, Setter

    enamldef Sheet(StyleSheet):
        Style:
            object_name = 'button'
            Setter:
                field = 'background'
                value = 'blue'

    enamldef Main(Window):
        alias button
        alias other
        Sheet:
            pass
        Container:
            PushButton: button:
                name = 'button'
            PushButton: other:
                style_class = 'button'

    """)
    main = compile_source(source, 'Main')()
    assert len(StyleCache.styles(main.button)) == 1
    assert len(StyleCache.styles(main.other)) == 0


def _assert_setters(item, values):
    from enaml.styling import StyleCache
    styles = StyleCache.styles(item)
    setters = [s.setters() for s in styles]
    setters = sum(setters, [])
    assert len(setters) == len(values)
    for setter, (field, value) in zip(setters, values):
        assert setter.field == field
        assert setter.value == value


def test_specificity():
    source = dedent("""\
    from enaml.widgets.api import Window, Container, PushButton, Field, Slider
    from enaml.styling import StyleSheet, Style, Setter

    enamldef Sheet(StyleSheet):
        Style:
            style_class = 'yellow'
            Setter:
                field = 'background'
                value = 'yellow'
        Style:
            object_name = 'button'
            Setter:
                field = 'background'
                value = 'green'
        Style:
            style_class = 'strong, bold'
            Setter:
                field = 'font-weight'
                value = 'bold'
        Style:
            element = 'Field'
            style_class = 'gray-text'
            Setter:
                field = 'color'
                value = 'gray'
        Style:
            element = 'PushButton'
            Setter:
                field = 'background'
                value = 'red'
        Style:
            Setter:
                field = 'background'
                value = 'blue'

    enamldef Main(Window):
        alias one
        alias two
        alias three
        alias four
        alias five
        alias six
        alias seven
        alias eight
        alias nine
        Sheet:
            pass
        Container:
            PushButton: one:
                pass
            Field: two:
                pass
            Slider: three:
                pass
            PushButton: four:
                style_class = 'yellow'
            PushButton: five:
                style_class = 'yellow bold'
            Slider: six:
                name = 'button'
            Field: seven:
                style_class = 'gray-text'
            Field: eight:
                name = 'button'
            PushButton: nine:
                name = 'button'
                style_class = 'gray-text yellow strong'

    """)

    main = compile_source(source, 'Main')()
    _assert_setters(main.one, (
        ('background', 'blue'),
        ('background', 'red'),
    ))
    _assert_setters(main.two, (
        ('background', 'blue'),
    ))
    _assert_setters(main.three, (
        ('background', 'blue'),
    ))
    _assert_setters(main.four, (
        ('background', 'blue'),
        ('background', 'red'),
        ('background', 'yellow'),
    ))
    _assert_setters(main.five, (
        ('background', 'blue'),
        ('background', 'red'),
        ('background', 'yellow'),
        ('font-weight', 'bold'),
    ))
    _assert_setters(main.six, (
        ('background', 'blue'),
        ('background', 'green'),
    ))
    _assert_setters(main.seven, (
        ('background', 'blue'),
        ('color', 'gray'),
    ))
    _assert_setters(main.eight, (
        ('background', 'blue'),
        ('background', 'green'),
    ))
    _assert_setters(main.nine, (
        ('background', 'blue'),
        ('background', 'red'),
        ('background', 'yellow'),
        ('font-weight', 'bold'),
        ('background', 'green'),
    ))


def test_cascade():
    source = dedent("""\
    from enaml.widgets.api import Window, Container, PushButton
    from enaml.styling import StyleSheet, Style, Setter

    enamldef Sheet1(StyleSheet):
        Style:
            style_class = 'yellow'
            Setter:
                field = 'background'
                value = 'yellow'
        Style:
            element = 'PushButton'
            Setter:
                field = 'background'
                value = 'red'

    enamldef Sheet2(StyleSheet):
        Style:
            style_class = 'cyan'
            Setter:
                field = 'background'
                value = 'cyan'
        Style:
            element = 'PushButton'
            Setter:
                field = 'background'
                value = 'green'

    enamldef Sheet3(StyleSheet):
        Style:
            style_class = 'magenta'
            Setter:
                field = 'background'
                value = 'magenta'
        Style:
            element = 'PushButton'
            Setter:
                field = 'background'
                value = 'blue'

    enamldef Main(Window):
        alias one
        alias two
        alias three
        alias four
        alias five
        alias six
        alias seven
        alias eight
        alias nine
        alias ten
        alias eleven
        Sheet2:
            pass
        Container:
            PushButton: one:
                pass
            PushButton: two:
                style_class = 'yellow'
            PushButton: three:
                style_class = 'cyan'
            PushButton: four:
                Sheet3:
                    pass
            PushButton: five:
                style_class = 'yellow'
                Sheet3:
                    pass
            PushButton: six:
                style_class = 'cyan'
                Sheet3:
                    pass
            PushButton: seven:
                style_class = 'magenta'
                Sheet3:
                    pass
            Container:
                Sheet3:
                    pass
                PushButton: eight:
                    pass
                PushButton: nine:
                    style_class = 'yellow'
                PushButton: ten:
                    style_class = 'cyan'
                PushButton: eleven:
                    style_class = 'magenta'

    def init():
        from enaml.application import Application
        app = Application()
        app.style_sheet = Sheet1()
        return Main()

    """)
    old_instance = None
    if Application.instance():
        old_instance = Application._instance
        Application._instance = None
    try:
        main = compile_source(source, 'init')()
        _assert_setters(main.one, (
            ('background', 'red'),
            ('background', 'green'),
        ))
        _assert_setters(main.two, (
            ('background', 'red'),
            ('background', 'yellow'),
            ('background', 'green'),
        ))
        _assert_setters(main.three, (
            ('background', 'red'),
            ('background', 'green'),
            ('background', 'cyan'),
        ))
        _assert_setters(main.four, (
            ('background', 'red'),
            ('background', 'green'),
            ('background', 'blue'),
        ))
        _assert_setters(main.five, (
            ('background', 'red'),
            ('background', 'yellow'),
            ('background', 'green'),
            ('background', 'blue'),
        ))
        _assert_setters(main.six, (
            ('background', 'red'),
            ('background', 'green'),
            ('background', 'cyan'),
            ('background', 'blue'),
        ))
        _assert_setters(main.seven, (
            ('background', 'red'),
            ('background', 'green'),
            ('background', 'blue'),
            ('background', 'magenta'),
        ))
        _assert_setters(main.eight, (
            ('background', 'red'),
            ('background', 'green'),
            ('background', 'blue'),
        ))
        _assert_setters(main.nine, (
            ('background', 'red'),
            ('background', 'yellow'),
            ('background', 'green'),
            ('background', 'blue'),
        ))
        _assert_setters(main.ten, (
            ('background', 'red'),
            ('background', 'green'),
            ('background', 'cyan'),
            ('background', 'blue'),
        ))
        _assert_setters(main.eleven, (
            ('background', 'red'),
            ('background', 'green'),
            ('background', 'blue'),
            ('background', 'magenta'),
        ))
    finally:
        Application._instance = old_instance


def _clear_cache():
    from enaml.styling import StyleCache
    StyleCache._item_style_sheets.clear()
    StyleCache._item_styles.clear()
    StyleCache._style_sheet_items.clear()
    StyleCache._style_items.clear()
    StyleCache._queried_items.clear()
    StyleCache._toolkit_setters.clear()


def _cache_items_empty():
    from enaml.styling import StyleCache
    if StyleCache._item_style_sheets:
        return False
    if StyleCache._item_styles:
        return False
    if StyleCache._queried_items:
        return False
    return True


def _cache_styles_empty():
    from enaml.styling import StyleCache
    if StyleCache._style_sheet_items:
        return False
    if StyleCache._style_items:
        return False
    return True


def _cache_tk_empty():
    from enaml.styling import StyleCache
    if StyleCache._toolkit_setters:
        return False
    return True


def test_cache_1():
    from enaml.application import Application
    from enaml.styling import StyleCache
    source = dedent("""\
    from enaml.widgets.api import Window, Container, PushButton
    from enaml.styling import StyleSheet, Style, Setter

    enamldef Sheet(StyleSheet):
        Style:
            element = 'PushButton'
            Setter:
                field = 'background'
                value = 'blue'

    enamldef Main(Window):
        alias button
        Sheet:
            pass
        Container:
            PushButton: button:
                pass

    """)
    _clear_cache()
    app = Application.instance()
    if app is not None:
        app.style_sheet = None
    main = compile_source(source, 'Main')()
    styles = StyleCache.styles(main.button)
    assert len(styles) == 1
    assert not _cache_items_empty()
    assert not _cache_styles_empty()
    main.destroy()
    assert _cache_items_empty()
    assert _cache_styles_empty()


def test_cache_2():
    from enaml.application import Application
    from enaml.styling import StyleCache
    source = dedent("""\
    from enaml.widgets.api import Window, Container, PushButton
    from enaml.styling import StyleSheet, Style, Setter

    enamldef Sheet(StyleSheet):
        Style:
            element = 'PushButton'
            Setter:
                field = 'background'
                value = 'blue'

    enamldef Main(Window):
        alias button
        Container:
            PushButton: button:
                pass

    def init():
        return Main(), Sheet()

    """)
    _clear_cache()
    main, sheet = compile_source(source, 'init')()
    app = Application.instance()
    if app is None:
        app = Application()
    app.style_sheet = sheet
    styles = StyleCache.styles(main.button)
    assert len(styles) == 1
    assert not _cache_items_empty()
    assert not _cache_styles_empty()
    main.destroy()
    assert _cache_items_empty()
    assert not _cache_styles_empty()
    sheet.destroy()
    assert _cache_styles_empty()
    assert app.style_sheet is None
