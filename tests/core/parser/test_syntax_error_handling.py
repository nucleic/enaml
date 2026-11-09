import ast
import sys

import pytest

from enaml.core.parser import parse


def parse_invalid_syntax(source, message, *, py_version=None, start=None, end=None):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=py_version)

    text = str(exc.value)
    messages = (message,) if isinstance(message, str) else message
    assert any(m.lower() in text.lower() for m in messages)

    if start is None:
        return

    assert exc.value.lineno == start[0]
    assert exc.value.offset == start[1]
    if end is not None:
        assert getattr(exc.value, "end_lineno", None) == end[0]
        if end[1] is not None:
            assert getattr(exc.value, "end_offset", None) == end[1]


@pytest.mark.parametrize(
    "source, message",
    [
        ("(a 1)", "invalid syntax"),
        ("print 1", "Missing parentheses"),
        ("a if b", "expected 'else'"),
        (
            "f'{x!}'",
            (
                "missing conversion",
                "missing conversion character",
                "invalid conversion character",
            ),
        ),
        ("(a = 1)", "invalid syntax"),
    ],
)
def test_invalid_python_syntax_is_rejected(source, message):
    parse_invalid_syntax(source, message)


@pytest.mark.parametrize(
    "source, message",
    [
        ("x = f'{x!q}'", "invalid conversion"),
        (
            "match x:\n    case 0:\n        pass\n    case _ as y:\n        pass",
            "cannot use '_' as a target",
        ),
    ],
)
def test_version_sensitive_invalid_syntax_is_rejected(source, message):
    parse_invalid_syntax(source, message)


@pytest.mark.skipif(
    sys.version_info < (3, 15), reason="Lazy imports are only supported in Python 3.15+"
)
@pytest.mark.parametrize(
    "source, message",
    [
        (
            "from pkg lazy import name",
            "use 'lazy from ... ' instead of 'from ... lazy import'",
        ),
        ("from pkg import name lazy", "invalid syntax"),
    ],
)
def test_invalid_lazy_import_syntax_is_rejected(source, message):
    parse_invalid_syntax(source, message)


