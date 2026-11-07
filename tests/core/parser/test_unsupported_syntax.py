import pytest

from enaml.core.parser import parse


@pytest.mark.parametrize("source", ["a @ b", "a @= b"])
def test_matrix_multiplication_requires_python_35(source):
    with pytest.raises(SyntaxError):
        parse(source, py_version=(3, 4))


@pytest.mark.parametrize("source", ["await b", "async def f():\n    pass"])
def test_await_and_async_require_python_35(source):
    with pytest.raises(SyntaxError):
        parse(source, py_version=(3, 4))


@pytest.mark.parametrize("source", ["match x:\n    case 0:\n        pass"])
def test_match_requires_python_310(source):
    with pytest.raises(SyntaxError):
        parse(source, py_version=(3, 9))


@pytest.mark.parametrize("source", ["try:\n    pass\nexcept* ValueError:\n    pass"])
def test_except_star_requires_python_311(source):
    with pytest.raises(SyntaxError):
        parse(source, py_version=(3, 10))
