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
    ':= in expr': r"""
    a = (b := 1)
    """,
    ':= in tuple': r"""
    a = (2, b := 1)
    """,
    ':= in list': r"""
    a = [2, b := 1]
    """,
    ':= in if': r"""
    if b := 1:
        pass
    """,
    ':= in elif': r"""
    a = 0
    if a:
        pass
    elif b := 1:
        pass
    """,
    ':= in while': r"""
    while b := 1:
        pass
    """,
    ':= in function argument': r"""
    f(a, b := c or None)
    """
}


@pytest.mark.skipif(sys.version_info < (3, 8), reason='Requires Python 3.8')
@pytest.mark.parametrize('desc', TEST_SOURCE.keys())
def test_walrus_operator(desc):
    """Test that we produce valid ast use of the := walrus operator.

    """
    src = dedent(TEST_SOURCE[desc]).strip()
    print(src)
    # Ensure it's valid
    py_ast = ast.parse(src)
    enaml_ast = parse(src).body[0].ast
    validate_ast(py_ast.body[0], enaml_ast.body[0], True)


TEST_BAD_SOURCE = {
    ':= in while': r"""
    while 2 := 1:
        pass
    """,
    ':= in function argument': r"""
    f(a, 2 := c or None)
    """
}

@pytest.mark.skipif(sys.version_info < (3, 8), reason='Requires Python 3.8')
@pytest.mark.parametrize('desc', TEST_BAD_SOURCE.keys())
def test_invalid_walrus_operator(desc):
    """Test that we produce valid ast use of the := walrus operator.

    """
    src = dedent(TEST_BAD_SOURCE[desc]).strip()
    print(src)
    with pytest.raises(SyntaxError):
        enaml_ast = parse(src).body[0].ast