@pytest.mark.skipif(
    sys.version_info < (3, 9), reason="Python 3.8 diagnostic is subpar in this case."
)
@pytest.mark.parametrize(
    "source, message, start, end",
    [
        (
            "f'a = {}'",
            (
                "valid expression required before '}'"
                if sys.version_info >= (3, 12)
                else "f-string: empty expression not allowed"
            ),
            (1, 8) if sys.version_info >= (3, 12) else None,
            (1, 9) if sys.version_info >= (3, 12) else None,
        ),
        (
            "f'a = {=}'",
            (
                "expression required before '='"
                if sys.version_info >= (3, 11)
                else "f-string: empty expression not allowed"
            ),
            (1, 8) if sys.version_info >= (3, 12) else None,
            (1, 9) if sys.version_info >= (3, 12) else None,
        ),
        (
            "f'a = {!}'",
            (
                "expression required before '!'"
                if sys.version_info >= (3, 11)
                else "f-string: empty expression not allowed"
            ),
            (1, 8) if sys.version_info >= (3, 12) else None,
            (1, 9) if sys.version_info >= (3, 12) else None,
        ),
        (
            "f'a = {:}'",
            (
                "expression required before ':'"
                if sys.version_info >= (3, 11)
                else "f-string: empty expression not allowed"
            ),
            (1, 8) if sys.version_info >= (3, 12) else None,
            (1, 9) if sys.version_info >= (3, 12) else (1, 11),
        ),
        (
            "f'a = {a=d}'",
            (
                "expecting '!', or ':', or '}'"
                if sys.version_info >= (3, 12)
                else "f-string: expecting '}'"
            ),
            (1, 10) if sys.version_info >= (3, 12) else None,
            (1, 11) if sys.version_info >= (3, 12) else None,
        ),
        (
            "f'a = { 1 + }'",
            (
                "f-string: expecting '=', or '!', or ':', or '}'"
                if sys.version_info >= (3, 12)
                else "f-string: invalid syntax"
            ),
            (1, 11) if sys.version_info >= (3, 12) else (1, 7),
            (1, 12) if sys.version_info >= (3, 12) else (1, 8),
        ),
        (
            "(\n\t'b'\n\tf'a = { 1 + }'\n)",
            (
                "f-string: expecting '=', or '!', or ':', or '}'"
                if sys.version_info >= (3, 12)
                else "f-string: invalid syntax"
            ),
            (3, 12) if sys.version_info >= (3, 12) else (3, 7),
            (3, 13) if sys.version_info >= (3, 12) else (3, 8),
        ),
        (
            'f"{x!z}"',
            (
                "f-string: invalid conversion character 'z': expected 's', 'r', or 'a'"
                if sys.version_info >= (3, 12)
                else "f-string: invalid conversion character: expected 's', 'r', or 'a'"
            ),
            (1, 6) if sys.version_info >= (3, 12) else None,
            (1, 7) if sys.version_info >= (3, 12) else None,
        ),
    ],
)
def test_syntax_error_in_str(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("(a 1)", "invalid syntax. Perhaps you forgot a comma?", (1, 2), (1, 5)),
        ("2 if 4", "expected 'else' after 'if' expression", (1, 1), (1, 7)),
        ("(a 1 if b else 2)", "invalid syntax. Perhaps you forgot a comma?", (1, 2), (1, 17)),
        ("(a lambda: 1)", "invalid syntax. Perhaps you forgot a comma?", (1, 2), (1, 13)),
        ("(a b)", "invalid syntax. Perhaps you forgot a comma?", (1, 2), (1, 5)),
        ("print 1", "Missing parentheses in call to 'print'", (1, 1), (1, 8)),
        ("exec 1", "Missing parentheses in call to 'exec'", (1, 1), (1, 7)),
        ("a if b", "expected 'else' after 'if' expression", (1, 1), (1, 7)),
        ("c = a if b:", "invalid syntax", (1, 11), (1, 12)),
    ],
)
def test_invalid_expression(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("global a, 1", "invalid syntax", (1, 11), (1, 12)),
        ("nonlocal a, 1", "invalid syntax", (1, 13), (1, 14)),
        ("yield raise", "invalid syntax", (1, 7), (1, 12)),
        ("assert raise", "invalid syntax", (1, 8), (1, 13)),
        ("return def", "invalid syntax", (1, 8), (1, 11)),
        ("raise def", "invalid syntax", (1, 7), (1, 10)),
        ("del raise", "invalid syntax", (1, 5), (1, 10)),
        ("if raise:\n\tpass", "invalid syntax", (1, 4), (1, 9)),
        ("@raise\ndef f():\n\tpass", "invalid syntax", (1, 2), (1, 7)),
        ("a: int = raise", "invalid syntax", (1, 10), (1, 15)),
    ],
)
def test_invalid_statements(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("f(**a, *b)", "iterable argument unpacking follows keyword argument unpacking", (1, 6) if sys.version_info >= (3, 12) else None, (1, 10) if sys.version_info >= (3, 12) else None),
        ("f(a for a in b, c)", "Generator expression must be parenthesized", (1, 3), (1, None)),
        ("f(a for a in b if a, c)", "Generator expression must be parenthesized", (1, 3), (1, None)),
        ("f(a for a in b, c for c in d)", "Generator expression must be parenthesized", (1, 3), (1, None)),
        ("f(a=1 for i in range(10))", "invalid syntax. Maybe you meant '==' or ':=' instead of '='?", (1, 3), (1, 5)),
        ("f(a, b for b in c)", "Generator expression must be parenthesized", (1, 6), (1, None)),
        ("f(a, b for b in c, d)", "Generator expression must be parenthesized", (1, 6), (1, None)),
        ("f(*a=b)", "cannot assign to iterable argument unpacking", (1, 3), (1, 7)),
        ("f(**a, b)", "positional argument follows keyword argument unpacking", (1, 9), (1, 10)),
        ("f(a=1, b)", "positional argument follows keyword argument", (1, 9), (1, 10)),
        ("f(b=c for c in d)", "invalid syntax. Maybe you meant '==' or ':=' instead of '='?", (1, 3), (1, 5)),
        ("f(1 + b=2)", 'expression cannot contain assignment, perhaps you meant "=="?', (1, 3), (1, 9)),
        ("f(True=1)", "cannot assign to True", (1, 3), (1, 8)),
        ("f(False=1)", "cannot assign to False", (1, 3), (1, 9)),
        ("f(None=1)", "cannot assign to None", (1, 3), (1, 8)),
    ],
)
def test_invalid_call_arguments(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("'a' = 1", "cannot assign to literal", (1, 1), (1, 4)),
        ("1 = 1", "cannot assign to literal", (1, 1), (1, 2)),
        ("True = 1", "cannot assign to True", (1, 1), (1, 5)),
        ("False = 1", "cannot assign to False", (1, 1), (1, 6)),
        ("... = 1", "cannot assign to ellipsis", (1, 1), (1, 4)),
        ("None = 1", "cannot assign to None", (1, 1), (1, 5)),
        ("(a, b) : int = (1, 2)", "only single target (not tuple) can be annotated", (1, 1), (1, 7)),
        ("[a, b] : int = [1, 2]", "only single target (not list) can be annotated", (1, 1), (1, 7)),
        ("([a, b]) : int = (1, 2)", "only single target (not list) can be annotated", (1, 2), (1, 8)),
        ("a, b: int, int = 1, 2", "only single target (not tuple) can be annotated", (1, 1), (1, 2)),
        ("{a, b} : set", "illegal target for annotation", (1, 1), (1, 7)),
        ("a + 1 = 2", "cannot assign to expression", (1, 1), (1, 6)),
        ("[i for i in range(2)] = 2", "cannot assign to list comprehension", (1, 1), (1, 22)),
        ("yield a = 1", "assignment to yield expression not possible", (1, 1), (1, 8)),
        ("a = yield b = 1", "assignment to yield expression not possible", (1, 5), (1, 12)),
        ("a + 1 += 1", "'expression' is an illegal expression for augmented assignment", (1, 1), (1, 6)),
        ("a + 1 += yield", "'expression' is an illegal expression for augmented assignment", (1, 1), (1, 6)),
        ("[i for i in range(2)] += 1", "'list comprehension' is an illegal expression for augmented assignment", (1, 1), (1, 22)),
        ("a += raise", "invalid syntax", (1, 6), (1, 11)),
    ],
)
def test_invalid_assignments(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("del [i for i in range(2)]", "cannot delete list comprehension", (1, 5), (1, 26)),
        ("del a + 1", "cannot delete expression", (1, 5), (1, 10)),
    ],
)
def test_invalid_del_statements(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("(*a for a in enumerate(range(5)))", "iterable unpacking cannot be used in comprehension", (1, 2), (1, 4)),
        ("[*a for a in enumerate(range(5))]", "iterable unpacking cannot be used in comprehension", (1, 2), (1, 4)),
        ("{*a for a in enumerate(range(5))}", "iterable unpacking cannot be used in comprehension", (1, 2), (1, 4)),
        ("[a, a for a in range(5)]", "did you forget parentheses around the comprehension target?", (1, 2), (1, 6)),
        ("[a,  for a in range(5)]", "did you forget parentheses around the comprehension target?", (1, 2), (1, 4)),
        ("{**a for a in [{1: 2}]}", "dict unpacking cannot be used in dict comprehension", (1, 2), (1, 4)),
        ("(a for a in raise)", "invalid syntax", (1, 13), (1, 18)),
        ("(a async for a in raise)", "invalid syntax", (1, 19), (1, 24)),
    ],
)
def test_invalid_comprehension(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end, py_version",
    [
        ("def f(a=1, b):\n\tpass", "parameter without a default follows parameter with a default", (1, 12), (1, 13), (3, 12)),
        ("def f(a=1, /, b):\n\tpass", "parameter without a default follows parameter with a default", (1, 15), (1, 16), (3, 12)),
        ("def f(x, (y, z), w):\n\tpass", "parameters cannot be parenthesized", (1, 10), (1, 16), (3, 11)),
        ("def f((x, y, z, w)):\n\tpass", "parameters cannot be parenthesized", (1, 7), (1, 19), (3, 11)),
        ("def f(x, (y, z, w)):\n\tpass", "parameters cannot be parenthesized", (1, 10), (1, 19), (3, 11)),
        ("def f((x, y, z), w):\n\tpass", "parameters cannot be parenthesized", (1, 7), (1, 16), (3, 11)),
        ("def foo(/,a,b=,c):\n\tpass", "at least one argument must precede /", (1, 9), (1, 10), (3, 11)),
        ("def foo(a,/,/,b,c):\n\tpass", "/ may appear only once", (1, 13), (1, 14), (3, 11)),
        ("def foo(a,/,a1,/,b,c):\n\tpass", "/ may appear only once", (1, 16), (1, 17), (3, 11)),
        ("def foo(a=1,/,/,*b,/,c):\n\tpass", "/ may appear only once", (1, 15), (1, 16), (3, 11)),
        ("def foo(a,/,a1=1,/,b,c):\n\tpass", "/ may appear only once", (1, 18), (1, 19), (3, 11)),
        ("def foo(a,*b,c,/,d,e):\n\tpass", "/ must be ahead of *", (1, 16), (1, 17), (3, 11)),
        ("def foo(a=1,*b,c=3,/,d,e):\n\tpass", "/ must be ahead of *", (1, 20), (1, 21), (3, 11)),
        ("def foo(a,*b=3,c):\n\tpass", "var-positional argument cannot have default value", (1, 13), (1, 14), (3, 11)),
        ("def foo(a,*b: int=,c):\n\tpass", "var-positional argument cannot have default value", (1, 18), (1, 19), (3, 11)),
        ("def foo(a,**b=3):\n\tpass", "var-keyword argument cannot have default value", (1, 14), (1, 15), (3, 11)),
        ("def foo(a,**b: int=3):\n\tpass", "var-keyword argument cannot have default value", (1, 19), (1, 20), (3, 11)),
        ("def foo(a,*a, b, **c, d):\n\tpass", "arguments cannot follow var-keyword argument", (1, 23), (1, 24), (3, 11)),
        ("def foo(a,*a, b, **c, d=4):\n\tpass", "arguments cannot follow var-keyword argument", (1, 23), (1, 24), (3, 11)),
        ("def foo(a,*a, b, **c, *d):\n\tpass", "arguments cannot follow var-keyword argument", (1, 23), (1, 24), (3, 11)),
        ("def foo(a,*a, b, **c, **d):\n\tpass", "arguments cannot follow var-keyword argument", (1, 23), (1, 25), (3, 11)),
        ("def foo(a=1,/,**b,/,c):\n\tpass", "arguments cannot follow var-keyword argument", (1, 19), (1, 20), (3, 11)),
        ("def foo(*b,*d):\n\tpass", "* argument may appear only once", (1, 12), (1, 13), (3, 11)),
        ("def foo(a,*b,c,*d,*e,c):\n\tpass", "* argument may appear only once", (1, 16), (1, 17), (3, 11)),
        ("def foo(a,b,/,c,*b,c,*d,*e,c):\n\tpass", "* argument may appear only once", (1, 22), (1, 23), (3, 11)),
        ("def foo(a,b,/,c,*b,c,*d,**e):\n\tpass", "* argument may appear only once", (1, 22), (1, 23), (3, 11)),
        ("def foo(a=1,/*,b,c):\n\tpass", "expected comma between / and *", (1, 14), (1, 15), (3, 11)),
        ("def foo(a=1,d=,c):\n\tpasss", "expected default value expression", (1, 14), (1, 15), (3, 11)),
        ("def foo(a,d=,c):\n\tpass", "expected default value expression", (1, 12), (1, 13), (3, 11)),
        ("def foo(a,d: int=,c):\n\tpass", "expected default value expression", (1, 17), (1, 18), (3, 11)),
        ("lambda x=1, y: x", "parameter without a default follows parameter with a default", (1, 13), (1, 14), (3, 12)),
        ("lambda x=1, /, y: x", "parameter without a default follows parameter with a default", (1, 16), (1, 17), (3, 12)),
        ("lambda x, (y, z), w: None", "parameters cannot be parenthesized", (1, 11), (1, 17), (3, 11)),
        ("lambda (x, y, z, w): None", "parameters cannot be parenthesized", (1, 8), (1, 20), (3, 11)),
        ("lambda x, (y, z, w): None", "parameters cannot be parenthesized", (1, 11), (1, 20), (3, 11)),
        ("lambda (x, y, z), w: None", "parameters cannot be parenthesized", (1, 8), (1, 17), (3, 11)),
        ("lambda /,a,b,c: None", "at least one argument must precede /", (1, 8), (1, 9), (3, 11)),
        ("lambda a,/,/,b,c: None", "/ may appear only once", (1, 12), (1, 13), (3, 11)),
        ("lambda a,/,a1,/,b,c: None", "/ may appear only once", (1, 15), (1, 16), (3, 11)),
        ("lambda a=1,/,/,*b,/,c: None", "/ may appear only once", (1, 14), (1, 15), (3, 11)),
        ("lambda a,/,a1=1,/,b,c: None", "/ may appear only once", (1, 17), (1, 18), (3, 11)),
        ("lambda a,*b,c,/,d,e: None", "/ must be ahead of *", (1, 15), (1, 16), (3, 11)),
        ("lambda a=1,*b,c=3,/,d,e: None", "/ must be ahead of *", (1, 19), (1, 20), (3, 11)),
        ("lambda a=1,/*,b,c: None", "expected comma between / and *", (1, 13), (1, 14), (3, 11)),
        ("lambda a,*b=3,c: None", "var-positional argument cannot have default value", (1, 12), (1, 13), (3, 11)),
        ("lambda a,**b=3: None", "var-keyword argument cannot have default value", (1, 13), (1, 14), (3, 11)),
        ("lambda a, *a, b, **c, d: None", "arguments cannot follow var-keyword argument", (1, 23), (1, 24), (3, 11)),
        ("lambda a,*a, b, **c, d=4: None", "arguments cannot follow var-keyword argument", (1, 22), (1, 23), (3, 11)),
        ("lambda a,*a, b, **c, *d: None", "arguments cannot follow var-keyword argument", (1, 22), (1, 23), (3, 11)),
        ("lambda a,*a, b, **c, **d: None", "arguments cannot follow var-keyword argument", (1, 22), (1, 24), (3, 11)),
        ("lambda a=1,/,**b,/,c: None", "arguments cannot follow var-keyword argument", (1, 18), (1, 19), (3, 11)),
        ("lambda *b,*d: None", "* argument may appear only once", (1, 11), (1, 12), (3, 11)),
        ("lambda a,*b,c,*d,*e,c: None", "* argument may appear only once", (1, 15), (1, 16), (3, 11)),
        ("lambda a,b,/,c,*b,c,*d,*e,c: None", "* argument may appear only once", (1, 21), (1, 22), (3, 11)),
        ("lambda a,b,/,c,*b,c,*d,**e: None", "* argument may appear only once", (1, 21), (1, 22), (3, 11)),
        ("lambda a=1,d=,c: None", "expected default value expression", (1, 13), (1, 14), (3, 11)),
        ("lambda a,d=,c: None", "expected default value expression", (1, 11), (1, 12), (3, 11)),
    ],
)
def test_invalid_parameters(source, message, start, end, py_version):
    parse_invalid_syntax(source, message, py_version=py_version, start=start, end=end)


