# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from ast import literal_eval
from textwrap import dedent

from utils import compile_source


def test_unicode_literal():
    source = dedent("""\
    from enaml.widgets.api import Window

    enamldef MyWindow(Window): win:
        attr test = u'I do unicode characters: αΨγ 😀⏰🏔 𠁒𠁝𠁖'
    """)
    myWindow = compile_source(source, 'MyWindow')()
    unicode_literal = u'I do unicode characters: αΨγ 😀⏰🏔 𠁒𠁝𠁖'
    assert unicode_literal == myWindow.test


def test_unicode_escape_literal():
    source = dedent("""\
    from enaml.widgets.api import Window

    enamldef MyWindow(Window): win:
        attr test = u'I do unicode characters: \\U00020052'
    """)
    myWindow = compile_source(source, 'MyWindow')()
    unicode_escape_literal = u'I do unicode characters: \U00020052'
    assert unicode_escape_literal == myWindow.test


def test_raw_unicode_literal():
    source = dedent("""\
    from enaml.widgets.api import Window

    enamldef MyWindow(Window): win:
        attr test = r'I do unicode characters: \\U00020052'
    """)
    myWindow = compile_source(source, 'MyWindow')()
    raw_unicode_literal = r'I do unicode characters: \U00020052'
    assert raw_unicode_literal == myWindow.test


def test_bytes_literal():
    source = dedent("""\
    from enaml.widgets.api import Window

    enamldef MyWindow(Window): win:
        attr test = b'I also do bytes with\\nescapes: \\785 and \\x12'
        attr test2 = b'And handle unicode escapes \\u0320 gracefully'
    """)
    myWindow = compile_source(source, 'MyWindow')()
    bytes_literal = b'I also do bytes with\nescapes: \785 and \x12'
    assert bytes_literal == myWindow.test
    bytes_literal = b'And handle unicode escapes \u0320 gracefully'
    assert bytes_literal == myWindow.test2


def test_raw_bytes_literal1():
    source = dedent("""\
    from enaml.widgets.api import Window

    enamldef MyWindow(Window): win:
        attr test = br'I do bytes with\\nescapes'
    """)
    myWindow = compile_source(source, 'MyWindow')()
    raw_bytes_literal = br'I do bytes with\nescapes'
    assert raw_bytes_literal == myWindow.test

def test_raw_bytes_literal2():
    source = dedent("""\
    from enaml.widgets.api import Window

    enamldef MyWindow(Window): win:
        attr test = rb'I do bytes with\\nescapes'
    """)
    myWindow = compile_source(source, 'MyWindow')()
    raw_bytes_literal = literal_eval(r"rb'I do bytes with\nescapes'")
    assert raw_bytes_literal == myWindow.test

def test_unicode_identifier():
    source = dedent("""\
    from enaml.widgets.api import Window

    enamldef MyWindow(Window): win:
        attr 𠁒 = 'test'
        # Check we do not mistake this for an invalid identifier
        attr a = 1.e6
    """)
    myWindow = compile_source(source, 'MyWindow')()
    exec("𠁒 = 'test'")
    assert locals()['𠁒'] == getattr(myWindow, """𠁒""")


if __name__ == '__main__':
    test_unicode_literal()
    test_unicode_escape_literal()
    test_raw_unicode_literal()
    test_bytes_literal()
    test_raw_bytes_literal1()
    test_raw_bytes_literal2()
    test_unicode_identifier()
