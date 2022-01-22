# --------------------------------------------------------------------------------------
# Copyright (c) 2021-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
# NOTE This is a vendored version of the pegen base python parser included in
# the header of python grammar DO NOT EDIT

import ast
import sys
import tokenize
from typing import Any, List, NoReturn, Optional, Tuple, TypeVar, Union

from pegen.parser import Parser
from pegen.tokenizer import Tokenizer

# Singleton ast nodes, created once for efficiency
Load = ast.Load()
Store = ast.Store()
Del = ast.Del()

Node = TypeVar("Node")
FC = TypeVar("FC", ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

EXPR_NAME_MAPPING = {
    ast.Attribute: "attribute",
    ast.Subscript: "subscript",
    ast.Starred: "starred",
    ast.Name: "name",
    ast.List: "list",
    ast.Tuple: "tuple",
    ast.Lambda: "lambda",
    ast.Call: "function call",
    ast.BoolOp: "expression",
    ast.BinOp: "expression",
    ast.UnaryOp: "expression",
    ast.GeneratorExp: "generator expression",
    ast.Yield: "yield expression",
    ast.YieldFrom: "yield expression",
    ast.Await: "await expression",
    ast.ListComp: "list comprehension",
    ast.SetComp: "set comprehension",
    ast.DictComp: "dict comprehension",
    ast.Dict: "dict literal",
    ast.Set: "set display",
    ast.JoinedStr: "f-string expression",
    ast.FormattedValue: "f-string expression",
    ast.Compare: "comparison",
    ast.IfExp: "conditional expression",
    ast.NamedExpr: "named expression",
}


class BasePythonParser(Parser):

    #: Name of the source file, used in error reports
    filename : str

    def __init__(self,
        tokenizer: Tokenizer, *,
        verbose: bool = False,
        filename: str = "<unknown>",
        path: str = "",
        py_version: Optional[tuple] = None,
    ) -> None:
        super().__init__(tokenizer, verbose=verbose)
        self.filename = filename
        self.path = path
        self.py_version = min(py_version, sys.version_info) if py_version else sys.version_info
        self._exception = None

    def parse(self, rule: str) -> Optional[ast.AST]:
        res = getattr(self, rule)()
        if res is None:
            if self._exception is not None:
                raise self._exception
            else:
                raise SyntaxError("invalid syntax")

        return res

    def check_version(self, min_version: Tuple[int, ...], error_msg: str, node: Node) -> Node:
        """Check that the python version is high enough for a rule to apply.

        """
        if self.py_version >= min_version:
            return node
        else:
            raise SyntaxError(
                f"{error_msg} is only supported in Python {min_version} and above."
            )

    def raise_indentation_error(self, msg) -> None:
        """Raise an indentation error."""
        raise IndentationError(msg)

    def get_expr_name(self, node) -> str:
        """Get a descriptive name for an expression."""
        # See https://github.com/python/cpython/blob/master/Parser/pegen.c#L161
        assert node is not None
        node_t = type(node)
        if node_t is ast.Constant:
            v = node.value
            if v in (None, True, False, Ellipsis):
                return str(v)
            else:
                return "literal"

        try:
            return EXPR_NAME_MAPPING[node_t]
        except KeyError:
            raise ValueError(
                f"unexpected expression in assignment {type(node).__name__} "
                f"(line {node.lineno})."
            )

    def set_expr_context(self, node, context):
        """Set the context (Load, Store, Del) of an ast node."""
        node.ctx = context
        return node

    def ensure_real(self, number_str: str):
        number = ast.literal_eval(number_str)
        if number is not complex:
            self.store_syntax_error("real number required in complex literal")
        return number

    def ensure_imaginary(self, number_str: str):
        number = ast.literal_eval(number_str)
        if number is not complex:
            self.store_syntax_error("imaginary  number required in complex literal")
        return number

    def generate_ast_for_string(self, tokens):
        """Generate AST nodes for strings."""
        err_msg = ''
        line = 1
        col_offset = 0
        source = ''
        for t in tokens:
            n_line = t.start[0] - line
            if n_line:
                col_offset = 0
            source += """\n""" * n_line + ' ' * (t.start[1] - col_offset) + t.string
            line, col_offset = t.end
        if source[0] == ' ':
            source = '(' + source[1:]
        else:
            source = '(' + source
        source += ')'
        try:
            m = ast.parse(source)
        except SyntaxError as e:
            err_msg = e.args[0]
            # Identify the line at which the error occurred to get a more
            # accurate line number
            for t in tokens:
                try:
                    m = ast.parse(t.string)
                except SyntaxError:
                    break

        # Avoid getting a triple nesting in the error report that does not
        # bring anything relevant to the traceback.
        if err_msg:
            self.store_syntax_error_known_location(err_msg, t)
            raise self._exception

        return m.body[0].value

    def extract_import_level(self, tokens: List[tokenize.TokenInfo]) -> int:
        """Extract the relative import level from the tokens preceding the module name.

        '.' count for one and '...' for 3.

        """
        level = 0
        for t in tokens:
            if t.string == ".":
                level += 1
            else:
                level += 3
        return level

    def set_decorators(self,
        target: FC,
        decorators: list
    ) -> FC:
        """Set the decorators on a function or class definition."""
        target.decorator_list = decorators
        return target

    def get_comparison_ops(self, pairs):
        return [op for op, _ in pairs]

    def get_comparators(self, pairs):
        return [comp for _, comp in pairs]

    def set_arg_type_comment(self, arg, type_comment):
        if type_comment:
            arg.type_comment = type_comment
        return arg

    def make_arguments(self,
        pos_only: Optional[List[Tuple[ast.arg, None]]],
        pos_only_with_default: List[Tuple[ast.arg, Any]],
        param_no_default: Optional[List[Tuple[ast.arg, None]]],
        param_default: Optional[List[Tuple[ast.arg, Any]]],
        after_star: Optional[
            Tuple[Optional[ast.arg], List[Tuple[ast.arg, Any]], Optional[ast.arg]]
        ]
    ) -> ast.arguments:
        """Build a function definition arguments."""
        defaults = (
            [d for _, d in pos_only_with_default if d is not None]
            if pos_only_with_default else
            []
        )
        defaults += (
            [d for _, d in param_default if d is not None]
            if param_default else
            []
        )

        pos_only = pos_only or pos_only_with_default

        # Because we need to combine pos only with and without default even
        # the version with no default is a tuple
        pos_only = [p for p, _ in pos_only]
        params = (param_no_default or []) + ([p for p, _ in param_default] if param_default else [])

        # If after_star is None, make a default tuple
        after_star = after_star or (None, [], None)

        return ast.arguments(
            posonlyargs=pos_only,
            args=params,
            defaults=defaults,
            vararg=after_star[0],
            kwonlyargs=[p for p, _ in after_star[1]],
            kw_defaults=[d for _, d in after_star[1]],
            kwarg=after_star[2]
        )

    def _store_syntax_error(
        self,
        message: str,
        start: Optional[Tuple[int, int]] = None,
        end: Optional[Tuple[int, int]] = None
    ) -> NoReturn:
        line_from_token = start is None and end is None
        if start is None or end is None:
            tok = self._tokenizer.diagnose()
            start = start or tok.start
            end = end or tok.end

        if line_from_token:
            line = tok.line
        else:
            # End is used only to get the proper text
            line = ""  # XXX more work to grab the sources

        self._exception = SyntaxError(
            message,
            (self.filename, start[0], start[1], line)
        )

    def store_syntax_error(self, message: str) -> NoReturn:
        self._store_syntax_error(message)

    make_syntax_error = store_syntax_error

    def store_syntax_error_known_location(self, message: str, node) -> None:
        """Store a syntax error that occured at a given AST node."""
        if isinstance(node, tokenize.TokenInfo):
            start = node.start
            end = node.end
        else:
            start = node.lineno, node.col_offset
            end = node.end_lineno, node.end_col_offset

        self._store_syntax_error(message, start, end)

    def store_syntax_error_known_range(
        self,
        message: str,
        start_node: Union[ast.AST, tokenize.TokenInfo],
        end_node: Union[ast.AST, tokenize.TokenInfo]
    ) -> None:
        if isinstance(start_node, tokenize.TokenInfo):
            start = start_node.start
        else:
            start = start_node.lineno, start_node.col_offset

        if isinstance(end_node, tokenize.TokenInfo):
            end = end_node.end
        else:
            end = end_node.end_lineno, end_node.end_col_offset

        self._store_syntax_error(message, start, end)

    def store_syntax_error_starting_from(
        self,
        message: str,
        start_node: Union[ast.AST, tokenize.TokenInfo]
    ) -> None:
        if isinstance(start_node, tokenize.TokenInfo):
            start = start_node.start
        else:
            start = start_node.lineno, start_node.col_offset

        self._store_syntax_error(message, start, None)

    def raise_syntax_error(self, message: str) -> NoReturn:
        self._store_syntax_error(message)
        raise self._exception

    def raise_syntax_error_known_location(
            self,
            message: str,
            node: Union[ast.AST, tokenize.TokenInfo]
        ) -> NoReturn:
        """Raise a syntax error that occurred at a given AST node."""
        self.store_syntax_error_known_location(message, node)
        raise self._exception

    def raise_syntax_error_known_range(
        self,
        message: str,
        start_node: Union[ast.AST, tokenize.TokenInfo],
        end_node: Union[ast.AST, tokenize.TokenInfo]
    ) -> NoReturn:
        self.store_syntax_error_known_range(message, start_node, end_node)
        raise self._exception

    def raise_syntax_error_starting_from(
        self,
        message: str,
        start_node: Union[ast.AST, tokenize.TokenInfo]
    ) -> NoReturn:
        self.store_syntax_error_starting_from(message, start_node)
        raise self._exception
