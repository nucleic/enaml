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
from enaml.compat import IS_PY3, exec_
from utils import compile_source as compile_enaml

if IS_PY3:
    import asyncio


def compile_py(source, item, filename='<test>', namespace=None):
    """ Like comple_source but python uses the parser """
    code = compile(source, filename, 'exec')
    namespace = namespace or {}
    exec_(code, namespace)
    return namespace[item]


def run_async(task):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(task)


@pytest.mark.skipif(not IS_PY3, reason="Async is python 3 only")
@pytest.mark.parametrize('compile_fn', [compile_py, compile_enaml])
def test_async_await_before_if(compile_fn):
    """Async function with if statement

    """
    source = dedent("""
    
    async def fetch(query):
        return query
    
    async def function(query):
        result = await fetch(query)
        if not query:
            return
        return result

    """)
    # Ensure it's valid 
    f = compile_fn(source, 'function')
    query = {'some': 'object'}
    r = run_async(f(query))
    assert r == query


@pytest.mark.skipif(not IS_PY3, reason="Async is python 3 only")
@pytest.mark.parametrize('compile_fn', [compile_py, compile_enaml])
def test_async_await_after_if(compile_fn):
    """Async function with await after if statement

    """
    source = dedent("""
    
    async def fetch(query):
        return query
    
    async def function(query):
        if not query:
            return
        result = await fetch(query)
        return result

    """)
    # Ensure it's valid
    
    f = compile_fn(source, 'function')
    loop = asyncio.get_event_loop()
    query = {'some': 'object'}
    r = run_async(f(query))
    assert r == query


def test_syntax_error(tmpdir):
    """ Test that a syntax error retains the path to the file
    
    """
    test_module_path = os.path.join(tmpdir, 'view.enaml')
    
    with open(os.path.join(tmpdir, 'test_main.enaml'), 'w') as f:
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
        sys.path.append(tmpdir)
        with enaml.imports():
            from test_main import MyWindow
        assert False, "Should raise a syntax error"
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        lines = tb.strip().split("\n")
        assert 'File "{}", line 5'.format(test_module_path) in lines[-4]
    finally:
        sys.path.remove(tmpdir)
