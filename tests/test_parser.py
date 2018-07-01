#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import sys
import enaml
import pytest
import traceback
from textwrap import dedent

def test_syntax_error_traceback_correct_path(tmpdir):
    """ Test that a syntax error retains the path to the file
    
    """
    test_module_path = os.path.join(tmpdir.strpath, 'view.enaml')
    
    with open(os.path.join(tmpdir.strpath, 'test_main.enaml'), 'w') as f:
        f.write(dedent("""
        from enaml.widgets.api import Window, Container, Label
        from view import CustomView

        enamldef MyWindow(Window): main:
            CustomView:
                pass

        """))
    
    with open(test_module_path, 'w') as f:
        f.write(dedent("""
        from enaml.widgets.api import Container, Label

        enamldef CustomLabel(Container):
            Label # : missing intentionally
                text = "Hello world"

        """))
    
    try:
        sys.path.append(tmpdir.strpath)
        with enaml.imports():
            from test_main import MyWindow
        assert False, "Should raise a syntax error"
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        lines = tb.strip().split("\n")
        assert 'File "{}", line 5'.format(test_module_path) in lines[-4]
    finally:
        sys.path.remove(tmpdir.strpath)
