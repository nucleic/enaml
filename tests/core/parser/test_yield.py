#------------------------------------------------------------------------------
# Copyright (c) 2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import sys
import ast
from textwrap import dedent

import pytest

from enaml.core.parser import parse

from .test_parser import validate_ast

TEST_SOURCE = {
    'yield': r"""
    def f():
        yield
    """,
    'yield a': r"""
    def f():
        yield a
    """,
    'yield a, (b, c)': r"""
    def f():
        yield a, (b, c)
    """,
    'yield from a': r"""
    def f():
        yield from a
    """
}

TEST_SOURCE_38 = {
    'yield a, *b': r"""
    def f():
        yield a, *b
    """
}

@pytest.mark.parametrize('desc',
    list(TEST_SOURCE) + list(TEST_SOURCE_38) if sys.version_info >= (3, 8) else []
)
def test_return_stmt(desc):
    """Test that we produce valid ast use of the := walrus operator.

    """
    src = dedent(TEST_SOURCE.get(desc, TEST_SOURCE_38.get(desc))).strip()
    print(src)
    # Ensure it's valid
    py_ast = ast.parse(src)
    enaml_ast = parse(src).body[0].ast
    validate_ast(py_ast.body[0], enaml_ast.body[0], True)
