import ast
import io
import difflib
import sys
import textwrap
import tokenize
from pathlib import Path

import pytest

from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.parser import parse

VALID_DIR = Path(__file__).resolve().parent / "valid" / "enaml"
PYTHON_VALID_DIR = Path(__file__).resolve().parent / "valid" / "python"


def _is_stdlib_ast(node):
    """Return True for stdlib AST nodes, excluding Enaml wrapper nodes."""
    return isinstance(node, ast.AST) and type(node).__module__ == "ast"


def _dump_node(node, *, seen=None, include_attributes=True):
    """Return a stable structural representation for AST-like objects."""
    if seen is None:
        seen = set()

    if node is None:
        return "None"
    if _is_stdlib_ast(node):
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
        if _is_stdlib_ast(node):
            return node
        if isinstance(node, list):
            if len(node) == 1:
                node = node[0]
                continue
            if all(_is_stdlib_ast(item) for item in node):
                return ast.Module(body=node, type_ignores=[])
            return node
        if hasattr(node, "ast") and getattr(node, "ast") is not None:
            node = getattr(node, "ast")
            continue
        body = getattr(node, "body", None)
        if isinstance(body, list):
            if all(_is_stdlib_ast(item) for item in body):
                return ast.Module(body=body, type_ignores=[])
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
        stem = path.stem.lower()
        if sys.version_info < (3, 14) and "type_params" in stem:
            items.append(
                pytest.param(
                    path,
                    marks=pytest.mark.skip(
                        "type declarations allowed only in Python 3.12+"
                    ),
                    id=stem,
                )
            )
        elif sys.version_info < (3, 14) and "tstring" in stem:
            items.append(
                pytest.param(
                    path,
                    marks=pytest.mark.skip(
                        "T-strings are only supported in Python 3.14+"
                    ),
                    id=stem,
                )
            )
        elif sys.version_info < (3, 14) and "unparenthesized_except" in stem:
            items.append(
                pytest.param(
                    path,
                    marks=pytest.mark.skip(
                        "Unparenthesized multi-exception except blocks are only supported in Python 3.14+"
                    ),
                    id=stem,
                )
            )
        elif sys.version_info < (3, 15) and "lazy_import" in stem:
            items.append(
                pytest.param(
                    path,
                    marks=pytest.mark.skip("Lazy imports allowed only in Python 3.15+"),
                    id=stem,
                )
            )
        elif sys.version_info < (3, 15) and "comprehensions_unpacking" in stem:
            items.append(
                pytest.param(
                    path,
                    marks=pytest.mark.skip(
                        "Unpacking in comprehensions allowed only in Python 3.15+"
                    ),
                    id=stem,
                )
            )
        else:
            items.append(pytest.param(path, id=stem))
    return items


def _iter_enaml_fixtures():
    if not VALID_DIR.exists():
        return []
    return sorted(
        VALID_DIR.rglob("*.enaml"), key=lambda path: str(path.relative_to(VALID_DIR))
    )


@pytest.mark.parametrize("path", _iter_python_snippets())
def test_valid_python_fixtures_match_stdlib_ast(path):
    with open(path) as f:
        source = f.read()

    for part in source.split("\n\n\n"):
        original = ast.parse(part)

        try:
            enaml_ast = _unwrap_python_ast(parse(part))
        except Exception:
            temp = io.StringIO(part)
            print("Parsing failed:")
            print("Source is:")
            print(textwrap.indent(part, "  "))
            temp = io.StringIO(part)
            print("Token stream is:")
            for t in tokenize.generate_tokens(temp.readline):
                print(t)
            print()
            print("CPython ast is:")
            print(ast.dump(original, include_attributes=True, indent="  "))
            raise

        o = ast.dump(original, include_attributes=True, indent="  ")
        p = ast.dump(enaml_ast, include_attributes=True, indent="  ")
        diff = "\n".join(
            difflib.unified_diff(
                o.split("\n"), p.split("\n"), "cpython", "python-pegen"
            )
        )
        if diff:
            print(part)
            print(diff)
        assert not diff


@pytest.mark.parametrize(
    "path", _iter_enaml_fixtures(), ids=lambda path: str(path.relative_to(VALID_DIR))
)
def test_valid_enaml_fixtures_parse_without_error(path):
    source = path.read_text(encoding="utf-8")

    for part in source.split("\n\n\n"):

        try:
            module = parse(part)
        except Exception:
            print("Parsing failed for part:")
            print(textwrap.indent(part, "  "))
            raise

        assert hasattr(module, "body")
        assert isinstance(module.body, list)
        EnamlCompiler.compile(module, str(path))
