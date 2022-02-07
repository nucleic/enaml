#------------------------------------------------------------------------------
# Copyright (c) 2021, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
"""Test for the code generator."""
import ast
import pytest

from enaml.core.code_generator import CodeGenerator


# Since we cannot have a return outside a function I am not sure we can ever
# encounter a non-implicit return opcode.
@pytest.mark.parametrize("source, return_on_lines", [
    ("pass", []),
    ("if a:\n    print("")", []),
    ("for i in range(10):\n    i", []),
    ("with open(f) as f:\n   print(f.readlines())", []),
])
def test_python_block_insertion(source, return_on_lines):
    cg = CodeGenerator()
    cg.insert_python_block(ast.parse(source))
    for i in cg.code_ops:
        if getattr(i, "name", "") == "RETURN_VALUE":
            assert i.lineno in return_on_lines
    cg.to_code()
