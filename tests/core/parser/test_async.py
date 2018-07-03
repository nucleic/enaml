
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
    'await multiple': """
    async def function(query):
        result = await fetch(query)
        result = await fetch(query)
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
    'await for': """
    async def function(queries):
        results = []
        async for r in fetch(queries):
            results.append(r)
        return result
    """,
    'await for or': """
    async def function(queries):
        results = []
        async for r in queries or fetch(quieries):
            results.append(r)
        return result
    """,
    'await for comp': """
    async def function(queries):
        results = []
        async for r in [f for f in fetch(quieries)]:
            results.append(r)
        return result
    """,
    'await for or comp': """
    async def function(queries):
        results = []
        async for r in queries or [f for f in fetch(quieries)]:
            results.append(r)
        return result
    """,
}


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

