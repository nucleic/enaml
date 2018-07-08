#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys
import ast
import pytest

from enaml.core.parser import parse

from .test_parser import validate_ast

TEST_SOURCE = {
    'f-string single value': r"""
    a = f'test {a:d}'
    """,
    'f-string multiple values': r"""
    a = f'test {a:g}, {b}'
    """,
    'f-string split 1': r"""
    a = (f'{r}' '{t:s}')
    """,
    'f-string split 2': r"""
    a = ('{r}' f'{t:s}')
    """,
    'f-string raw string': r"""
    a = rf'{a}\n'
    """,
    'f-string raw string 2': r"""
    a = fr'{a}\n'
    """,
}
for k, v in list(TEST_SOURCE.items()):
    TEST_SOURCE[k.replace('f-', 'F-')] = v.replace("f'", "F'")
    if "rf'" in v:
        TEST_SOURCE[k.replace('raw', 'RAW')] = v.replace("rf'", "Rf'")
        TEST_SOURCE[k.replace('f-', 'F-').replace('raw', 'RAW')] =\
            v.replace("rf'", "RF'")
    if "fr'" in v:
        TEST_SOURCE[k.replace('raw', 'RAW')] = v.replace("fr'", "fR'")
        TEST_SOURCE[k.replace('f-', 'F-').replace('raw', 'RAW')] =\
            v.replace("fr'", "FR'")


@pytest.mark.skipif(sys.version_info < (3, 6), reason='Requires Python 3.6')
@pytest.mark.parametrize('desc', TEST_SOURCE.keys())
def test_f_strings(desc):
    """Async function with await list comp statement
    """
    src = TEST_SOURCE[desc].strip()
    print(src)
    # Ensure it's valid
    py_ast = ast.parse(src)
    enaml_ast = parse(src).body[0].ast
    validate_ast(py_ast.body[0], enaml_ast.body[0], True)
