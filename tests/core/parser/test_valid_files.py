import ast
import sys
from pathlib import Path

import pytest

from enaml.core.parser import parse

VALID_DIR = Path(__file__).resolve().parent / "valid" / "enaml"
PYTHON_VALID_DIR = Path(__file__).resolve().parent / "valid" / "python"


def _dump_node(node, *, seen=None, include_attributes=True):
    """Return a stable structural representation for AST-like objects."""
    if seen is None:
        seen = set()

    if node is None:
        return "None"
    if isinstance(node, ast.AST):
        return ast.dump(node, include_attributes=include_attributes)
    if isinstance(node, list):
        return (
            "["
            + ", ".join(
                _dump_node(value, seen=seen, include_attributes=include_attributes)
                for value in node
            )
            + "]"
        )
    if isinstance(node, tuple):
        inner = ", ".join(
            _dump_node(value, seen=seen, include_attributes=include_attributes)
            for value in node
        )
        return "(" + inner + (")" if len(node) != 1 else ",)")
    if isinstance(node, dict):
        items = [
            f"{key!r}: {_dump_node(value, seen=seen, include_attributes=include_attributes)}"
            for key, value in node.items()
        ]
        return "{" + ", ".join(items) + "}"
    if isinstance(node, str):
        return repr(node)
    if isinstance(node, (int, float, bool)):
        return repr(node)
    if hasattr(node, "_fields"):
        node_id = id(node)
        if node_id in seen:
            return f"<cycle:{type(node).__name__}>"
        seen.add(node_id)
        try:
            fields = [
                f"{field}={_dump_node(getattr(node, field), seen=seen, include_attributes=include_attributes)}"
                for field in getattr(node, "_fields", ())
            ]
            return f"{type(node).__name__}({', '.join(fields)})"
        finally:
            seen.remove(node_id)
    return repr(node)


def _unwrap_python_ast(node):
    """Return the underlying Python AST while ignoring Enaml-wrapper nodes."""
    seen = set()
    while node is not None and id(node) not in seen:
        seen.add(id(node))
        if isinstance(node, ast.AST):
            return node
        if hasattr(node, "ast") and getattr(node, "ast") is not None:
            node = getattr(node, "ast")
            continue
        body = getattr(node, "body", None)
        if isinstance(body, list):
            for item in body:
                if hasattr(item, "ast") and getattr(item, "ast") is not None:
                    node = item
                    break
            else:
                return node
            continue
        return node
    return node


def _iter_python_snippets():
    if not PYTHON_VALID_DIR.exists():
        return []

    items = []
    for path in sorted(
        PYTHON_VALID_DIR.rglob("*.py"),
        key=lambda path: str(path.relative_to(PYTHON_VALID_DIR)),
    ):
        items.append(path)
    return items


def _iter_enaml_fixtures():
    if not VALID_DIR.exists():
        return []
    return sorted(
        VALID_DIR.rglob("*.enaml"), key=lambda path: str(path.relative_to(VALID_DIR))
    )


def _should_skip_python_fixture(path):
    return sys.version_info < (3, 14) and "tstring" in path.stem.lower()


@pytest.mark.parametrize("path", _iter_python_snippets())
def test_valid_python_fixtures_match_stdlib_ast(path):
    if _should_skip_python_fixture(path):
        pytest.skip("t-strings require Python 3.14+")

    source = path.read_text(encoding="utf-8")
    parsed = _unwrap_python_ast(parse(source))
    python_ast = ast.parse(source)

    assert _dump_node(parsed, include_attributes=True) == _dump_node(
        python_ast, include_attributes=True
    )


@pytest.mark.skipif(
    sys.version_info < (3, 15), reason="Lazy imports are only supported in Python 3.15+"
)
def test_lazy_imports_ast():
    source = "import foo\nfrom bar import baz\n"
    parsed = parse(source)
    python_ast = ast.parse(source)

    assert len(parsed.body) == 1
    assert len(parsed.body[0].ast.body) == 2
    assert parsed.body[0].ast.body[0].is_lazy == 0
    assert parsed.body[0].ast.body[1].is_lazy == 0
    assert ast.dump(parsed.body[0].ast.body[0], include_attributes=True) == ast.dump(
        python_ast.body[0], include_attributes=True
    )
    assert ast.dump(parsed.body[0].ast.body[1], include_attributes=True) == ast.dump(
        python_ast.body[1], include_attributes=True
    )


@pytest.mark.skipif(
    sys.version_info < (3, 15), reason="Lazy imports are only supported in Python 3.15+"
)
def test_explicit_lazy_imports_ast():
    source = "lazy import foo\nlazy from bar import baz\n"
    parsed = parse(source)
    python_ast = ast.parse(source)

    assert len(parsed.body) == 1
    assert len(parsed.body[0].ast.body) == 2
    assert parsed.body[0].ast.body[0].is_lazy == 1
    assert parsed.body[0].ast.body[1].is_lazy == 1
    assert ast.dump(parsed.body[0].ast.body[0], include_attributes=True) == ast.dump(
        python_ast.body[0], include_attributes=True
    )
    assert ast.dump(parsed.body[0].ast.body[1], include_attributes=True) == ast.dump(
        python_ast.body[1], include_attributes=True
    )


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
def test_invalid_lazy_import_syntax(source, message):
    with pytest.raises(SyntaxError, match=message):
        parse(source)


@pytest.mark.parametrize(
    "path", _iter_enaml_fixtures(), ids=lambda path: str(path.relative_to(VALID_DIR))
)
def test_valid_enaml_fixtures_parse_without_error(path):
    source = path.read_text(encoding="utf-8")
    module = parse(source)

    assert hasattr(module, "body")
    assert isinstance(module.body, list)
