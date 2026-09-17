# ------------------------------------------------------------------------------
# Copyright (c) 2018-2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
import sys
import ast
import pytest

from enaml.core.parser import parse

from .test_parser import validate_ast

TEST_SOURCE = {
    "f-string single value": r"""
    a = f'test {a:d}'
    """,
    "f-string multiple values": r"""
    a = f'test {a:g}, {b}'
    """,
    "f-string split 1": r"""
    a = (f'{r}' '{t:s}')
    """,
    "f-string split 2": r"""
    a = ('{r}' f'{t:s}')
    """,
    "f-string raw string": r"""
    a = rf'{a}\n'
    """,
    "f-string raw string 2": r"""
    a = fr'{a}\n'
    """,
    "f-string debug value": r"""
    a = f'{a=}'
    """,
    "f-string debug value with format": r"""
    a = f'{a=:>10}'
    """,
    "f-string nested format spec": r"""
    a = f'{value:{width}}'
    """,
}
for k, v in list(TEST_SOURCE.items()):
    TEST_SOURCE[k.replace("f-", "F-")] = v.replace("f'", "F'")
    if "rf'" in v:
        TEST_SOURCE[k.replace("raw", "RAW")] = v.replace("rf'", "Rf'")
        TEST_SOURCE[k.replace("f-", "F-").replace("raw", "RAW")] = v.replace(
            "rf'", "RF'"
        )
    if "fr'" in v:
        TEST_SOURCE[k.replace("raw", "RAW")] = v.replace("fr'", "fR'")
        TEST_SOURCE[k.replace("f-", "F-").replace("raw", "RAW")] = v.replace(
            "fr'", "FR'"
        )


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11")
@pytest.mark.parametrize("desc", TEST_SOURCE.keys())
def test_f_strings(desc):
    """Test that we produce valid ast for f-strings."""
    src = TEST_SOURCE[desc].strip()
    print(src)
    # Ensure it's valid
    py_ast = ast.parse(src)
    enaml_ast = parse(src).body[0].ast
    validate_ast(py_ast.body[0], enaml_ast.body[0], True)


@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Requires Python 3.11",
)
@pytest.mark.parametrize("source", [("f'{\\}'"), ("('d'\nf'{\\}')")])
def test_reporting_errors_f_strings(source):
    """Test that we properly report error on f-string."""
    with pytest.raises(SyntaxError) as e:
        parse(source)

    assert "backslash" in e.value.args[0]


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11")
@pytest.mark.parametrize(
    "source",
    [
        "a = f'{x=}'",
        "a = f'{x=!r}'",
        "a = f'{x=:>10}'",
        "a = f'{value:{width}}'",
    ],
)
def test_debug_f_strings(source):
    """Test debug f-strings and nested format-spec parsing."""
    py_ast = ast.parse(source)
    enaml_ast = parse(source).body[0].ast
    validate_ast(py_ast.body[0], enaml_ast.body[0], True)


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11")
@pytest.mark.parametrize("source", ["f'{x!q}'", "f'{x!}'", "f'{x!foo}'"])
def test_invalid_fstring_conversion(source):
    """Reject invalid conversion characters in f-strings."""
    with pytest.raises(SyntaxError):
        parse(source)


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11")
@pytest.mark.parametrize(
    "source",
    [
        "try:\n    pass\nexcept* ValueError as e:\n    pass",
        "try:\n    pass\nexcept* ValueError:\n    pass\nelse:\n    pass",
    ],
)
def test_except_star_syntax(source):
    """Ensure Python 3.11 except* blocks are parsed like CPython."""
    py_ast = ast.parse(source)
    enaml_ast = parse(source).body[0].ast
    validate_ast(py_ast.body[0], enaml_ast.body[0], True)


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11")
@pytest.mark.parametrize(
    "source",
    [
        "match x:\n    case 0:\n        pass\n    case _:\n        pass",
        "match x:\n    case 1 | 2 if x > 0:\n        pass\n    case _:\n        pass",
        "match x:\n    case _ as y:\n        pass",
    ],
)
def test_match_syntax(source):
    """Ensure Python 3.11 match statements are parsed like CPython."""
    py_ast = ast.parse(source)
    enaml_ast = parse(source).body[0].ast
    validate_ast(py_ast.body[0], enaml_ast.body[0], True)


@pytest.mark.skipif(sys.version_info < (3, 15), reason="Requires Python 3.15")
@pytest.mark.parametrize("source", ["lazy import os", "lazy from math import sqrt"])
def test_lazy_import_syntax(source):
    """Ensure Python 3.15 lazy imports are parsed like CPython."""
    py_ast = ast.parse(source)
    enaml_ast = parse(source).body[0].ast
    validate_ast(py_ast.body[0], enaml_ast.body[0], True)


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11")
@pytest.mark.parametrize(
    "source",
    [
        "try:\n    pass\nexcept ValueError:\n    pass\nexcept* TypeError:\n    pass",
        "try:\n    pass\nexcept* ValueError:\n    pass\nexcept TypeError:\n    pass",
    ],
)
def test_invalid_except_star_mixing(source):
    """Reject mixing except and except* in the same try block."""
    with pytest.raises(SyntaxError):
        parse(source)


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11")
@pytest.mark.parametrize(
    "source",
    [
        "match x:\n    case 1 as _:\n        pass",
    ],
)
def test_invalid_match_pattern_target(source):
    """Reject invalid wildcard targets in match statements."""
    with pytest.raises(SyntaxError):
        parse(source)
