#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#-----------------------------------------------------------------------------
import sys
import ast

import pytest
from enaml.core.parser import parse

from .test_parser import validate_ast

FUNC_TEMPLATE =\
"""def f({}):
    pass
"""


POS_ARG_TEMP = ['a',
                'a=1',
                'a, b',
                'a, b=1',
                'a=1, b=2']


SIGNATURES = POS_ARG_TEMP[:]
for suffix in (',', ', *args', ', **kwargs', ', *args, **kwargs'):
    SIGNATURES.extend([s + suffix for s in POS_ARG_TEMP])

if sys.version_info[0] == 2:
    tuple_unpacking = ['(a, b)',
                       '(a, b)=(1, 2)',
                       '(a, b), c',
                       '(a, b), c=3',
                       '(a, b)=(1, 2), c=3']
    for suffix in (',', ', *args', ', **kwargs', ', *args, **kwargs'):
        SIGNATURES.extend([s + suffix for s in tuple_unpacking])

else:
    pos = [''] + [s.replace('a', 'c').replace('b', 'd') + ', '
                  for s in POS_ARG_TEMP]
    kw_only = [star_arg + s
               for s in POS_ARG_TEMP for star_arg in ('*, ', '*args, ')]
    for kw in kw_only:
        for suffix in ('', ', **kwargs'):
            SIGNATURES.extend([p + kw + suffix for p in pos])

    # annotated signatures
    pos = [''] + [s.replace('a', 'a: int') for s in POS_ARG_TEMP]
    no_kw_only = [',', ', *args', ', **kwargs', ', *args, **kwargs',
                  ', *args: int', ', **kwargs: int',
                  ', *args: int, **kwargs', ', *args, **kwargs: int',
                  ', *args: int, **kwargs: int']
    kw_only = [s.replace('b', 'b: int') for s in kw_only]
    for kw in no_kw_only:
        SIGNATURES.extend([p + kw for p in pos if p != '' and kw != ','])
    for kw in kw_only:
        for s in ('', ', **kwargs', ', **kwargs: int'):
            SIGNATURES.extend([p + ',' + kw + s if p else kw + s for p in pos])


@pytest.mark.parametrize('signature', SIGNATURES)
def test_func_definition_parsing(signature):
    """Test parsing all possible function signatures.

    """
    src = FUNC_TEMPLATE.format(signature)
    py_ast = ast.parse(src).body[0]
    enaml_ast = parse(src).body[0].ast.body[0]
    validate_ast(py_ast, enaml_ast, True)


@pytest.mark.skipif(sys.version_info < (3,), reason='Requires Python 3')
def test_func_return_annotation_parsing():
    """Test that we parse properly functions with a return type annotation.

    """
    src = "def f() -> int:\n    pass"
    py_ast = ast.parse(src).body[0]
    enaml_ast = parse(src).body[0].ast.body[0]
    validate_ast(py_ast, enaml_ast, True)
