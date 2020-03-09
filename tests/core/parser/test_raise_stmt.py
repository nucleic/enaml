#------------------------------------------------------------------------------
# Copyright (c) 2019, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#-----------------------------------------------------------------------------
import sys
import ast
from textwrap import dedent

import pytest
from enaml.core.parser import parse

from .test_parser import validate_ast


def test_raise_exception():
    """Test raising an exception.

    """
    src = """raise Exception()"""
    py_ast = ast.parse(src).body[0]
    enaml_ast = parse(src).body[0].ast.body[0]
    validate_ast(py_ast, enaml_ast, True)


def test_reraise_exception():
    """Test raising an exception.

    """
    src = dedent("""
    try:
        a = ""/0
    except:
        raise
    """)
    py_ast = ast.parse(src).body[0]
    enaml_ast = parse(src).body[0].ast.body[0]
    validate_ast(py_ast, enaml_ast, True)


@pytest.mark.skipif(sys.version_info < (3,), reason='Requires Python 3')
def test_raise_exception_with_cause():
    """Test that we parse properly functions with a return type annotation.

    """
    src = dedent("""
    try:
        a = ""/0
    except Exception as e:
        raise Exception() from e
    """)
    py_ast = ast.parse(src).body[0]
    enaml_ast = parse(src).body[0].ast.body[0]
    validate_ast(py_ast, enaml_ast, True)
