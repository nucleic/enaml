# --------------------------------------------------------------------------------------
# Copyright (c) 2021-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
import ast
import warnings
from typing import Dict, Iterable, List, Type, Union

from .. import enaml_ast
from .base_python_parser import BasePythonParser, Del, Load, Store

# XXX doc
class BaseEnamlParser(BasePythonParser):
    """"""

    # The nodes which can be inverted to form an assignable expression.
    INVERTABLE = (ast.Name, ast.Attribute, ast.Call, ast.Subscript)

    # The disallowed ast types on the rhs of a :: operator
    NOTIFICATION_DISALLOWED = {
        ast.FunctionDef: "function definition",
        ast.ClassDef: "class definition",
        ast.Yield: "yield statement",
        ast.Return: "return statement",
        ast.GeneratorExp: "generator expressions",
    }

    # The disallowed ast types on the rhs of a << operator
    SUBSCRIPTION_DISALLOWED = {
        ast.FunctionDef: "function definition",
        ast.ClassDef: "class definition",
        ast.Yield: "yield statement",
        ast.GeneratorExp: "generator expressions",
    }

    # The disallowed ast types in the body of a declarative function
    DECL_FUNCDEF_DISALLOWED = {
        ast.FunctionDef: "function definition",
        ast.ClassDef: "class definition",
        ast.Yield: "yield statement",
        ast.GeneratorExp: "generator expressions",
    }

    def create_python_module(self, stmts: List[ast.AST]) -> enaml_ast.PythonModule:
        """Create a python from a list of Python ast node."""
        return enaml_ast.PythonModule(
            ast=ast.Module(
                body=stmts,
                type_ignores=[],
                lineno=stmts[0].lineno,
                col_offset=stmts[0].col_offset,
                end_lineno=stmts[-1].end_lineno,
                end_col_offset=stmts[-1].end_col_offset,
            ),
            lineno=stmts[0].lineno,
            col_offset=stmts[0].col_offset,
            end_lineno=stmts[-1].end_lineno,
            end_col_offset=stmts[-1].end_col_offset,
        )

    def create_enaml_module(
        self,
        nodes: Iterable[ast.AST],
        lineno: int,
        col_offset: int,
        end_lineno: int,
        end_col_offset: int,
    ) -> enaml_ast.Module:
        """Create an enaml Module from a list of ast nodes."""
        body = []
        stmts = []
        for node in nodes:
            if isinstance(node, (enaml_ast.EnamlDef, enaml_ast.Template)):
                if stmts:
                    body.append(self.create_python_module(stmts))
                    stmts = []
                body.append(node)
            else:
                stmts.append(node)
        if stmts:
            body.append(self.create_python_module(stmts))
        return enaml_ast.Module(
            body=body,
            lineno=lineno,
            col_offset=col_offset,
            end_lineno=end_lineno,
            end_col_offset=end_col_offset,
        )

    # rework to take a list of ast node and return it and filter out None values
    def validate_enamldef(self, node: enaml_ast.EnamlDef) -> enaml_ast.EnamlDef:
        """Validate the correctness of names in an enamldef definition.

        This function ensures that identifiers do not shadow one another.

        """
        ident_names = set()

        def check_id(name, node):
            if name in ident_names:
                msg = (
                    f"redeclaration of identifier '{name}'"
                    " (this will be an error in Enaml version 1.0)"
                )
                warnings.warn_explicit(msg, SyntaxWarning, self.filename, node.lineno)
            ident_names.add(name)

        # validate the identifiers
        ChildDef = enaml_ast.ChildDef
        TemplateInst = enaml_ast.TemplateInst
        stack = list(reversed(node.body))
        while stack:
            n = stack.pop()
            if isinstance(n, ChildDef):
                if n.identifier:
                    check_id(n.identifier, n)
                stack.extend(reversed(n.body))
            elif isinstance(n, TemplateInst):
                idents = n.identifiers
                if idents is not None:
                    for name in idents.names:
                        check_id(name, idents)
                    if idents.starname:
                        check_id(idents.starname, idents)

        return node

    def create_python_func_for_operator(
        self, body: List[ast.AST], forbidden_nodes: Dict[Type[ast.AST], str], msg: str
    ) -> enaml_ast.PythonModule:
        for node in body:
            for item in ast.walk(node):
                if type(item) in forbidden_nodes:
                    msg = msg % forbidden_nodes[type(item)]
                    self.raise_syntax_error_known_location(msg, item)

        func_node = ast.FunctionDef()
        func_node.name = "f"
        func_node.args = self.make_arguments(None, [], None, None, None)
        func_node.decorator_list = []
        func_node.returns = None
        func_node.body = body
        func_node.lineno = body[0].lineno
        func_node.col_offset = body[0].col_offset
        func_node.end_lineno = body[-1].end_lineno
        func_node.end_col_offset = body[-1].end_col_offset

        return self.create_python_module([func_node])

    def validate_decl_func_body(self, body: List[ast.AST]) -> List[ast.AST]:
        """Validate the body of declarative function.

        Any definition that may capture the surrounding scope is forbidden.

        """
        for node in body:
            for item in ast.walk(node):
                if type(item) in self.DECL_FUNCDEF_DISALLOWED:
                    msg = (
                        f"{self.DECL_FUNCDEF_DISALLOWED[type(item)]} "
                        "not allowed in a declarative function block."
                    )
                    self.raise_syntax_error_known_location(msg, item)

        return body

    def validate_template(self, node: enaml_ast.Template) -> enaml_ast.Template:
        """Validate the correctness of names in a template definitions.

        This function ensures that parameters, const expressions, and
        identifiers do not shadow one another.

        """
        param_names = set()
        const_names = set()
        ident_names = set()

        def check_const(name: str, node: enaml_ast.ConstExpr):
            msg = None
            if name in param_names:
                msg = f"declaration of 'const {name}' shadows a parameter"
            elif name in const_names:
                msg = f"redeclaration of 'const {name}'"
            if msg is not None:
                self.raise_syntax_error_known_location(msg, node)
            const_names.add(name)

        def check_id(
            name: str, node: Union[enaml_ast.ChildDef, enaml_ast.TemplateIdentifiers]
        ):
            msg = None
            if name in param_names:
                msg = f"identifier '{name}' shadows a parameter"
            elif name in const_names:
                msg = f"identifier '{name}' shadows a const expression"
            elif name in ident_names:
                msg = f"redeclaration of identifier '{name}'"
            if msg is not None:
                self.raise_syntax_error_known_location(msg, node)
            ident_names.add(name)

        # collect the parameter names
        params = node.parameters
        for param in params.positional:
            param_names.add(param.name)
        for param in params.keywords:
            param_names.add(param.name)
        if params.starparam:
            param_names.add(params.starparam)

        # validate the const expressions
        ConstExpr = enaml_ast.ConstExpr
        for item in node.body:
            if isinstance(item, ConstExpr):
                check_const(item.name, item)

        # validate the identifiers
        ChildDef = enaml_ast.ChildDef
        TemplateInst = enaml_ast.TemplateInst
        stack = list(reversed(node.body))
        while stack:
            n = stack.pop()
            if isinstance(n, ChildDef):
                if n.identifier:
                    check_id(n.identifier, n)
                stack.extend(reversed(n.body))
            elif isinstance(n, TemplateInst):
                idents = n.identifiers
                if idents is not None:
                    for name in idents.names:
                        check_id(name, idents)
                    if idents.starname:
                        check_id(idents.starname, idents)

        return node

    def validate_template_paramlist(
        self,
        paramlist: List[
            Union[enaml_ast.PositionalParameter, enaml_ast.KeywordParameter]
        ],
        starparam: str,
    ) -> dict[str, list]:
        keywords = []
        positional = []
        seen_params = set([starparam])
        for param in paramlist:
            if param.name in seen_params:
                msg = f"duplicate argument '{param.name}' in template definition"
                self.raise_syntax_error_known_location(msg, param)
            seen_params.add(param.name)
            if isinstance(param, enaml_ast.KeywordParameter):
                keywords.append(param)
            elif keywords:
                msg = "non-default argument follows default argument"
                self.raise_syntax_error_known_location(msg, param)
            else:
                positional.append(param)
        return {"positional": positional, "keywords": keywords, "starparam": starparam}

    def validate_template_inst(
        self, node: enaml_ast.TemplateInst
    ) -> enaml_ast.TemplateInst:
        """Validate a template instantiation.

        This function ensures that the bindings on the instantiation refer
        to declared identifiers on the instantiation.

        """
        names = set()
        if node.identifiers:
            names.update(node.identifiers.names)
        for binding in node.body:
            if binding.name not in names:
                msg = f"'{binding.name}' is not a valid template id reference"
                self.raise_syntax_error_known_location(msg, binding)

        return node