@pytest.mark.parametrize(
    "source, start, end",
    [
        ("def f(a, *):\n\tpass", (1, 10), (1, 11)),
        ("def f(a, *,):\n\tpass", (1, 10), (1, 11)),
        ("def f(a, *, **):\n\tpass", (1, 10), (1, 11)),
        ("lambda a, *: a", (1, 12), (1, 13)),
        ("lambda a, *, **:a", (1, 14), (1, 16)),
    ],
)
def test_invalid_star_etc(source, start, end):
    parse_invalid_syntax(source, "named arguments must follow bare *", start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("with open(a) as {b: 1}:\n\tpass", "cannot assign to dict", (1, 17), (1, 23)),
        ("with open(a) as {b}:\n\tpass", "cannot assign to set", (1, 17), (1, 20)),
        ("with open(a) as 1:\n\tpass", "cannot assign to literal", (1, 17), (1, 18)),
    ],
)
def test_invalid_with_item(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("for {a} in [[1]]:\n\tpass", "cannot assign to set display", (1, 5), (1, 8)),
        ("async for (a := i)", "cannot assign to named expression", (1, 12), (1, 18)),
    ],
)
def test_invalid_for_target(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("a = (1+1 := 2)", "cannot use assignment expressions with expression", (1, 6), (1, 9)),
        ("a := raise", "invalid syntax", (1, 3), (1, 5)),
    ],
)
def test_named_expression(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("a = (*b)", "cannot use starred expression here", (1, 6), (1, 8)),
        ("a = (**b)", "cannot use double starred expression here", (1, 6), (1, 8)),
    ],
)
def test_invalid_group(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("from a import b,", "trailing comma not allowed without surrounding parentheses", (1, 17), (1, 18) if sys.version_info >= (3, 12) else (1, 17)),
        ("from a import b, and 3", "invalid syntax", (1, 18), (1, 21)),
        ("from a import raise", "invalid syntax", (1, 15), (1, 20)),
    ],
)
def test_invalid_import_from_as_names(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ("with open(a) as f, b as d:\npass", "expected an indented block after 'with' statement on line 1", (2, 1), (2, 5)),
        ("with open(a) as f, b as d\npass", "expected ':'", (1, 26), (1, 27) if sys.version_info >= (3, 12) else (1, 26)),
    ],
)
def test_invalid_with_statements(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.skipif(sys.version_info < (3, 14), reason="T-strings are only supported in Python 3.14+")
@pytest.mark.parametrize(
    "source, message, start, end",
    [
        ('t"{x!}"', "t-string: missing conversion character", (1, 6), (1, 7)),
        ('t"{x!z}"', "invalid conversion character 'z': expected 's', 'r', or 'a'", (1, 6), (1, 7)),
        ('t"{x:{y}"', "expecting '}', or format specs", (1, 9), (1, 10)),
    ],
)
def test_invalid_tstring_replacement_field(source, message, start, end):
    parse_invalid_syntax(source, message, start=start, end=end)


@pytest.mark.skipif(
    sys.version_info < (3, 15), reason="Lazy imports are only supported in Python 3.15+"
)
@pytest.mark.parametrize(
    "source, message",
    [
        ("from pkg lazy import name", "use 'lazy from ... ' instead of 'from ... lazy import'"),
        ("from pkg import name lazy", "invalid syntax"),
    ],
)
def test_invalid_lazy_import_syntax(source, message):
    parse_invalid_syntax(source, message)


@pytest.mark.parametrize(
    "source, message",
    [
        ("x = f'{x!q}'", "invalid conversion"),
        (
            "match x:\n    case 0:\n        pass\n    case _ as y:\n        pass",
            "cannot use '_' as a target",
        ),
    ],
)
def test_version_sensitive_invalid_syntax_is_rejected_2(source, message):
    parse_invalid_syntax(source, message)


@pytest.mark.parametrize(
    "source, message",
    [
        ("\nasync with (open(a) as f, b as d):\npass", "expected an indented block after 'with' statement on line 2"),
        ("\nasync with (open(a) as f, b as d)\npass", "expected ':'"),
    ],
)
def test_async_with_syntax_errors(source, message):
    parse_invalid_syntax(source, message)


@pytest.mark.parametrize(
    "source, message, py_version",
    [
        ("try:\n    a = 1\nexcept *ValueError:\n    pass", "Exception groups are", (3, 10)),
        ("match a:\n    case 1:\n        pass", "Pattern matching is", (3, 9)),
    ],
)
def test_version_guarded_syntax(source, message, py_version):
    parse_invalid_syntax(source, message, py_version=py_version)
