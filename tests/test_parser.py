#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import pytest
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
def test_async_await_before_if():
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
    for compile_fn in (compile_py, compile_enaml):
        f = compile_fn(source, 'function')
        query = {'some': 'object'}
        r = run_async(f(query))
        assert r == query


@pytest.mark.skipif(not IS_PY3, reason="Async is python 3 only")
def test_async_await_after_if():
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
    
    for compile_fn in (compile_py, compile_enaml):
        f = compile_fn(source, 'function')
        loop = asyncio.get_event_loop()
        query = {'some': 'object'}
        r = run_async(f(query))
        assert r == query
