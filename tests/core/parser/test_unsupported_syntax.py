import io
import tokenize

import pytest

from enaml.core.parser import parse


@pytest.mark.parametrize("source", ["a @ b", "a @= b"])
def test_matrix_multiplication_requires_python_35(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 4))

    assert "The '@' operator is" in str(exc.value)


@pytest.mark.parametrize("source", ["await b", "async def f():\n    pass"])
def test_await_and_async_require_python_35(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 4))

    assert "Await expressions are" in str(exc.value) or "Async functions are" in str(exc.value)


@pytest.mark.parametrize(
    "source, message",
    [
        ("async def f():\n    pass", "Async functions are"),
        ("async with a:\n    pass", "Async with statements are"),
        ("async for a in b:\n    pass", "Async for loops are"),
    ],
)
def test_async_requires_python_35(source, message):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 4))

    assert message in str(exc.value)


@pytest.mark.parametrize("source", ["[a async for a in b if c]"])
def test_async_comprehension_requires_python_36(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 5))

    assert "Async comprehensions are" in str(exc.value)


@pytest.mark.parametrize("source", ["a: int = 1", "(a): int "])
def test_variable_annotation_requires_python_36(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 5))

    assert "Variable annotation syntax is" in str(exc.value)


@pytest.mark.parametrize("source", ["def f(a,/):\n\tpass", "def f(a=1,/):\n\tpass"])
def test_pos_only_args_require_python_38(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 7))

    assert "Positional only arguments are" in str(exc.value)


@pytest.mark.parametrize("source", ["a := 1"])
def test_assignment_operator_requires_python_38(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 7))

    assert "The ':=' operator is" in str(exc.value)


@pytest.mark.parametrize("source", ["@f[1]\ndef f():\n\tpass"])
def test_generic_decorators_require_python_39(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 8))

    assert "Generic decorator are" in str(exc.value)


@pytest.mark.parametrize("source", ["with (a, b):\n\tpass"])
def test_parenthesized_with_items_require_python_39(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 8))

    assert "Parenthesized with items" in str(exc.value)


@pytest.mark.parametrize(
    "source",
    ["match a:\n\tcase 1:\n\t\tpass", "match a", "match a:\ncase b"],
)
def test_match_requires_python_310(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 9))

    assert "Pattern matching is" in str(exc.value)


@pytest.mark.parametrize("source", ["try:\n\ta = 1\nexcept *ValueError:\n\tpass"])
def test_except_star_requires_python_311(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 10))

    assert "Exception groups are" in str(exc.value)


@pytest.mark.parametrize("source", ["type T = int", "type T[U] = tuple[U]"])
def test_type_statement_requires_python_312(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 11))

    assert "Type statement is" in str(exc.value) or "Type parameter lists are" in str(exc.value)


@pytest.mark.parametrize("source", ["def f[T]():\n\tpass", "async def f[T]():\n\tpass"])
def test_generic_function_statement_requires_python_312(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 11))

    assert "Type parameter lists are" in str(exc.value)


@pytest.mark.parametrize("source", ["class A[T]:\n\tpass"])
def test_generic_class_statement_requires_python_312(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 11))

    assert "Type parameter lists are" in str(exc.value)


@pytest.mark.parametrize("source", ["try:\n\tpass\nexcept ValueError, IndexError:\n\tpass"])
def test_unparenthesized_except_requires_python_314(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 13))

    assert "multiple exception types must be parenthesized" in str(exc.value)


@pytest.mark.parametrize(
    "source, message",
    [
        ("[*a for a in b]", "iterable unpacking cannot be used in comprehension"),
        ("{*a for a in b}", "iterable unpacking cannot be used in comprehension"),
        ("(*a for a in b)", "iterable unpacking cannot be used in comprehension"),
        ("{**a for a in b}", "dict unpacking cannot be used in dict comprehension"),
    ],
)
def test_comprehension_unpacking_requires_python_315(source, message):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 14))

    assert message in str(exc.value)


@pytest.mark.parametrize("source", ["lazy import foo", "lazy import foo as bar", "lazy from pkg import name"])
def test_lazy_import_requires_python_315(source):
    with pytest.raises(SyntaxError) as exc:
        parse(source, py_version=(3, 14))

    assert "Lazy imports are" in str(exc.value) or "use 'lazy from ... ' instead of 'from ... lazy import'" in str(exc.value)
