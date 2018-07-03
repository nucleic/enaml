#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys
import ast
from textwrap import dedent
import pytest

from enaml.core.parser import parse

from .test_parser import validate_ast

FUNC_TEMPLATE =\
"""
import asyncio

async def fetch(query):
    return query

{}
"""

TEST_SOURCE = {
    'await': """
    async def function(queries):
        r =  await query()
        return r
    """,
    'await if': """
    async def function(query):
        result = await fetch(query)
        if not query:
            return
        return result
    """,
    'if await': """
    async def function(query):
        if not query:
            return
        result = await fetch(query)
        return result
    """,
    'await future': """
    async def function(query):
        f = fetch(query)
        await f
        return result
    """,
    'await subscript': """
    async def function(query):
        tasks = [fetch(query)]
        await tasks[0]
        return result
    """,
    'await attr': """
    async def function(query):
        class API:
            search = fetch
        api = API()
        await api.fetch(query)
        return result
    """,
    'await list comp': """
    async def function(queries):
        result = [await fetch(q) for q in queries]
        return result
    """,
    'await dict comp': """
    async def function(queries):
        result = {i:await fetch(q) for i, q in enumerate(queries)}
        return result
    """,
    'async for': """
    async def function(queries):
        results = []
        async for r in fetch(queries):
            results.append(r)
        return result
    """,
    'async for or': """
    async def function(queries):
        results = []
        async for r in queries or fetch(queries):
            results.append(r)
        return result
    """,
    'async for comp': """
    async def function(queries):
        results = []
        async for r in [f for f in fetch(queries)]:
            results.append(r)
        return result
    """,
    'async for or comp': """
    async def function(queries):
        results = []
        async for r in queries or [f for f in fetch(queries)]:
            results.append(r)
        return result
    """,
    'async with': """
    async def function(query):
        lock = asyncio.lock()
        async with lock:
            result = await fetch(query)
        return result
    """,
}

if sys.version_info >= (3, 6):
    TEST_SOURCE.update({
        'async for list comp': """
        async def function(queries):
            result = [r async for r in fetch(q)]
            return result
        """,
        'async for if list comp': """
        async def function(queries):
            result = [r async for r in fetch(queries) if r]
            return result
        """,
    })

if sys.version_info < (3, 7):
    TEST_SOURCE.update({
        'async not keyword': """
        def function(queries):
            async = False
            return queries
        """,
        'await not keyword': """
        def function(queries):
            await = False
            return queries
        """,
    })


@pytest.mark.skipif(sys.version_info < (3, 5), reason='Requires Python 3.5')
@pytest.mark.parametrize('desc', TEST_SOURCE.keys())
def test_async(desc):
    """Async function with await list comp statement
    """
    src = FUNC_TEMPLATE.format(dedent(TEST_SOURCE[desc]))
    # Ensure it's valid 
    py_ast = ast.parse(src)
    enaml_ast = parse(src).body[0].ast
    validate_ast(py_ast.body[0], enaml_ast.body[0], True)
    validate_ast(py_ast.body[1], enaml_ast.body[1], True)
    validate_ast(py_ast.body[2], enaml_ast.body[2], True)
