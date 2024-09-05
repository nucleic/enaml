
#---------------------------------------------------------------------------------------
# Copyright (c) 2021-2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#---------------------------------------------------------------------------------------
# NOTE This file was generated using enaml/core/parser/generate_enaml_parser.py
# DO NOT EDIT DIRECTLY
import ast
import sys
import itertools
from typing import Any, List, NoReturn, Optional, Tuple, TypeVar, Union

from enaml.core import enaml_ast
from pegen.parser import Parser, logger, memoize, memoize_left_rec

from .base_enaml_parser import BaseEnamlParser as Parser

# Singleton ast nodes, created once for efficiency
Load = ast.Load()
Store = ast.Store()
Del = ast.Del()
# Keywords and soft keywords are listed at the end of the parser definition.
class EnamlParser(Parser):

    @memoize
    def start(self) -> Optional[enaml_ast . Module]:
        # start: enaml_item* NEWLINE? $
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._loop0_1(),)
            and
            (self.expect('NEWLINE'),)
            and
            (self.expect('ENDMARKER'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . create_enaml_module ( itertools . chain . from_iterable ( a ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def enaml_item(self) -> Optional[List [ast . AST]]:
        # enaml_item: statement | enamldef | template
        mark = self._mark()
        if (
            (statement := self.statement())
        ):
            return statement;
        self._reset(mark)
        if (
            (a := self.enamldef())
        ):
            return [a];
        self._reset(mark)
        if (
            (a := self.template())
        ):
            return [a];
        self._reset(mark)
        return None;

    @memoize
    def enamldef(self) -> Optional[enaml_ast . EnamlDef]:
        # enamldef: pragma* "enamldef" NAME '(' NAME ')' [':' NAME] &&':' enamldef_body
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (p := self._loop0_2(),)
            and
            (self.expect("enamldef"))
            and
            (a := self.name())
            and
            (self.expect('('))
            and
            (b := self.name())
            and
            (self.expect(')'))
            and
            (c := self._tmp_3(),)
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (d := self.enamldef_body())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . validate_enamldef ( enaml_ast . EnamlDef ( typename = a . string , base = b . string , identifier = c . string if c else '' , docstring = d [0] , body = [x for x in d [1] if not isinstance ( x , ast . Pass )] , pragmas = p , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) );
        self._reset(mark)
        return None;

    @memoize
    def enamldef_body(self) -> Optional[Tuple [str , list]]:
        # enamldef_body: NEWLINE INDENT STRING NEWLINE enamldef_item+ DEDENT | NEWLINE INDENT enamldef_item+ DEDENT | enamldef_simple_item | invalid_block
        mark = self._mark()
        if (
            (self.expect('NEWLINE'))
            and
            (self.expect('INDENT'))
            and
            (a := self.string())
            and
            (self.expect('NEWLINE'))
            and
            (b := self._loop1_4())
            and
            (self.expect('DEDENT'))
        ):
            return a . string , b;
        self._reset(mark)
        if (
            (self.expect('NEWLINE'))
            and
            (self.expect('INDENT'))
            and
            (b := self._loop1_5())
            and
            (self.expect('DEDENT'))
        ):
            return "" , b;
        self._reset(mark)
        if (
            (a := self.enamldef_simple_item())
        ):
            return "" , [a];
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_block())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def enamldef_item(self) -> Optional[Any]:
        # enamldef_item: enamldef_simple_item | decl_funcdef | child_def | template_inst
        mark = self._mark()
        if (
            (enamldef_simple_item := self.enamldef_simple_item())
        ):
            return enamldef_simple_item;
        self._reset(mark)
        if (
            (decl_funcdef := self.decl_funcdef())
        ):
            return decl_funcdef;
        self._reset(mark)
        if (
            (child_def := self.child_def())
        ):
            return child_def;
        self._reset(mark)
        if (
            (template_inst := self.template_inst())
        ):
            return template_inst;
        self._reset(mark)
        return None;

    @memoize
    def enamldef_simple_item(self) -> Optional[Any]:
        # enamldef_simple_item: binding | ex_binding | storage_alias_const_expr | 'pass' NEWLINE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (binding := self.binding())
        ):
            return binding;
        self._reset(mark)
        if (
            (ex_binding := self.ex_binding())
        ):
            return ex_binding;
        self._reset(mark)
        if (
            (storage_alias_const_expr := self.storage_alias_const_expr())
        ):
            return storage_alias_const_expr;
        self._reset(mark)
        if (
            (self.expect('pass'))
            and
            (self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Pass ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def pragmas(self) -> Optional[List [enaml_ast . Pragma]]:
        # pragmas: pragma+
        mark = self._mark()
        if (
            (_loop1_6 := self._loop1_6())
        ):
            return _loop1_6;
        self._reset(mark)
        return None;

    @memoize
    def pragma(self) -> Optional[enaml_ast . Pragma]:
        # pragma: "pragma" NAME ['(' ','.pragma_arg+ ')'] NEWLINE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect("pragma"))
            and
            (a := self.name())
            and
            (args := self._tmp_7(),)
            and
            (self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . Pragma ( command = a . string , arguments = args or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def pragma_arg(self) -> Optional[enaml_ast . PragmaArg]:
        # pragma_arg: NAME | NUMBER | STRING
        mark = self._mark()
        if (
            (a := self.name())
        ):
            return enaml_ast . PragmaArg ( kind = "token" , value = a . string );
        self._reset(mark)
        if (
            (a := self.number())
        ):
            return enaml_ast . PragmaArg ( kind = "number" , value = a );
        self._reset(mark)
        if (
            (a := self.string())
        ):
            return enaml_ast . PragmaArg ( kind = "string" , value = a );
        self._reset(mark)
        return None;

    @memoize
    def storage_alias_const_expr(self) -> Optional[Any]:
        # storage_alias_const_expr: alias_expr | const_expr | storage_expr
        mark = self._mark()
        if (
            (alias_expr := self.alias_expr())
        ):
            return alias_expr;
        self._reset(mark)
        if (
            (const_expr := self.const_expr())
        ):
            return const_expr;
        self._reset(mark)
        if (
            (storage_expr := self.storage_expr())
        ):
            return storage_expr;
        self._reset(mark)
        return None;

    @memoize
    def alias_expr(self) -> Optional[enaml_ast . AliasExpr]:
        # alias_expr: "alias" NAME [':' '.'.NAME+] NEWLINE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect("alias"))
            and
            (a := self.name())
            and
            (b := self._tmp_8(),)
            and
            (self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . AliasExpr ( name = a . string , target = b [0] . string if b else a . string , chain = tuple ( p . string for p in b [1 :] ) if b else ( ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def const_expr(self) -> Optional[enaml_ast . ConstExpr]:
        # const_expr: "const" NAME [':' dec_primary] &'=' operator_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect("const"))
            and
            (a := self.name())
            and
            (b := self._tmp_9(),)
            and
            (self.positive_lookahead(self.expect, '='))
            and
            (d := self.operator_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . ConstExpr ( name = a . string , typename = b , expr = d . value , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def storage_expr(self) -> Optional[enaml_ast . StorageExpr]:
        # storage_expr: ("attr" | "event") NAME [':' dec_primary] NEWLINE | ("attr" | "event") NAME [':' dec_primary] operator_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._tmp_10())
            and
            (b := self.name())
            and
            (c := self._tmp_11(),)
            and
            (self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . StorageExpr ( name = b . string , kind = a . string , typename = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self._tmp_12())
            and
            (b := self.name())
            and
            (c := self._tmp_13(),)
            and
            (e := self.operator_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . StorageExpr ( name = b . string , kind = a . string , typename = c , expr = e , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def child_def(self) -> Optional[enaml_ast . ChildDef]:
        # child_def: NAME ':' child_def_body | NAME ':' NAME ':' child_def_body
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (self.expect(':'))
            and
            (c := self.child_def_body())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . ChildDef ( typename = a . string , identifier = "" , body = [x for x in c if not isinstance ( x , ast . Pass )] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.name())
            and
            (self.expect(':'))
            and
            (b := self.name())
            and
            (self.expect(':'))
            and
            (c := self.child_def_body())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . ChildDef ( typename = a . string , identifier = b . string , body = [x for x in c if not isinstance ( x , ast . Pass )] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def child_def_body(self) -> Optional[list]:
        # child_def_body: NEWLINE INDENT child_def_item+ DEDENT | child_def_simple_item | invalid_block
        mark = self._mark()
        if (
            (self.expect('NEWLINE'))
            and
            (self.expect('INDENT'))
            and
            (a := self._loop1_14())
            and
            (self.expect('DEDENT'))
        ):
            return a;
        self._reset(mark)
        if (
            (a := self.child_def_simple_item())
        ):
            return [a];
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_block())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def child_def_item(self) -> Optional[Any]:
        # child_def_item: child_def_simple_item | decl_funcdef | child_def | template_inst
        mark = self._mark()
        if (
            (child_def_simple_item := self.child_def_simple_item())
        ):
            return child_def_simple_item;
        self._reset(mark)
        if (
            (decl_funcdef := self.decl_funcdef())
        ):
            return decl_funcdef;
        self._reset(mark)
        if (
            (child_def := self.child_def())
        ):
            return child_def;
        self._reset(mark)
        if (
            (template_inst := self.template_inst())
        ):
            return template_inst;
        self._reset(mark)
        return None;

    @memoize
    def child_def_simple_item(self) -> Optional[Any]:
        # child_def_simple_item: binding | ex_binding | alias_expr | storage_expr | 'pass' NEWLINE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (binding := self.binding())
        ):
            return binding;
        self._reset(mark)
        if (
            (ex_binding := self.ex_binding())
        ):
            return ex_binding;
        self._reset(mark)
        if (
            (alias_expr := self.alias_expr())
        ):
            return alias_expr;
        self._reset(mark)
        if (
            (storage_expr := self.storage_expr())
        ):
            return storage_expr;
        self._reset(mark)
        if (
            (self.expect('pass'))
            and
            (self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Pass ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def binding(self) -> Optional[enaml_ast . Binding]:
        # binding: NAME operator_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (b := self.operator_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . Binding ( name = a . string , expr = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def ex_binding(self) -> Optional[enaml_ast . ExBinding]:
        # ex_binding: '.'.NAME+ operator_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._gather_15())
            and
            (b := self.operator_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . ExBinding ( chain = tuple ( p . string for p in a ) , expr = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def operator_expr(self) -> Optional[Any]:
        # operator_expr: ('=' | '<<') py_expr NEWLINE | ('>>' | ':=') py_expr NEWLINE | ':' ':' block | '<<' block
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._tmp_17())
            and
            (b := self.py_expr())
            and
            (self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . OperatorExpr ( operator = a . string , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self._tmp_18())
            and
            (b := self.py_expr())
            and
            (self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . OperatorExpr ( operator = a . string , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if isinstance ( b . ast . body , self . INVERTABLE ) else self . raise_syntax_error_known_location ( "can't assign to expression of this form" , b );
        self._reset(mark)
        if (
            (a := self.expect(':'))
            and
            (b := self.expect(':'))
            and
            (c := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . OperatorExpr ( operator = '::' , value = self . create_python_func_for_operator ( c , self . NOTIFICATION_DISALLOWED , '%s not allowed in a notification block' ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if a . end == b . start else self . raise_syntax_error_known_range ( "invalid syntax. Did you mean '::' ?" , a , b );
        self._reset(mark)
        if (
            (self.expect('<<'))
            and
            (a := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . OperatorExpr ( operator = '<<' , value = self . create_python_func_for_operator ( a , self . SUBSCRIPTION_DISALLOWED , '%s not allowed in a subscription block' ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def py_expr(self) -> Optional[enaml_ast . PythonExpression]:
        # py_expr: expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . PythonExpression ( ast = ast . Expression ( body = a ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def decl_funcdef(self) -> Optional[Any]:
        # decl_funcdef: 'async' sync_decl_fundef | sync_decl_fundef
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('async'))
            and
            (a := self.sync_decl_fundef())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . AsyncFuncDef ( funcdef = ( ast . AsyncFunctionDef ( name = a . funcdef . name , args = a . funcdef . args , returns = a . funcdef . returns , body = a . funcdef . body , decorator_list = a . funcdef . decorator_list , type_params = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) if sys . version_info >= ( 3 , 12 ) else ast . AsyncFunctionDef ( name = a . funcdef . name , args = a . funcdef . args , returns = a . funcdef . returns , body = a . funcdef . body , decorator_list = a . funcdef . decorator_list , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) ) , is_override = a . is_override , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (sync_decl_fundef := self.sync_decl_fundef())
        ):
            return sync_decl_fundef;
        self._reset(mark)
        return None;

    @memoize
    def sync_decl_fundef(self) -> Optional[Any]:
        # sync_decl_fundef: "func" NAME '(' params? ')' ['->' expression] &&':' block | NAME '=' '>' '(' params? ')' ['->' expression] &&':' block
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect("func"))
            and
            (a := self.name())
            and
            (self.expect('('))
            and
            (b := self.params(),)
            and
            (self.expect(')'))
            and
            (r := self._tmp_19(),)
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (c := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . FuncDef ( funcdef = ( ast . FunctionDef ( name = a . string , args = b or self . make_arguments ( None , [] , None , [] , None ) , returns = r , body = self . validate_decl_func_body ( c ) , decorator_list = [] , type_params = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 12 ) else ast . FunctionDef ( name = a . string , args = b or self . make_arguments ( None , [] , None , [] , None ) , returns = r , body = self . validate_decl_func_body ( c ) , decorator_list = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) ) , is_override = False , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.name())
            and
            (x := self.expect('='))
            and
            (y := self.expect('>'))
            and
            (self.expect('('))
            and
            (b := self.params(),)
            and
            (self.expect(')'))
            and
            (r := self._tmp_20(),)
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (c := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . FuncDef ( funcdef = ( ast . FunctionDef ( name = a . string , args = b or self . make_arguments ( None , [] , None , [] , None ) , returns = r , body = self . validate_decl_func_body ( c ) , decorator_list = [] , type_params = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 12 ) else ast . FunctionDef ( name = a . string , args = b or self . make_arguments ( None , [] , None , [] , None ) , returns = r , body = self . validate_decl_func_body ( c ) , decorator_list = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) ) , is_override = True , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if x . end == y . start else self . raise_syntax_error_known_range ( "invalid syntax. Did you mean '=>' ?" , x , y );
        self._reset(mark)
        return None;

    @memoize
    def template(self) -> Optional[enaml_ast . Template]:
        # template: pragmas? "template" NAME '(' template_params? ')' &&':' template_body
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.pragmas(),)
            and
            (self.expect("template"))
            and
            (b := self.name())
            and
            (self.expect('('))
            and
            (c := self.template_params(),)
            and
            (self.expect(')'))
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (d := self.template_body())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . validate_template ( enaml_ast . Template ( name = b . string , parameters = ( c or enaml_ast . TemplateParameters ( positional = [] , keywords = [] , starparam = "" ) ) , docstring = d [0] , body = [i for i in d [1] if not isinstance ( i , ast . Pass )] , pragmas = a or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) );
        self._reset(mark)
        return None;

    @memoize
    def template_body(self) -> Optional[Tuple [str , list]]:
        # template_body: NEWLINE INDENT template_item+ DEDENT | NEWLINE INDENT STRING NEWLINE template_item+ DEDENT | template_simple_item | invalid_block
        mark = self._mark()
        if (
            (self.expect('NEWLINE'))
            and
            (self.expect('INDENT'))
            and
            (a := self._loop1_21())
            and
            (self.expect('DEDENT'))
        ):
            return "" , a;
        self._reset(mark)
        if (
            (self.expect('NEWLINE'))
            and
            (self.expect('INDENT'))
            and
            (d := self.string())
            and
            (self.expect('NEWLINE'))
            and
            (a := self._loop1_22())
            and
            (self.expect('DEDENT'))
        ):
            return d . string , a;
        self._reset(mark)
        if (
            (a := self.template_simple_item())
        ):
            return "" , [a];
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_block())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def template_item(self) -> Optional[Any]:
        # template_item: template_simple_item | child_def | template_inst
        mark = self._mark()
        if (
            (template_simple_item := self.template_simple_item())
        ):
            return template_simple_item;
        self._reset(mark)
        if (
            (child_def := self.child_def())
        ):
            return child_def;
        self._reset(mark)
        if (
            (template_inst := self.template_inst())
        ):
            return template_inst;
        self._reset(mark)
        return None;

    @memoize
    def template_simple_item(self) -> Optional[Any]:
        # template_simple_item: const_expr | 'pass' NEWLINE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (const_expr := self.const_expr())
        ):
            return const_expr;
        self._reset(mark)
        if (
            (self.expect('pass'))
            and
            (self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Pass ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def template_params(self) -> Optional[Any]:
        # template_params: ','.template_param+ [',' '*' NAME] | '*' NAME
        mark = self._mark()
        if (
            (a := self._gather_23())
            and
            (b := self._tmp_25(),)
        ):
            return enaml_ast . TemplateParameters ( ** self . validate_template_paramlist ( a , b . string if b else "" ) );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (b := self.name())
        ):
            return enaml_ast . TemplateParameters ( ** self . validate_template_paramlist ( [] , b . string ) );
        self._reset(mark)
        return None;

    @memoize
    def template_param(self) -> Optional[Any]:
        # template_param: NAME ':' expression | NAME '=' expression | NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (self.expect(':'))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . PositionalParameter ( name = a . string , specialization = enaml_ast . PythonExpression ( ast = ast . Expression ( body = b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        if (
            (a := self.name())
            and
            (self.expect('='))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . KeywordParameter ( name = a . string , default = enaml_ast . PythonExpression ( ast = ast . Expression ( body = b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . PositionalParameter ( name = a . string , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def template_inst(self) -> Optional[Any]:
        # template_inst: pragmas? NAME '(' template_args? ')' [':' template_ids] ':' template_inst_body
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.pragmas(),)
            and
            (b := self.name())
            and
            (self.expect('('))
            and
            (c := self.template_args(),)
            and
            (self.expect(')'))
            and
            (d := self._tmp_26(),)
            and
            (self.expect(':'))
            and
            (e := self.template_inst_body())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . validate_template_inst ( enaml_ast . TemplateInst ( name = b . string , arguments = ( c or enaml_ast . TemplateArguments ( args = [] , stararg = None ) ) , identifiers = d , pragmas = a or [] , body = [i for i in e if not isinstance ( i , ast . Pass )] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) );
        self._reset(mark)
        return None;

    @memoize
    def template_args(self) -> Optional[Any]:
        # template_args: ','.template_argument+ [',' '*' expression] | '*' expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._gather_27())
            and
            (b := self._tmp_29(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateArguments ( args = a , stararg = ( enaml_ast . PythonExpression ( ast = ast . Expression ( body = b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) if b else None ) , );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateArguments ( args = [] , stararg = enaml_ast . PythonExpression ( ast = ast . Expression ( body = b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) , );
        self._reset(mark)
        return None;

    @memoize
    def template_argument(self) -> Optional[Any]:
        # template_argument: expression | expression for_if_clauses
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . PythonExpression ( ast = ast . Expression ( body = a ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        if (
            (a := self.expression())
            and
            (b := self.for_if_clauses())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . PythonExpression ( ast . GeneratorExp ( elt = a , generators = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        return None;

    @memoize
    def template_ids(self) -> Optional[Any]:
        # template_ids: ','.NAME+ [',' '*' NAME] | '*' NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._gather_30())
            and
            (b := self._tmp_32(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateIdentifiers ( names = [p . string for p in a] , starname = b . string if b else "" , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (b := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateIdentifiers ( names = [] , starname = b . string , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def template_inst_body(self) -> Optional[Any]:
        # template_inst_body: NEWLINE INDENT template_inst_item+ DEDENT | template_inst_item | invalid_block
        mark = self._mark()
        if (
            (self.expect('NEWLINE'))
            and
            (self.expect('INDENT'))
            and
            (a := self._loop1_33())
            and
            (self.expect('DEDENT'))
        ):
            return a;
        self._reset(mark)
        if (
            (a := self.template_inst_item())
        ):
            return [a];
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_block())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def template_inst_item(self) -> Optional[Any]:
        # template_inst_item: NAME ['.' '.'.NAME+] operator_expr | 'pass' NEWLINE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (b := self._tmp_34(),)
            and
            (c := self.operator_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateInstBinding ( name = a . string , chain = tuple ( p . string for p in b ) if b else ( ) , expr = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        if (
            (self.expect('pass'))
            and
            (self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Pass ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def statements(self) -> Optional[list]:
        # statements: statement+
        mark = self._mark()
        if (
            (a := self._loop1_35())
        ):
            return list ( itertools . chain . from_iterable ( a ) );
        self._reset(mark)
        return None;

    @memoize
    def statement(self) -> Optional[list]:
        # statement: compound_stmt | simple_stmts
        mark = self._mark()
        if (
            (a := self.compound_stmt())
        ):
            return [a];
        self._reset(mark)
        if (
            (a := self.simple_stmts())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def statement_newline(self) -> Optional[list]:
        # statement_newline: compound_stmt NEWLINE | simple_stmts | NEWLINE | $
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.compound_stmt())
            and
            (self.expect('NEWLINE'))
        ):
            return [a];
        self._reset(mark)
        if (
            (simple_stmts := self.simple_stmts())
        ):
            return simple_stmts;
        self._reset(mark)
        if (
            (self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return [ast . Pass ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )];
        self._reset(mark)
        if (
            (self.expect('ENDMARKER'))
        ):
            return None;
        self._reset(mark)
        return None;

    @memoize
    def simple_stmts(self) -> Optional[list]:
        # simple_stmts: simple_stmt !';' NEWLINE | ';'.simple_stmt+ ';'? NEWLINE
        mark = self._mark()
        if (
            (a := self.simple_stmt())
            and
            (self.negative_lookahead(self.expect, ';'))
            and
            (self.expect('NEWLINE'))
        ):
            return [a];
        self._reset(mark)
        if (
            (a := self._gather_36())
            and
            (self.expect(';'),)
            and
            (self.expect('NEWLINE'))
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def simple_stmt(self) -> Optional[Any]:
        # simple_stmt: assignment | &"type" type_alias | star_expressions | &'return' return_stmt | &('import' | 'from') import_stmt | &'raise' raise_stmt | 'pass' | &'del' del_stmt | &'yield' yield_stmt | &'assert' assert_stmt | 'break' | 'continue' | &'global' global_stmt | &'nonlocal' nonlocal_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (assignment := self.assignment())
        ):
            return assignment;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, "type"))
            and
            (type_alias := self.type_alias())
        ):
            return type_alias;
        self._reset(mark)
        if (
            (e := self.star_expressions())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Expr ( value = e , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'return'))
            and
            (return_stmt := self.return_stmt())
        ):
            return return_stmt;
        self._reset(mark)
        if (
            (self.positive_lookahead(self._tmp_38, ))
            and
            (import_stmt := self.import_stmt())
        ):
            return import_stmt;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'raise'))
            and
            (raise_stmt := self.raise_stmt())
        ):
            return raise_stmt;
        self._reset(mark)
        if (
            (self.expect('pass'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Pass ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'del'))
            and
            (del_stmt := self.del_stmt())
        ):
            return del_stmt;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'yield'))
            and
            (yield_stmt := self.yield_stmt())
        ):
            return yield_stmt;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'assert'))
            and
            (assert_stmt := self.assert_stmt())
        ):
            return assert_stmt;
        self._reset(mark)
        if (
            (self.expect('break'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Break ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('continue'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Continue ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'global'))
            and
            (global_stmt := self.global_stmt())
        ):
            return global_stmt;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'nonlocal'))
            and
            (nonlocal_stmt := self.nonlocal_stmt())
        ):
            return nonlocal_stmt;
        self._reset(mark)
        return None;

    @memoize
    def compound_stmt(self) -> Optional[Any]:
        # compound_stmt: &('def' | '@' | 'async') function_def | &'if' if_stmt | &('class' | '@') class_def | &('with' | 'async') with_stmt | &('for' | 'async') for_stmt | &'try' try_stmt | &'while' while_stmt | match_stmt
        mark = self._mark()
        if (
            (self.positive_lookahead(self._tmp_39, ))
            and
            (function_def := self.function_def())
        ):
            return function_def;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'if'))
            and
            (if_stmt := self.if_stmt())
        ):
            return if_stmt;
        self._reset(mark)
        if (
            (self.positive_lookahead(self._tmp_40, ))
            and
            (class_def := self.class_def())
        ):
            return class_def;
        self._reset(mark)
        if (
            (self.positive_lookahead(self._tmp_41, ))
            and
            (with_stmt := self.with_stmt())
        ):
            return with_stmt;
        self._reset(mark)
        if (
            (self.positive_lookahead(self._tmp_42, ))
            and
            (for_stmt := self.for_stmt())
        ):
            return for_stmt;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'try'))
            and
            (try_stmt := self.try_stmt())
        ):
            return try_stmt;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'while'))
            and
            (while_stmt := self.while_stmt())
        ):
            return while_stmt;
        self._reset(mark)
        if (
            (match_stmt := self.match_stmt())
        ):
            return match_stmt;
        self._reset(mark)
        return None;

    @memoize
    def assignment(self) -> Optional[Any]:
        # assignment: NAME ':' expression ['=' annotated_rhs] | ('(' single_target ')' | single_subscript_attribute_target) ':' expression ['=' annotated_rhs] | ((star_targets '='))+ (yield_expr | star_expressions) !'=' TYPE_COMMENT? | single_target augassign ~ (yield_expr | star_expressions) | invalid_assignment
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (self.expect(':'))
            and
            (b := self.expression())
            and
            (c := self._tmp_43(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 6 ) , "Variable annotation syntax is" , ast . AnnAssign ( target = ast . Name ( id = a . string , ctx = Store , lineno = a . start [0] , col_offset = a . start [1] , end_lineno = a . end [0] , end_col_offset = a . end [1] , ) , annotation = b , value = c , simple = 1 , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) );
        self._reset(mark)
        if (
            (a := self._tmp_44())
            and
            (self.expect(':'))
            and
            (b := self.expression())
            and
            (c := self._tmp_45(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 6 ) , "Variable annotation syntax is" , ast . AnnAssign ( target = a , annotation = b , value = c , simple = 0 , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) );
        self._reset(mark)
        if (
            (a := self._loop1_46())
            and
            (b := self._tmp_47())
            and
            (self.negative_lookahead(self.expect, '='))
            and
            (tc := self.type_comment(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Assign ( targets = a , value = b , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        cut = False
        if (
            (a := self.single_target())
            and
            (b := self.augassign())
            and
            (cut := True)
            and
            (c := self._tmp_48())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . AugAssign ( target = a , op = b , value = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if cut:
            return None;
        if (
            self.call_invalid_rules
            and
            (self.invalid_assignment())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def annotated_rhs(self) -> Optional[Any]:
        # annotated_rhs: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def augassign(self) -> Optional[Any]:
        # augassign: '+=' | '-=' | '*=' | '@=' | '/=' | '%=' | '&=' | '|=' | '^=' | '<<=' | '>>=' | '**=' | '//='
        mark = self._mark()
        if (
            (self.expect('+='))
        ):
            return ast . Add ( );
        self._reset(mark)
        if (
            (self.expect('-='))
        ):
            return ast . Sub ( );
        self._reset(mark)
        if (
            (self.expect('*='))
        ):
            return ast . Mult ( );
        self._reset(mark)
        if (
            (self.expect('@='))
        ):
            return self . check_version ( ( 3 , 5 ) , "The '@' operator is" , ast . MatMult ( ) );
        self._reset(mark)
        if (
            (self.expect('/='))
        ):
            return ast . Div ( );
        self._reset(mark)
        if (
            (self.expect('%='))
        ):
            return ast . Mod ( );
        self._reset(mark)
        if (
            (self.expect('&='))
        ):
            return ast . BitAnd ( );
        self._reset(mark)
        if (
            (self.expect('|='))
        ):
            return ast . BitOr ( );
        self._reset(mark)
        if (
            (self.expect('^='))
        ):
            return ast . BitXor ( );
        self._reset(mark)
        if (
            (self.expect('<<='))
        ):
            return ast . LShift ( );
        self._reset(mark)
        if (
            (self.expect('>>='))
        ):
            return ast . RShift ( );
        self._reset(mark)
        if (
            (self.expect('**='))
        ):
            return ast . Pow ( );
        self._reset(mark)
        if (
            (self.expect('//='))
        ):
            return ast . FloorDiv ( );
        self._reset(mark)
        return None;

    @memoize
    def return_stmt(self) -> Optional[ast . Return]:
        # return_stmt: 'return' star_expressions?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('return'))
            and
            (a := self.star_expressions(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Return ( value = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def raise_stmt(self) -> Optional[ast . Raise]:
        # raise_stmt: 'raise' expression ['from' expression] | 'raise'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('raise'))
            and
            (a := self.expression())
            and
            (b := self._tmp_49(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Raise ( exc = a , cause = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('raise'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Raise ( exc = None , cause = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def global_stmt(self) -> Optional[ast . Global]:
        # global_stmt: 'global' ','.NAME+
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('global'))
            and
            (a := self._gather_50())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Global ( names = [n . string for n in a] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def nonlocal_stmt(self) -> Optional[ast . Nonlocal]:
        # nonlocal_stmt: 'nonlocal' ','.NAME+
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('nonlocal'))
            and
            (a := self._gather_52())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Nonlocal ( names = [n . string for n in a] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def del_stmt(self) -> Optional[ast . Delete]:
        # del_stmt: 'del' del_targets &(';' | NEWLINE) | invalid_del_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('del'))
            and
            (a := self.del_targets())
            and
            (self.positive_lookahead(self._tmp_54, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Delete ( targets = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_del_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def yield_stmt(self) -> Optional[ast . Expr]:
        # yield_stmt: yield_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (y := self.yield_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Expr ( value = y , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def assert_stmt(self) -> Optional[ast . Assert]:
        # assert_stmt: 'assert' expression [',' expression]
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('assert'))
            and
            (a := self.expression())
            and
            (b := self._tmp_55(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Assert ( test = a , msg = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def import_stmt(self) -> Optional[ast . Import]:
        # import_stmt: invalid_import | import_name | import_from
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.invalid_import())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (import_name := self.import_name())
        ):
            return import_name;
        self._reset(mark)
        if (
            (import_from := self.import_from())
        ):
            return import_from;
        self._reset(mark)
        return None;

    @memoize
    def import_name(self) -> Optional[ast . Import]:
        # import_name: 'import' dotted_as_names
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('import'))
            and
            (a := self.dotted_as_names())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Import ( names = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def import_from(self) -> Optional[ast . ImportFrom]:
        # import_from: 'from' (('.' | '...'))* dotted_name 'import' import_from_targets | 'from' (('.' | '...'))+ 'import' import_from_targets
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('from'))
            and
            (a := self._loop0_56(),)
            and
            (b := self.dotted_name())
            and
            (self.expect('import'))
            and
            (c := self.import_from_targets())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ImportFrom ( module = b , names = c , level = self . extract_import_level ( a ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('from'))
            and
            (a := self._loop1_57())
            and
            (self.expect('import'))
            and
            (b := self.import_from_targets())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ImportFrom ( names = b , level = self . extract_import_level ( a ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 9 ) else ast . ImportFrom ( module = None , names = b , level = self . extract_import_level ( a ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def import_from_targets(self) -> Optional[List [ast . alias]]:
        # import_from_targets: '(' import_from_as_names ','? ')' | import_from_as_names !',' | '*' | invalid_import_from_targets
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('('))
            and
            (a := self.import_from_as_names())
            and
            (self.expect(','),)
            and
            (self.expect(')'))
        ):
            return a;
        self._reset(mark)
        if (
            (import_from_as_names := self.import_from_as_names())
            and
            (self.negative_lookahead(self.expect, ','))
        ):
            return import_from_as_names;
        self._reset(mark)
        if (
            (self.expect('*'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return [ast . alias ( name = "*" , asname = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )];
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_import_from_targets())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def import_from_as_names(self) -> Optional[List [ast . alias]]:
        # import_from_as_names: ','.import_from_as_name+
        mark = self._mark()
        if (
            (a := self._gather_58())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def import_from_as_name(self) -> Optional[ast . alias]:
        # import_from_as_name: NAME ['as' NAME]
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (b := self._tmp_60(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . alias ( name = a . string , asname = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def dotted_as_names(self) -> Optional[List [ast . alias]]:
        # dotted_as_names: ','.dotted_as_name+
        mark = self._mark()
        if (
            (a := self._gather_61())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def dotted_as_name(self) -> Optional[ast . alias]:
        # dotted_as_name: dotted_name ['as' NAME]
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.dotted_name())
            and
            (b := self._tmp_63(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . alias ( name = a , asname = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize_left_rec
    def dotted_name(self) -> Optional[str]:
        # dotted_name: dotted_name '.' NAME | NAME
        mark = self._mark()
        if (
            (a := self.dotted_name())
            and
            (self.expect('.'))
            and
            (b := self.name())
        ):
            return a + "." + b . string;
        self._reset(mark)
        if (
            (a := self.name())
        ):
            return a . string;
        self._reset(mark)
        return None;

    @memoize
    def block(self) -> Optional[list]:
        # block: NEWLINE INDENT statements DEDENT | simple_stmts | invalid_block
        mark = self._mark()
        if (
            (self.expect('NEWLINE'))
            and
            (self.expect('INDENT'))
            and
            (a := self.statements())
            and
            (self.expect('DEDENT'))
        ):
            return a;
        self._reset(mark)
        if (
            (simple_stmts := self.simple_stmts())
        ):
            return simple_stmts;
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_block())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def decorators(self) -> Optional[Any]:
        # decorators: decorator+
        mark = self._mark()
        if (
            (_loop1_64 := self._loop1_64())
        ):
            return _loop1_64;
        self._reset(mark)
        return None;

    @memoize
    def decorator(self) -> Optional[Any]:
        # decorator: ('@' dec_maybe_call NEWLINE) | ('@' named_expression NEWLINE)
        mark = self._mark()
        if (
            (a := self._tmp_65())
        ):
            return a;
        self._reset(mark)
        if (
            (a := self._tmp_66())
        ):
            return self . check_version ( ( 3 , 9 ) , "Generic decorator are" , a );
        self._reset(mark)
        return None;

    @memoize
    def dec_maybe_call(self) -> Optional[Any]:
        # dec_maybe_call: dec_primary '(' arguments? ')' | dec_primary
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (dn := self.dec_primary())
            and
            (self.expect('('))
            and
            (z := self.arguments(),)
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Call ( func = dn , args = z [0] if z else [] , keywords = z [1] if z else [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (dec_primary := self.dec_primary())
        ):
            return dec_primary;
        self._reset(mark)
        return None;

    @memoize_left_rec
    def dec_primary(self) -> Optional[Any]:
        # dec_primary: dec_primary '.' NAME | NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.dec_primary())
            and
            (self.expect('.'))
            and
            (b := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = a . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def class_def(self) -> Optional[ast . ClassDef]:
        # class_def: decorators class_def_raw | class_def_raw
        mark = self._mark()
        if (
            (a := self.decorators())
            and
            (b := self.class_def_raw())
        ):
            return self . set_decorators ( b , a );
        self._reset(mark)
        if (
            (class_def_raw := self.class_def_raw())
        ):
            return class_def_raw;
        self._reset(mark)
        return None;

    @memoize
    def class_def_raw(self) -> Optional[ast . ClassDef]:
        # class_def_raw: invalid_class_def_raw | 'class' NAME type_params? ['(' arguments? ')'] &&':' block
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_class_def_raw())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('class'))
            and
            (a := self.name())
            and
            (t := self.type_params(),)
            and
            (b := self._tmp_67(),)
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (c := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ( ast . ClassDef ( a . string , bases = b [0] if b else [] , keywords = b [1] if b else [] , body = c , decorator_list = [] , type_params = t or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) if sys . version_info >= ( 3 , 12 ) else ast . ClassDef ( a . string , bases = b [0] if b else [] , keywords = b [1] if b else [] , body = c , decorator_list = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) );
        self._reset(mark)
        return None;

    @memoize
    def function_def(self) -> Optional[Union [ast . FunctionDef , ast . AsyncFunctionDef]]:
        # function_def: decorators function_def_raw | function_def_raw
        mark = self._mark()
        if (
            (d := self.decorators())
            and
            (f := self.function_def_raw())
        ):
            return self . set_decorators ( f , d );
        self._reset(mark)
        if (
            (f := self.function_def_raw())
        ):
            return self . set_decorators ( f , [] );
        self._reset(mark)
        return None;

    @memoize
    def function_def_raw(self) -> Optional[Union [ast . FunctionDef , ast . AsyncFunctionDef]]:
        # function_def_raw: invalid_def_raw | 'def' NAME type_params? &&'(' params? ')' ['->' expression] &&':' func_type_comment? block | 'async' 'def' NAME type_params? &&'(' params? ')' ['->' expression] &&':' func_type_comment? block
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_def_raw())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('def'))
            and
            (n := self.name())
            and
            (t := self.type_params(),)
            and
            (self.expect_forced(self.expect('('), "'('"))
            and
            (params := self.params(),)
            and
            (self.expect(')'))
            and
            (a := self._tmp_68(),)
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (tc := self.func_type_comment(),)
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ( ast . FunctionDef ( name = n . string , args = params or self . make_arguments ( None , [] , None , [] , None ) , returns = a , body = b , type_comment = tc , type_params = t or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) if sys . version_info >= ( 3 , 12 ) else ast . FunctionDef ( name = n . string , args = params or self . make_arguments ( None , [] , None , [] , None ) , returns = a , body = b , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) );
        self._reset(mark)
        if (
            (self.expect('async'))
            and
            (self.expect('def'))
            and
            (n := self.name())
            and
            (t := self.type_params(),)
            and
            (self.expect_forced(self.expect('('), "'('"))
            and
            (params := self.params(),)
            and
            (self.expect(')'))
            and
            (a := self._tmp_69(),)
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (tc := self.func_type_comment(),)
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ( self . check_version ( ( 3 , 5 ) , "Async functions are" , ast . AsyncFunctionDef ( name = n . string , args = params or self . make_arguments ( None , [] , None , [] , None ) , returns = a , body = b , type_comment = tc , type_params = t or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) ) if sys . version_info >= ( 3 , 12 ) else self . check_version ( ( 3 , 5 ) , "Async functions are" , ast . AsyncFunctionDef ( name = n . string , args = params or self . make_arguments ( None , [] , None , [] , None ) , returns = a , body = b , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) ) );
        self._reset(mark)
        return None;

    @memoize
    def params(self) -> Optional[Any]:
        # params: invalid_parameters | parameters
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.invalid_parameters())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (parameters := self.parameters())
        ):
            return parameters;
        self._reset(mark)
        return None;

    @memoize
    def parameters(self) -> Optional[ast . arguments]:
        # parameters: slash_no_default param_no_default* param_with_default* star_etc? | slash_with_default param_with_default* star_etc? | param_no_default+ param_with_default* star_etc? | param_with_default+ star_etc? | star_etc
        mark = self._mark()
        if (
            (a := self.slash_no_default())
            and
            (b := self._loop0_70(),)
            and
            (c := self._loop0_71(),)
            and
            (d := self.star_etc(),)
        ):
            return self . check_version ( ( 3 , 8 ) , "Positional only arguments are" , self . make_arguments ( a , [] , b , c , d ) );
        self._reset(mark)
        if (
            (a := self.slash_with_default())
            and
            (b := self._loop0_72(),)
            and
            (c := self.star_etc(),)
        ):
            return self . check_version ( ( 3 , 8 ) , "Positional only arguments are" , self . make_arguments ( None , a , None , b , c ) , );
        self._reset(mark)
        if (
            (a := self._loop1_73())
            and
            (b := self._loop0_74(),)
            and
            (c := self.star_etc(),)
        ):
            return self . make_arguments ( None , [] , a , b , c );
        self._reset(mark)
        if (
            (a := self._loop1_75())
            and
            (b := self.star_etc(),)
        ):
            return self . make_arguments ( None , [] , None , a , b );
        self._reset(mark)
        if (
            (a := self.star_etc())
        ):
            return self . make_arguments ( None , [] , None , None , a );
        self._reset(mark)
        return None;

    @memoize
    def slash_no_default(self) -> Optional[List [Tuple [ast . arg , None]]]:
        # slash_no_default: param_no_default+ '/' ',' | param_no_default+ '/' &')'
        mark = self._mark()
        if (
            (a := self._loop1_76())
            and
            (self.expect('/'))
            and
            (self.expect(','))
        ):
            return [( p , None ) for p in a];
        self._reset(mark)
        if (
            (a := self._loop1_77())
            and
            (self.expect('/'))
            and
            (self.positive_lookahead(self.expect, ')'))
        ):
            return [( p , None ) for p in a];
        self._reset(mark)
        return None;

    @memoize
    def slash_with_default(self) -> Optional[List [Tuple [ast . arg , Any]]]:
        # slash_with_default: param_no_default* param_with_default+ '/' ',' | param_no_default* param_with_default+ '/' &')'
        mark = self._mark()
        if (
            (a := self._loop0_78(),)
            and
            (b := self._loop1_79())
            and
            (self.expect('/'))
            and
            (self.expect(','))
        ):
            return ( [( p , None ) for p in a] if a else [] ) + b;
        self._reset(mark)
        if (
            (a := self._loop0_80(),)
            and
            (b := self._loop1_81())
            and
            (self.expect('/'))
            and
            (self.positive_lookahead(self.expect, ')'))
        ):
            return ( [( p , None ) for p in a] if a else [] ) + b;
        self._reset(mark)
        return None;

    @memoize
    def star_etc(self) -> Optional[Tuple [Optional [ast . arg] , List [Tuple [ast . arg , Any]] , Optional [ast . arg]]]:
        # star_etc: invalid_star_etc | '*' param_no_default param_maybe_default* kwds? | '*' param_no_default_star_annotation param_maybe_default* kwds? | '*' ',' param_maybe_default+ kwds? | kwds
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.invalid_star_etc())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (a := self.param_no_default())
            and
            (b := self._loop0_82(),)
            and
            (c := self.kwds(),)
        ):
            return ( a , b , c );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (a := self.param_no_default_star_annotation())
            and
            (b := self._loop0_83(),)
            and
            (c := self.kwds(),)
        ):
            return ( a , b , c );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (self.expect(','))
            and
            (b := self._loop1_84())
            and
            (c := self.kwds(),)
        ):
            return ( None , b , c );
        self._reset(mark)
        if (
            (a := self.kwds())
        ):
            return ( None , [] , a );
        self._reset(mark)
        return None;

    @memoize
    def kwds(self) -> Optional[ast . arg]:
        # kwds: invalid_kwds | '**' param_no_default
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.invalid_kwds())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('**'))
            and
            (a := self.param_no_default())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def param_no_default(self) -> Optional[ast . arg]:
        # param_no_default: param ',' TYPE_COMMENT? | param TYPE_COMMENT? &')'
        mark = self._mark()
        if (
            (a := self.param())
            and
            (self.expect(','))
            and
            (tc := self.type_comment(),)
        ):
            return self . set_arg_type_comment ( a , tc );
        self._reset(mark)
        if (
            (a := self.param())
            and
            (tc := self.type_comment(),)
            and
            (self.positive_lookahead(self.expect, ')'))
        ):
            return self . set_arg_type_comment ( a , tc );
        self._reset(mark)
        return None;

    @memoize
    def param_no_default_star_annotation(self) -> Optional[ast . arg]:
        # param_no_default_star_annotation: param_star_annotation ',' TYPE_COMMENT? | param_star_annotation TYPE_COMMENT? &')'
        mark = self._mark()
        if (
            (a := self.param_star_annotation())
            and
            (self.expect(','))
            and
            (tc := self.type_comment(),)
        ):
            return self . set_arg_type_comment ( a , tc );
        self._reset(mark)
        if (
            (a := self.param_star_annotation())
            and
            (tc := self.type_comment(),)
            and
            (self.positive_lookahead(self.expect, ')'))
        ):
            return self . set_arg_type_comment ( a , tc );
        self._reset(mark)
        return None;

    @memoize
    def param_with_default(self) -> Optional[Tuple [ast . arg , Any]]:
        # param_with_default: param default ',' TYPE_COMMENT? | param default TYPE_COMMENT? &')'
        mark = self._mark()
        if (
            (a := self.param())
            and
            (c := self.default())
            and
            (self.expect(','))
            and
            (tc := self.type_comment(),)
        ):
            return ( self . set_arg_type_comment ( a , tc ) , c );
        self._reset(mark)
        if (
            (a := self.param())
            and
            (c := self.default())
            and
            (tc := self.type_comment(),)
            and
            (self.positive_lookahead(self.expect, ')'))
        ):
            return ( self . set_arg_type_comment ( a , tc ) , c );
        self._reset(mark)
        return None;

    @memoize
    def param_maybe_default(self) -> Optional[Tuple [ast . arg , Any]]:
        # param_maybe_default: param default? ',' TYPE_COMMENT? | param default? TYPE_COMMENT? &')'
        mark = self._mark()
        if (
            (a := self.param())
            and
            (c := self.default(),)
            and
            (self.expect(','))
            and
            (tc := self.type_comment(),)
        ):
            return ( self . set_arg_type_comment ( a , tc ) , c );
        self._reset(mark)
        if (
            (a := self.param())
            and
            (c := self.default(),)
            and
            (tc := self.type_comment(),)
            and
            (self.positive_lookahead(self.expect, ')'))
        ):
            return ( self . set_arg_type_comment ( a , tc ) , c );
        self._reset(mark)
        return None;

    @memoize
    def param(self) -> Optional[Any]:
        # param: NAME annotation?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (b := self.annotation(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . arg ( arg = a . string , annotation = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def param_star_annotation(self) -> Optional[Any]:
        # param_star_annotation: NAME star_annotation
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (b := self.star_annotation())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . arg ( arg = a . string , annotations = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def annotation(self) -> Optional[Any]:
        # annotation: ':' expression
        mark = self._mark()
        if (
            (self.expect(':'))
            and
            (a := self.expression())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def star_annotation(self) -> Optional[Any]:
        # star_annotation: ':' star_expression
        mark = self._mark()
        if (
            (self.expect(':'))
            and
            (a := self.star_expression())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def default(self) -> Optional[Any]:
        # default: '=' expression | invalid_default
        mark = self._mark()
        if (
            (self.expect('='))
            and
            (a := self.expression())
        ):
            return a;
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_default())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def if_stmt(self) -> Optional[ast . If]:
        # if_stmt: invalid_if_stmt | 'if' named_expression ':' block elif_stmt | 'if' named_expression ':' block else_block?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_if_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('if'))
            and
            (a := self.named_expression())
            and
            (self.expect(':'))
            and
            (b := self.block())
            and
            (c := self.elif_stmt())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . If ( test = a , body = b , orelse = c or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('if'))
            and
            (a := self.named_expression())
            and
            (self.expect(':'))
            and
            (b := self.block())
            and
            (c := self.else_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . If ( test = a , body = b , orelse = c or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def elif_stmt(self) -> Optional[List [ast . If]]:
        # elif_stmt: invalid_elif_stmt | 'elif' named_expression ':' block elif_stmt | 'elif' named_expression ':' block else_block?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_elif_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('elif'))
            and
            (a := self.named_expression())
            and
            (self.expect(':'))
            and
            (b := self.block())
            and
            (c := self.elif_stmt())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return [ast . If ( test = a , body = b , orelse = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )];
        self._reset(mark)
        if (
            (self.expect('elif'))
            and
            (a := self.named_expression())
            and
            (self.expect(':'))
            and
            (b := self.block())
            and
            (c := self.else_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return [ast . If ( test = a , body = b , orelse = c or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )];
        self._reset(mark)
        return None;

    @memoize
    def else_block(self) -> Optional[list]:
        # else_block: invalid_else_stmt | 'else' &&':' block
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.invalid_else_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('else'))
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.block())
        ):
            return b;
        self._reset(mark)
        return None;

    @memoize
    def while_stmt(self) -> Optional[ast . While]:
        # while_stmt: invalid_while_stmt | 'while' named_expression ':' block else_block?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_while_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('while'))
            and
            (a := self.named_expression())
            and
            (self.expect(':'))
            and
            (b := self.block())
            and
            (c := self.else_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . While ( test = a , body = b , orelse = c or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def for_stmt(self) -> Optional[Union [ast . For , ast . AsyncFor]]:
        # for_stmt: invalid_for_stmt | 'for' star_targets 'in' ~ star_expressions &&':' TYPE_COMMENT? block else_block? | 'async' 'for' star_targets 'in' ~ star_expressions ':' TYPE_COMMENT? block else_block? | invalid_for_target
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_for_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        cut = False
        if (
            (self.expect('for'))
            and
            (t := self.star_targets())
            and
            (self.expect('in'))
            and
            (cut := True)
            and
            (ex := self.star_expressions())
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (tc := self.type_comment(),)
            and
            (b := self.block())
            and
            (el := self.else_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . For ( target = t , iter = ex , body = b , orelse = el or [] , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if cut:
            return None;
        cut = False
        if (
            (self.expect('async'))
            and
            (self.expect('for'))
            and
            (t := self.star_targets())
            and
            (self.expect('in'))
            and
            (cut := True)
            and
            (ex := self.star_expressions())
            and
            (self.expect(':'))
            and
            (tc := self.type_comment(),)
            and
            (b := self.block())
            and
            (el := self.else_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 5 ) , "Async for loops are" , ast . AsyncFor ( target = t , iter = ex , body = b , orelse = el or [] , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) );
        self._reset(mark)
        if cut:
            return None;
        if (
            self.call_invalid_rules
            and
            (self.invalid_for_target())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def with_stmt(self) -> Optional[Union [ast . With , ast . AsyncWith]]:
        # with_stmt: invalid_with_stmt_indent | 'with' '(' ','.with_item+ ','? ')' ':' block | 'with' ','.with_item+ ':' TYPE_COMMENT? block | 'async' 'with' '(' ','.with_item+ ','? ')' ':' block | 'async' 'with' ','.with_item+ ':' TYPE_COMMENT? block | invalid_with_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_with_stmt_indent())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('with'))
            and
            (self.expect('('))
            and
            (a := self._gather_85())
            and
            (self.expect(','),)
            and
            (self.expect(')'))
            and
            (self.expect(':'))
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 9 ) , "Parenthesized with items" , ast . With ( items = a , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) );
        self._reset(mark)
        if (
            (self.expect('with'))
            and
            (a := self._gather_87())
            and
            (self.expect(':'))
            and
            (tc := self.type_comment(),)
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . With ( items = a , body = b , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('async'))
            and
            (self.expect('with'))
            and
            (self.expect('('))
            and
            (a := self._gather_89())
            and
            (self.expect(','),)
            and
            (self.expect(')'))
            and
            (self.expect(':'))
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 9 ) , "Parenthesized with items" , ast . AsyncWith ( items = a , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) );
        self._reset(mark)
        if (
            (self.expect('async'))
            and
            (self.expect('with'))
            and
            (a := self._gather_91())
            and
            (self.expect(':'))
            and
            (tc := self.type_comment(),)
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 5 ) , "Async with statements are" , ast . AsyncWith ( items = a , body = b , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_with_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def with_item(self) -> Optional[ast . withitem]:
        # with_item: expression 'as' star_target &(',' | ')' | ':') | invalid_with_item | expression
        mark = self._mark()
        if (
            (e := self.expression())
            and
            (self.expect('as'))
            and
            (t := self.star_target())
            and
            (self.positive_lookahead(self._tmp_93, ))
        ):
            return ast . withitem ( context_expr = e , optional_vars = t );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_with_item())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (e := self.expression())
        ):
            return ast . withitem ( context_expr = e , optional_vars = None );
        self._reset(mark)
        return None;

    @memoize
    def try_stmt(self) -> Optional[ast . Try]:
        # try_stmt: invalid_try_stmt | 'try' &&':' block finally_block | 'try' &&':' block except_block+ else_block? finally_block? | 'try' &&':' block except_star_block+ else_block? finally_block?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_try_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('try'))
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.block())
            and
            (f := self.finally_block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Try ( body = b , handlers = [] , orelse = [] , finalbody = f , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('try'))
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.block())
            and
            (ex := self._loop1_94())
            and
            (el := self.else_block(),)
            and
            (f := self.finally_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Try ( body = b , handlers = ex , orelse = el or [] , finalbody = f or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('try'))
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.block())
            and
            (ex := self._loop1_95())
            and
            (el := self.else_block(),)
            and
            (f := self.finally_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 11 ) , "Exception groups are" , ( ast . TryStar ( body = b , handlers = ex , orelse = el or [] , finalbody = f or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 11 ) else None ) );
        self._reset(mark)
        return None;

    @memoize
    def except_block(self) -> Optional[ast . ExceptHandler]:
        # except_block: invalid_except_stmt_indent | 'except' expression ['as' NAME] ':' block | 'except' ':' block | invalid_except_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_except_stmt_indent())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('except'))
            and
            (e := self.expression())
            and
            (t := self._tmp_96(),)
            and
            (self.expect(':'))
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ExceptHandler ( type = e , name = t , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('except'))
            and
            (self.expect(':'))
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ExceptHandler ( type = None , name = None , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_except_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def except_star_block(self) -> Optional[ast . ExceptHandler]:
        # except_star_block: invalid_except_star_stmt_indent | 'except' '*' expression ['as' NAME] ':' block | invalid_except_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_except_star_stmt_indent())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('except'))
            and
            (self.expect('*'))
            and
            (e := self.expression())
            and
            (t := self._tmp_97(),)
            and
            (self.expect(':'))
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ExceptHandler ( type = e , name = t , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_except_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def finally_block(self) -> Optional[list]:
        # finally_block: invalid_finally_stmt | 'finally' &&':' block
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.invalid_finally_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('finally'))
            and
            (self.expect_forced(self.expect(':'), "':'"))
            and
            (a := self.block())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def match_stmt(self) -> Optional["ast.Match"]:
        # match_stmt: "match" subject_expr ':' NEWLINE INDENT case_block+ DEDENT | invalid_match_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect("match"))
            and
            (subject := self.subject_expr())
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.expect('INDENT'))
            and
            (cases := self._loop1_98())
            and
            (self.expect('DEDENT'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Match ( subject = subject , cases = cases , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_match_stmt())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def subject_expr(self) -> Optional[Any]:
        # subject_expr: star_named_expression ',' star_named_expressions? | named_expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (value := self.star_named_expression())
            and
            (self.expect(','))
            and
            (values := self.star_named_expressions(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 10 ) , "Pattern matching is" , ast . Tuple ( elts = [value] + ( values or [] ) , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) );
        self._reset(mark)
        if (
            (e := self.named_expression())
        ):
            return self . check_version ( ( 3 , 10 ) , "Pattern matching is" , e );
        self._reset(mark)
        return None;

    @memoize
    def case_block(self) -> Optional["ast.match_case"]:
        # case_block: invalid_case_block | "case" patterns guard? ':' block
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.invalid_case_block())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect("case"))
            and
            (pattern := self.patterns())
            and
            (guard := self.guard(),)
            and
            (self.expect(':'))
            and
            (body := self.block())
        ):
            return ast . match_case ( pattern = pattern , guard = guard , body = body );
        self._reset(mark)
        return None;

    @memoize
    def guard(self) -> Optional[Any]:
        # guard: 'if' named_expression
        mark = self._mark()
        if (
            (self.expect('if'))
            and
            (guard := self.named_expression())
        ):
            return guard;
        self._reset(mark)
        return None;

    @memoize
    def patterns(self) -> Optional[Any]:
        # patterns: open_sequence_pattern | pattern
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (patterns := self.open_sequence_pattern())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSequence ( patterns = patterns , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (pattern := self.pattern())
        ):
            return pattern;
        self._reset(mark)
        return None;

    @memoize
    def pattern(self) -> Optional[Any]:
        # pattern: as_pattern | or_pattern
        mark = self._mark()
        if (
            (as_pattern := self.as_pattern())
        ):
            return as_pattern;
        self._reset(mark)
        if (
            (or_pattern := self.or_pattern())
        ):
            return or_pattern;
        self._reset(mark)
        return None;

    @memoize
    def as_pattern(self) -> Optional["ast.MatchAs"]:
        # as_pattern: or_pattern 'as' pattern_capture_target | invalid_as_pattern
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (pattern := self.or_pattern())
            and
            (self.expect('as'))
            and
            (target := self.pattern_capture_target())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchAs ( pattern = pattern , name = target , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_as_pattern())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def or_pattern(self) -> Optional["ast.MatchOr"]:
        # or_pattern: '|'.closed_pattern+
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (patterns := self._gather_99())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchOr ( patterns = patterns , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if len ( patterns ) > 1 else patterns [0];
        self._reset(mark)
        return None;

    @memoize
    def closed_pattern(self) -> Optional[Any]:
        # closed_pattern: literal_pattern | capture_pattern | wildcard_pattern | value_pattern | group_pattern | sequence_pattern | mapping_pattern | class_pattern
        mark = self._mark()
        if (
            (literal_pattern := self.literal_pattern())
        ):
            return literal_pattern;
        self._reset(mark)
        if (
            (capture_pattern := self.capture_pattern())
        ):
            return capture_pattern;
        self._reset(mark)
        if (
            (wildcard_pattern := self.wildcard_pattern())
        ):
            return wildcard_pattern;
        self._reset(mark)
        if (
            (value_pattern := self.value_pattern())
        ):
            return value_pattern;
        self._reset(mark)
        if (
            (group_pattern := self.group_pattern())
        ):
            return group_pattern;
        self._reset(mark)
        if (
            (sequence_pattern := self.sequence_pattern())
        ):
            return sequence_pattern;
        self._reset(mark)
        if (
            (mapping_pattern := self.mapping_pattern())
        ):
            return mapping_pattern;
        self._reset(mark)
        if (
            (class_pattern := self.class_pattern())
        ):
            return class_pattern;
        self._reset(mark)
        return None;

    @memoize
    def literal_pattern(self) -> Optional[Any]:
        # literal_pattern: signed_number !('+' | '-') | complex_number | strings | 'None' | 'True' | 'False'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (value := self.signed_number())
            and
            (self.negative_lookahead(self._tmp_101, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchValue ( value = value , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (value := self.complex_number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchValue ( value = value , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (value := self.strings())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchValue ( value = value , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('None'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSingleton ( value = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('True'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSingleton ( value = True , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('False'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSingleton ( value = False , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def literal_expr(self) -> Optional[Any]:
        # literal_expr: signed_number !('+' | '-') | complex_number | strings | 'None' | 'True' | 'False'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (signed_number := self.signed_number())
            and
            (self.negative_lookahead(self._tmp_102, ))
        ):
            return signed_number;
        self._reset(mark)
        if (
            (complex_number := self.complex_number())
        ):
            return complex_number;
        self._reset(mark)
        if (
            (strings := self.strings())
        ):
            return strings;
        self._reset(mark)
        if (
            (self.expect('None'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('True'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = True , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('False'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = False , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def complex_number(self) -> Optional[Any]:
        # complex_number: signed_real_number '+' imaginary_number | signed_real_number '-' imaginary_number
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (real := self.signed_real_number())
            and
            (self.expect('+'))
            and
            (imag := self.imaginary_number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = real , op = ast . Add ( ) , right = imag , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (real := self.signed_real_number())
            and
            (self.expect('-'))
            and
            (imag := self.imaginary_number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = real , op = ast . Sub ( ) , right = imag , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def signed_number(self) -> Optional[Any]:
        # signed_number: NUMBER | '-' NUMBER
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = ast . literal_eval ( a . string ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('-'))
            and
            (a := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . USub ( ) , operand = ast . Constant ( value = ast . literal_eval ( a . string ) , lineno = a . start [0] , col_offset = a . start [1] , end_lineno = a . end [0] , end_col_offset = a . end [1] ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        return None;

    @memoize
    def signed_real_number(self) -> Optional[Any]:
        # signed_real_number: real_number | '-' real_number
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (real_number := self.real_number())
        ):
            return real_number;
        self._reset(mark)
        if (
            (self.expect('-'))
            and
            (real := self.real_number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . USub ( ) , operand = real , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def real_number(self) -> Optional[ast . Constant]:
        # real_number: NUMBER
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (real := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = self . ensure_real ( real ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def imaginary_number(self) -> Optional[ast . Constant]:
        # imaginary_number: NUMBER
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (imag := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = self . ensure_imaginary ( imag ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def capture_pattern(self) -> Optional[Any]:
        # capture_pattern: pattern_capture_target
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (target := self.pattern_capture_target())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchAs ( pattern = None , name = target , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def pattern_capture_target(self) -> Optional[str]:
        # pattern_capture_target: !"_" NAME !('.' | '(' | '=')
        mark = self._mark()
        if (
            (self.negative_lookahead(self.expect, "_"))
            and
            (name := self.name())
            and
            (self.negative_lookahead(self._tmp_103, ))
        ):
            return name . string;
        self._reset(mark)
        return None;

    @memoize
    def wildcard_pattern(self) -> Optional["ast.MatchAs"]:
        # wildcard_pattern: "_"
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect("_"))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchAs ( pattern = None , target = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def value_pattern(self) -> Optional["ast.MatchValue"]:
        # value_pattern: attr !('.' | '(' | '=')
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (attr := self.attr())
            and
            (self.negative_lookahead(self._tmp_104, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchValue ( value = attr , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize_left_rec
    def attr(self) -> Optional[ast . Attribute]:
        # attr: name_or_attr '.' NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (value := self.name_or_attr())
            and
            (self.expect('.'))
            and
            (attr := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = value , attr = attr . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @logger
    def name_or_attr(self) -> Optional[Any]:
        # name_or_attr: attr | NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (attr := self.attr())
        ):
            return attr;
        self._reset(mark)
        if (
            (name := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = name . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def group_pattern(self) -> Optional[Any]:
        # group_pattern: '(' pattern ')'
        mark = self._mark()
        if (
            (self.expect('('))
            and
            (pattern := self.pattern())
            and
            (self.expect(')'))
        ):
            return pattern;
        self._reset(mark)
        return None;

    @memoize
    def sequence_pattern(self) -> Optional["ast.MatchSequence"]:
        # sequence_pattern: '[' maybe_sequence_pattern? ']' | '(' open_sequence_pattern? ')'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('['))
            and
            (patterns := self.maybe_sequence_pattern(),)
            and
            (self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSequence ( patterns = patterns or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('('))
            and
            (patterns := self.open_sequence_pattern(),)
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSequence ( patterns = patterns or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def open_sequence_pattern(self) -> Optional[Any]:
        # open_sequence_pattern: maybe_star_pattern ',' maybe_sequence_pattern?
        mark = self._mark()
        if (
            (pattern := self.maybe_star_pattern())
            and
            (self.expect(','))
            and
            (patterns := self.maybe_sequence_pattern(),)
        ):
            return [pattern] + ( patterns or [] );
        self._reset(mark)
        return None;

    @memoize
    def maybe_sequence_pattern(self) -> Optional[Any]:
        # maybe_sequence_pattern: ','.maybe_star_pattern+ ','?
        mark = self._mark()
        if (
            (patterns := self._gather_105())
            and
            (self.expect(','),)
        ):
            return patterns;
        self._reset(mark)
        return None;

    @memoize
    def maybe_star_pattern(self) -> Optional[Any]:
        # maybe_star_pattern: star_pattern | pattern
        mark = self._mark()
        if (
            (star_pattern := self.star_pattern())
        ):
            return star_pattern;
        self._reset(mark)
        if (
            (pattern := self.pattern())
        ):
            return pattern;
        self._reset(mark)
        return None;

    @memoize
    def star_pattern(self) -> Optional[Any]:
        # star_pattern: '*' pattern_capture_target | '*' wildcard_pattern
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('*'))
            and
            (target := self.pattern_capture_target())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchStar ( name = target , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (self.wildcard_pattern())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchStar ( target = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def mapping_pattern(self) -> Optional[Any]:
        # mapping_pattern: '{' '}' | '{' double_star_pattern ','? '}' | '{' items_pattern ',' double_star_pattern ','? '}' | '{' items_pattern ','? '}'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('{'))
            and
            (self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchMapping ( keys = [] , patterns = [] , rest = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (rest := self.double_star_pattern())
            and
            (self.expect(','),)
            and
            (self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchMapping ( keys = [] , patterns = [] , rest = rest , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (items := self.items_pattern())
            and
            (self.expect(','))
            and
            (rest := self.double_star_pattern())
            and
            (self.expect(','),)
            and
            (self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchMapping ( keys = [k for k , _ in items] , patterns = [p for _ , p in items] , rest = rest , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (items := self.items_pattern())
            and
            (self.expect(','),)
            and
            (self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchMapping ( keys = [k for k , _ in items] , patterns = [p for _ , p in items] , rest = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        return None;

    @memoize
    def items_pattern(self) -> Optional[Any]:
        # items_pattern: ','.key_value_pattern+
        mark = self._mark()
        if (
            (_gather_107 := self._gather_107())
        ):
            return _gather_107;
        self._reset(mark)
        return None;

    @memoize
    def key_value_pattern(self) -> Optional[Any]:
        # key_value_pattern: (literal_expr | attr) ':' pattern
        mark = self._mark()
        if (
            (key := self._tmp_109())
            and
            (self.expect(':'))
            and
            (pattern := self.pattern())
        ):
            return ( key , pattern );
        self._reset(mark)
        return None;

    @memoize
    def double_star_pattern(self) -> Optional[Any]:
        # double_star_pattern: '**' pattern_capture_target
        mark = self._mark()
        if (
            (self.expect('**'))
            and
            (target := self.pattern_capture_target())
        ):
            return target;
        self._reset(mark)
        return None;

    @memoize
    def class_pattern(self) -> Optional["ast.MatchClass"]:
        # class_pattern: name_or_attr '(' ')' | name_or_attr '(' positional_patterns ','? ')' | name_or_attr '(' keyword_patterns ','? ')' | name_or_attr '(' positional_patterns ',' keyword_patterns ','? ')' | invalid_class_pattern
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (cls := self.name_or_attr())
            and
            (self.expect('('))
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchClass ( cls = cls , patterns = [] , kwd_attrs = [] , kwd_patterns = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (cls := self.name_or_attr())
            and
            (self.expect('('))
            and
            (patterns := self.positional_patterns())
            and
            (self.expect(','),)
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchClass ( cls = cls , patterns = patterns , kwd_attrs = [] , kwd_patterns = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (cls := self.name_or_attr())
            and
            (self.expect('('))
            and
            (keywords := self.keyword_patterns())
            and
            (self.expect(','),)
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchClass ( cls = cls , patterns = [] , kwd_attrs = [k for k , _ in keywords] , kwd_patterns = [p for _ , p in keywords] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        if (
            (cls := self.name_or_attr())
            and
            (self.expect('('))
            and
            (patterns := self.positional_patterns())
            and
            (self.expect(','))
            and
            (keywords := self.keyword_patterns())
            and
            (self.expect(','),)
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchClass ( cls = cls , patterns = patterns , kwd_attrs = [k for k , _ in keywords] , kwd_patterns = [p for _ , p in keywords] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_class_pattern())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def positional_patterns(self) -> Optional[Any]:
        # positional_patterns: ','.pattern+
        mark = self._mark()
        if (
            (args := self._gather_110())
        ):
            return args;
        self._reset(mark)
        return None;

    @memoize
    def keyword_patterns(self) -> Optional[Any]:
        # keyword_patterns: ','.keyword_pattern+
        mark = self._mark()
        if (
            (_gather_112 := self._gather_112())
        ):
            return _gather_112;
        self._reset(mark)
        return None;

    @memoize
    def keyword_pattern(self) -> Optional[Any]:
        # keyword_pattern: NAME '=' pattern
        mark = self._mark()
        if (
            (arg := self.name())
            and
            (self.expect('='))
            and
            (value := self.pattern())
        ):
            return ( arg . string , value );
        self._reset(mark)
        return None;

    @memoize
    def type_alias(self) -> Optional["ast.TypeAlias"]:
        # type_alias: "type" NAME type_params? '=' expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect("type"))
            and
            (n := self.name())
            and
            (t := self.type_params(),)
            and
            (self.expect('='))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 12 ) , "Type statement is" , ( ast . TypeAlias ( name = ast . Name ( id = n . string , ctx = Store , lineno = n . start [0] , col_offset = n . start [1] , end_lineno = n . end [0] , end_col_offset = n . end [1] , ) , type_params = t or [] , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 12 ) else None ) );
        self._reset(mark)
        return None;

    @memoize
    def type_params(self) -> Optional[list]:
        # type_params: '[' type_param_seq ']'
        mark = self._mark()
        if (
            (self.expect('['))
            and
            (t := self.type_param_seq())
            and
            (self.expect(']'))
        ):
            return self . check_version ( ( 3 , 12 ) , "Type parameter lists are" , t );
        self._reset(mark)
        return None;

    @memoize
    def type_param_seq(self) -> Optional[Any]:
        # type_param_seq: ','.type_param+ ','?
        mark = self._mark()
        if (
            (a := self._gather_114())
            and
            (self.expect(','),)
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def type_param(self) -> Optional[Any]:
        # type_param: NAME type_param_bound? | '*' NAME ":" expression | '*' NAME | '**' NAME ":" expression | '**' NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (b := self.type_param_bound(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . TypeVar ( name = a . string , bound = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 12 ) else object ( );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (self.name())
            and
            (colon := self.expect(":"))
            and
            (e := self.expression())
        ):
            return self . raise_syntax_error_starting_from ( "cannot use constraints with TypeVarTuple" if isinstance ( e , ast . Tuple ) else "cannot use bound with TypeVarTuple" , colon );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . TypeVarTuple ( name = a . string , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 12 ) else object ( );
        self._reset(mark)
        if (
            (self.expect('**'))
            and
            (self.name())
            and
            (colon := self.expect(":"))
            and
            (e := self.expression())
        ):
            return self . raise_syntax_error_starting_from ( "cannot use constraints with ParamSpec" if isinstance ( e , ast . Tuple ) else "cannot use bound with ParamSpec" , colon );
        self._reset(mark)
        if (
            (self.expect('**'))
            and
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ParamSpec ( name = a . string , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 12 ) else object ( );
        self._reset(mark)
        return None;

    @memoize
    def type_param_bound(self) -> Optional[Any]:
        # type_param_bound: ":" expression
        mark = self._mark()
        if (
            (self.expect(":"))
            and
            (e := self.expression())
        ):
            return e;
        self._reset(mark)
        return None;

    @memoize
    def expressions(self) -> Optional[Any]:
        # expressions: expression ((',' expression))+ ','? | expression ',' | expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.expression())
            and
            (b := self._loop1_116())
            and
            (self.expect(','),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = [a] + b , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.expression())
            and
            (self.expect(','))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = [a] , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (expression := self.expression())
        ):
            return expression;
        self._reset(mark)
        return None;

    @memoize
    def expression(self) -> Optional[Any]:
        # expression: invalid_expression | invalid_legacy_expression | disjunction 'if' disjunction 'else' expression | disjunction | lambdef
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_expression())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_legacy_expression())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (a := self.disjunction())
            and
            (self.expect('if'))
            and
            (b := self.disjunction())
            and
            (self.expect('else'))
            and
            (c := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . IfExp ( body = a , test = b , orelse = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (disjunction := self.disjunction())
        ):
            return disjunction;
        self._reset(mark)
        if (
            (lambdef := self.lambdef())
        ):
            return lambdef;
        self._reset(mark)
        return None;

    @memoize
    def yield_expr(self) -> Optional[Any]:
        # yield_expr: 'yield' 'from' expression | 'yield' star_expressions?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('yield'))
            and
            (self.expect('from'))
            and
            (a := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . YieldFrom ( value = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('yield'))
            and
            (a := self.star_expressions(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Yield ( value = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def star_expressions(self) -> Optional[Any]:
        # star_expressions: star_expression ((',' star_expression))+ ','? | star_expression ',' | star_expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.star_expression())
            and
            (b := self._loop1_117())
            and
            (self.expect(','),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = [a] + b , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.star_expression())
            and
            (self.expect(','))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = [a] , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (star_expression := self.star_expression())
        ):
            return star_expression;
        self._reset(mark)
        return None;

    @memoize
    def star_expression(self) -> Optional[Any]:
        # star_expression: '*' bitwise_or | expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('*'))
            and
            (a := self.bitwise_or())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Starred ( value = a , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (expression := self.expression())
        ):
            return expression;
        self._reset(mark)
        return None;

    @memoize
    def star_named_expressions(self) -> Optional[Any]:
        # star_named_expressions: ','.star_named_expression+ ','?
        mark = self._mark()
        if (
            (a := self._gather_118())
            and
            (self.expect(','),)
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def star_named_expression(self) -> Optional[Any]:
        # star_named_expression: '*' bitwise_or | named_expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('*'))
            and
            (a := self.bitwise_or())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Starred ( value = a , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (named_expression := self.named_expression())
        ):
            return named_expression;
        self._reset(mark)
        return None;

    @memoize
    def assignment_expression(self) -> Optional[Any]:
        # assignment_expression: NAME ':=' ~ expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        cut = False
        if (
            (a := self.name())
            and
            (self.expect(':='))
            and
            (cut := True)
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 8 ) , "The ':=' operator is" , ast . NamedExpr ( target = ast . Name ( id = a . string , ctx = Store , lineno = a . start [0] , col_offset = a . start [1] , end_lineno = a . end [0] , end_col_offset = a . end [1] ) , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) );
        self._reset(mark)
        if cut:
            return None;
        return None;

    @memoize
    def named_expression(self) -> Optional[Any]:
        # named_expression: assignment_expression | invalid_named_expression | expression !':='
        mark = self._mark()
        if (
            (assignment_expression := self.assignment_expression())
        ):
            return assignment_expression;
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_named_expression())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (a := self.expression())
            and
            (self.negative_lookahead(self.expect, ':='))
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def disjunction(self) -> Optional[Any]:
        # disjunction: conjunction (('or' conjunction))+ | conjunction
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.conjunction())
            and
            (b := self._loop1_120())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BoolOp ( op = ast . Or ( ) , values = [a] + b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (conjunction := self.conjunction())
        ):
            return conjunction;
        self._reset(mark)
        return None;

    @memoize
    def conjunction(self) -> Optional[Any]:
        # conjunction: inversion (('and' inversion))+ | inversion
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.inversion())
            and
            (b := self._loop1_121())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BoolOp ( op = ast . And ( ) , values = [a] + b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (inversion := self.inversion())
        ):
            return inversion;
        self._reset(mark)
        return None;

    @memoize
    def inversion(self) -> Optional[Any]:
        # inversion: 'not' inversion | comparison
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('not'))
            and
            (a := self.inversion())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . Not ( ) , operand = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (comparison := self.comparison())
        ):
            return comparison;
        self._reset(mark)
        return None;

    @memoize
    def comparison(self) -> Optional[Any]:
        # comparison: bitwise_or compare_op_bitwise_or_pair+ | bitwise_or
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.bitwise_or())
            and
            (b := self._loop1_122())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Compare ( left = a , ops = self . get_comparison_ops ( b ) , comparators = self . get_comparators ( b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (bitwise_or := self.bitwise_or())
        ):
            return bitwise_or;
        self._reset(mark)
        return None;

    @memoize
    def compare_op_bitwise_or_pair(self) -> Optional[Any]:
        # compare_op_bitwise_or_pair: eq_bitwise_or | noteq_bitwise_or | lte_bitwise_or | lt_bitwise_or | gte_bitwise_or | gt_bitwise_or | notin_bitwise_or | in_bitwise_or | isnot_bitwise_or | is_bitwise_or
        mark = self._mark()
        if (
            (eq_bitwise_or := self.eq_bitwise_or())
        ):
            return eq_bitwise_or;
        self._reset(mark)
        if (
            (noteq_bitwise_or := self.noteq_bitwise_or())
        ):
            return noteq_bitwise_or;
        self._reset(mark)
        if (
            (lte_bitwise_or := self.lte_bitwise_or())
        ):
            return lte_bitwise_or;
        self._reset(mark)
        if (
            (lt_bitwise_or := self.lt_bitwise_or())
        ):
            return lt_bitwise_or;
        self._reset(mark)
        if (
            (gte_bitwise_or := self.gte_bitwise_or())
        ):
            return gte_bitwise_or;
        self._reset(mark)
        if (
            (gt_bitwise_or := self.gt_bitwise_or())
        ):
            return gt_bitwise_or;
        self._reset(mark)
        if (
            (notin_bitwise_or := self.notin_bitwise_or())
        ):
            return notin_bitwise_or;
        self._reset(mark)
        if (
            (in_bitwise_or := self.in_bitwise_or())
        ):
            return in_bitwise_or;
        self._reset(mark)
        if (
            (isnot_bitwise_or := self.isnot_bitwise_or())
        ):
            return isnot_bitwise_or;
        self._reset(mark)
        if (
            (is_bitwise_or := self.is_bitwise_or())
        ):
            return is_bitwise_or;
        self._reset(mark)
        return None;

    @memoize
    def eq_bitwise_or(self) -> Optional[Any]:
        # eq_bitwise_or: '==' bitwise_or
        mark = self._mark()
        if (
            (self.expect('=='))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . Eq ( ) , a );
        self._reset(mark)
        return None;

    @memoize
    def noteq_bitwise_or(self) -> Optional[tuple]:
        # noteq_bitwise_or: '!=' bitwise_or
        mark = self._mark()
        if (
            (self.expect('!='))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . NotEq ( ) , a );
        self._reset(mark)
        return None;

    @memoize
    def lte_bitwise_or(self) -> Optional[Any]:
        # lte_bitwise_or: '<=' bitwise_or
        mark = self._mark()
        if (
            (self.expect('<='))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . LtE ( ) , a );
        self._reset(mark)
        return None;

    @memoize
    def lt_bitwise_or(self) -> Optional[Any]:
        # lt_bitwise_or: '<' bitwise_or
        mark = self._mark()
        if (
            (self.expect('<'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . Lt ( ) , a );
        self._reset(mark)
        return None;

    @memoize
    def gte_bitwise_or(self) -> Optional[Any]:
        # gte_bitwise_or: '>=' bitwise_or
        mark = self._mark()
        if (
            (self.expect('>='))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . GtE ( ) , a );
        self._reset(mark)
        return None;

    @memoize
    def gt_bitwise_or(self) -> Optional[Any]:
        # gt_bitwise_or: '>' bitwise_or
        mark = self._mark()
        if (
            (self.expect('>'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . Gt ( ) , a );
        self._reset(mark)
        return None;

    @memoize
    def notin_bitwise_or(self) -> Optional[Any]:
        # notin_bitwise_or: 'not' 'in' bitwise_or
        mark = self._mark()
        if (
            (self.expect('not'))
            and
            (self.expect('in'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . NotIn ( ) , a );
        self._reset(mark)
        return None;

    @memoize
    def in_bitwise_or(self) -> Optional[Any]:
        # in_bitwise_or: 'in' bitwise_or
        mark = self._mark()
        if (
            (self.expect('in'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . In ( ) , a );
        self._reset(mark)
        return None;

    @memoize
    def isnot_bitwise_or(self) -> Optional[Any]:
        # isnot_bitwise_or: 'is' 'not' bitwise_or
        mark = self._mark()
        if (
            (self.expect('is'))
            and
            (self.expect('not'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . IsNot ( ) , a );
        self._reset(mark)
        return None;

    @memoize
    def is_bitwise_or(self) -> Optional[Any]:
        # is_bitwise_or: 'is' bitwise_or
        mark = self._mark()
        if (
            (self.expect('is'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . Is ( ) , a );
        self._reset(mark)
        return None;

    @memoize_left_rec
    def bitwise_or(self) -> Optional[Any]:
        # bitwise_or: bitwise_or '|' bitwise_xor | bitwise_xor
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.bitwise_or())
            and
            (self.expect('|'))
            and
            (b := self.bitwise_xor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . BitOr ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (bitwise_xor := self.bitwise_xor())
        ):
            return bitwise_xor;
        self._reset(mark)
        return None;

    @memoize_left_rec
    def bitwise_xor(self) -> Optional[Any]:
        # bitwise_xor: bitwise_xor '^' bitwise_and | bitwise_and
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.bitwise_xor())
            and
            (self.expect('^'))
            and
            (b := self.bitwise_and())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . BitXor ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (bitwise_and := self.bitwise_and())
        ):
            return bitwise_and;
        self._reset(mark)
        return None;

    @memoize_left_rec
    def bitwise_and(self) -> Optional[Any]:
        # bitwise_and: bitwise_and '&' shift_expr | shift_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.bitwise_and())
            and
            (self.expect('&'))
            and
            (b := self.shift_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . BitAnd ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (shift_expr := self.shift_expr())
        ):
            return shift_expr;
        self._reset(mark)
        return None;

    @memoize_left_rec
    def shift_expr(self) -> Optional[Any]:
        # shift_expr: shift_expr '<<' sum | shift_expr '>>' sum | sum
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.shift_expr())
            and
            (self.expect('<<'))
            and
            (b := self.sum())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . LShift ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.shift_expr())
            and
            (self.expect('>>'))
            and
            (b := self.sum())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . RShift ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (sum := self.sum())
        ):
            return sum;
        self._reset(mark)
        return None;

    @memoize_left_rec
    def sum(self) -> Optional[Any]:
        # sum: sum '+' term | sum '-' term | term
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.sum())
            and
            (self.expect('+'))
            and
            (b := self.term())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Add ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.sum())
            and
            (self.expect('-'))
            and
            (b := self.term())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Sub ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (term := self.term())
        ):
            return term;
        self._reset(mark)
        return None;

    @memoize_left_rec
    def term(self) -> Optional[Any]:
        # term: term '*' factor | term '/' factor | term '//' factor | term '%' factor | term '@' factor | factor
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.term())
            and
            (self.expect('*'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Mult ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.term())
            and
            (self.expect('/'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Div ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.term())
            and
            (self.expect('//'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . FloorDiv ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.term())
            and
            (self.expect('%'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Mod ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.term())
            and
            (self.expect('@'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 5 ) , "The '@' operator is" , ast . BinOp ( left = a , op = ast . MatMult ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) );
        self._reset(mark)
        if (
            (factor := self.factor())
        ):
            return factor;
        self._reset(mark)
        return None;

    @memoize
    def factor(self) -> Optional[Any]:
        # factor: '+' factor | '-' factor | '~' factor | power
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('+'))
            and
            (a := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . UAdd ( ) , operand = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('-'))
            and
            (a := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . USub ( ) , operand = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('~'))
            and
            (a := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . Invert ( ) , operand = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (power := self.power())
        ):
            return power;
        self._reset(mark)
        return None;

    @memoize
    def power(self) -> Optional[Any]:
        # power: await_primary '**' factor | await_primary
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.await_primary())
            and
            (self.expect('**'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Pow ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (await_primary := self.await_primary())
        ):
            return await_primary;
        self._reset(mark)
        return None;

    @memoize
    def await_primary(self) -> Optional[Any]:
        # await_primary: 'await' primary | primary
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('await'))
            and
            (a := self.primary())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 5 ) , "Await expressions are" , ast . Await ( a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) );
        self._reset(mark)
        if (
            (primary := self.primary())
        ):
            return primary;
        self._reset(mark)
        return None;

    @memoize_left_rec
    def primary(self) -> Optional[Any]:
        # primary: primary '.' NAME | primary genexp | primary '(' arguments? ')' | primary '[' slices ']' | atom
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.primary())
            and
            (self.expect('.'))
            and
            (b := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.primary())
            and
            (b := self.genexp())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Call ( func = a , args = [b] , keywords = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.primary())
            and
            (self.expect('('))
            and
            (b := self.arguments(),)
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Call ( func = a , args = b [0] if b else [] , keywords = b [1] if b else [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        if (
            (a := self.primary())
            and
            (self.expect('['))
            and
            (b := self.slices())
            and
            (self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Subscript ( value = a , slice = b , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (atom := self.atom())
        ):
            return atom;
        self._reset(mark)
        return None;

    @memoize
    def slices(self) -> Optional[Any]:
        # slices: slice !',' | ','.(slice | starred_expression)+ ','?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.slice())
            and
            (self.negative_lookahead(self.expect, ','))
        ):
            return a;
        self._reset(mark)
        if (
            (a := self._gather_123())
            and
            (self.expect(','),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = a , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 9 ) else ( ast . ExtSlice ( dims = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if any ( isinstance ( e , ast . Slice ) for e in a ) else ast . Index ( value = ast . Tuple ( elts = [e . value for e in a] , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) );
        self._reset(mark)
        return None;

    @memoize
    def slice(self) -> Optional[Any]:
        # slice: expression? ':' expression? [':' expression?] | named_expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.expression(),)
            and
            (self.expect(':'))
            and
            (b := self.expression(),)
            and
            (c := self._tmp_125(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Slice ( lower = a , upper = b , step = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.named_expression())
        ):
            return a if sys . version_info >= ( 3 , 9 ) or isinstance ( a , ast . Slice ) else ast . Index ( value = a , lineno = a . lineno , col_offset = a . col_offset , end_lineno = a . end_lineno , end_col_offset = a . end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def atom(self) -> Optional[Any]:
        # atom: NAME | 'True' | 'False' | 'None' | &(STRING | FSTRING_START) strings | NUMBER | &'(' (tuple | group | genexp) | &'[' (list | listcomp) | &'{' (dict | set | dictcomp | setcomp) | '...'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = a . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('True'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = True , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 9 ) else ast . Constant ( value = True , kind = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('False'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = False , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 9 ) else ast . Constant ( value = False , kind = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('None'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 9 ) else ast . Constant ( value = None , kind = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.positive_lookahead(self._tmp_126, ))
            and
            (strings := self.strings())
        ):
            return strings;
        self._reset(mark)
        if (
            (a := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = ast . literal_eval ( a . string ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 9 ) else ast . Constant ( value = ast . literal_eval ( a . string ) , kind = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, '('))
            and
            (_tmp_127 := self._tmp_127())
        ):
            return _tmp_127;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, '['))
            and
            (_tmp_128 := self._tmp_128())
        ):
            return _tmp_128;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, '{'))
            and
            (_tmp_129 := self._tmp_129())
        ):
            return _tmp_129;
        self._reset(mark)
        if (
            (self.expect('...'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = Ellipsis , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 9 ) else ast . Constant ( value = Ellipsis , kind = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def group(self) -> Optional[Any]:
        # group: '(' (yield_expr | named_expression) ')' | invalid_group
        mark = self._mark()
        if (
            (self.expect('('))
            and
            (a := self._tmp_130())
            and
            (self.expect(')'))
        ):
            return a;
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_group())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def lambdef(self) -> Optional[Any]:
        # lambdef: 'lambda' lambda_params? ':' expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('lambda'))
            and
            (a := self.lambda_params(),)
            and
            (self.expect(':'))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Lambda ( args = a or self . make_arguments ( None , [] , None , [] , ( None , [] , None ) ) , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def lambda_params(self) -> Optional[Any]:
        # lambda_params: invalid_lambda_parameters | lambda_parameters
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.invalid_lambda_parameters())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (lambda_parameters := self.lambda_parameters())
        ):
            return lambda_parameters;
        self._reset(mark)
        return None;

    @memoize
    def lambda_parameters(self) -> Optional[ast . arguments]:
        # lambda_parameters: lambda_slash_no_default lambda_param_no_default* lambda_param_with_default* lambda_star_etc? | lambda_slash_with_default lambda_param_with_default* lambda_star_etc? | lambda_param_no_default+ lambda_param_with_default* lambda_star_etc? | lambda_param_with_default+ lambda_star_etc? | lambda_star_etc
        mark = self._mark()
        if (
            (a := self.lambda_slash_no_default())
            and
            (b := self._loop0_131(),)
            and
            (c := self._loop0_132(),)
            and
            (d := self.lambda_star_etc(),)
        ):
            return self . make_arguments ( a , [] , b , c , d );
        self._reset(mark)
        if (
            (a := self.lambda_slash_with_default())
            and
            (b := self._loop0_133(),)
            and
            (c := self.lambda_star_etc(),)
        ):
            return self . make_arguments ( None , a , None , b , c );
        self._reset(mark)
        if (
            (a := self._loop1_134())
            and
            (b := self._loop0_135(),)
            and
            (c := self.lambda_star_etc(),)
        ):
            return self . make_arguments ( None , [] , a , b , c );
        self._reset(mark)
        if (
            (a := self._loop1_136())
            and
            (b := self.lambda_star_etc(),)
        ):
            return self . make_arguments ( None , [] , None , a , b );
        self._reset(mark)
        if (
            (a := self.lambda_star_etc())
        ):
            return self . make_arguments ( None , [] , None , [] , a );
        self._reset(mark)
        return None;

    @memoize
    def lambda_slash_no_default(self) -> Optional[List [Tuple [ast . arg , None]]]:
        # lambda_slash_no_default: lambda_param_no_default+ '/' ',' | lambda_param_no_default+ '/' &':'
        mark = self._mark()
        if (
            (a := self._loop1_137())
            and
            (self.expect('/'))
            and
            (self.expect(','))
        ):
            return [( p , None ) for p in a];
        self._reset(mark)
        if (
            (a := self._loop1_138())
            and
            (self.expect('/'))
            and
            (self.positive_lookahead(self.expect, ':'))
        ):
            return [( p , None ) for p in a];
        self._reset(mark)
        return None;

    @memoize
    def lambda_slash_with_default(self) -> Optional[List [Tuple [ast . arg , Any]]]:
        # lambda_slash_with_default: lambda_param_no_default* lambda_param_with_default+ '/' ',' | lambda_param_no_default* lambda_param_with_default+ '/' &':'
        mark = self._mark()
        if (
            (a := self._loop0_139(),)
            and
            (b := self._loop1_140())
            and
            (self.expect('/'))
            and
            (self.expect(','))
        ):
            return ( [( p , None ) for p in a] if a else [] ) + b;
        self._reset(mark)
        if (
            (a := self._loop0_141(),)
            and
            (b := self._loop1_142())
            and
            (self.expect('/'))
            and
            (self.positive_lookahead(self.expect, ':'))
        ):
            return ( [( p , None ) for p in a] if a else [] ) + b;
        self._reset(mark)
        return None;

    @memoize
    def lambda_star_etc(self) -> Optional[Tuple [Optional [ast . arg] , List [Tuple [ast . arg , Any]] , Optional [ast . arg]]]:
        # lambda_star_etc: invalid_lambda_star_etc | '*' lambda_param_no_default lambda_param_maybe_default* lambda_kwds? | '*' ',' lambda_param_maybe_default+ lambda_kwds? | lambda_kwds
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.invalid_lambda_star_etc())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (a := self.lambda_param_no_default())
            and
            (b := self._loop0_143(),)
            and
            (c := self.lambda_kwds(),)
        ):
            return ( a , b , c );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (self.expect(','))
            and
            (b := self._loop1_144())
            and
            (c := self.lambda_kwds(),)
        ):
            return ( None , b , c );
        self._reset(mark)
        if (
            (a := self.lambda_kwds())
        ):
            return ( None , [] , a );
        self._reset(mark)
        return None;

    @memoize
    def lambda_kwds(self) -> Optional[ast . arg]:
        # lambda_kwds: invalid_lambda_kwds | '**' lambda_param_no_default
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.invalid_lambda_kwds())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('**'))
            and
            (a := self.lambda_param_no_default())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def lambda_param_no_default(self) -> Optional[ast . arg]:
        # lambda_param_no_default: lambda_param ',' | lambda_param &':'
        mark = self._mark()
        if (
            (a := self.lambda_param())
            and
            (self.expect(','))
        ):
            return a;
        self._reset(mark)
        if (
            (a := self.lambda_param())
            and
            (self.positive_lookahead(self.expect, ':'))
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def lambda_param_with_default(self) -> Optional[Tuple [ast . arg , Any]]:
        # lambda_param_with_default: lambda_param default ',' | lambda_param default &':'
        mark = self._mark()
        if (
            (a := self.lambda_param())
            and
            (c := self.default())
            and
            (self.expect(','))
        ):
            return ( a , c );
        self._reset(mark)
        if (
            (a := self.lambda_param())
            and
            (c := self.default())
            and
            (self.positive_lookahead(self.expect, ':'))
        ):
            return ( a , c );
        self._reset(mark)
        return None;

    @memoize
    def lambda_param_maybe_default(self) -> Optional[Tuple [ast . arg , Any]]:
        # lambda_param_maybe_default: lambda_param default? ',' | lambda_param default? &':'
        mark = self._mark()
        if (
            (a := self.lambda_param())
            and
            (c := self.default(),)
            and
            (self.expect(','))
        ):
            return ( a , c );
        self._reset(mark)
        if (
            (a := self.lambda_param())
            and
            (c := self.default(),)
            and
            (self.positive_lookahead(self.expect, ':'))
        ):
            return ( a , c );
        self._reset(mark)
        return None;

    @memoize
    def lambda_param(self) -> Optional[ast . arg]:
        # lambda_param: NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . arg ( arg = a . string , annotation = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if sys . version_info >= ( 3 , 9 ) else ast . arg ( arg = a . string , annotation = None , type_comment = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def fstring_mid(self) -> Optional[Any]:
        # fstring_mid: fstring_replacement_field | FSTRING_MIDDLE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (fstring_replacement_field := self.fstring_replacement_field())
        ):
            return fstring_replacement_field;
        self._reset(mark)
        if (
            (t := self.fstring_middle())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = t . string , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def fstring_replacement_field(self) -> Optional[Any]:
        # fstring_replacement_field: '{' (yield_expr | star_expressions) "="? fstring_conversion? fstring_full_format_spec? '}' | invalid_replacement_field
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('{'))
            and
            (a := self._tmp_145())
            and
            (debug_expr := self.expect("="),)
            and
            (conversion := self.fstring_conversion(),)
            and
            (format := self.fstring_full_format_spec(),)
            and
            (self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . FormattedValue ( value = a , conversion = ( conversion . decode ( ) [0] if conversion else ( b'r' [0] if debug_expr else - 1 ) ) , format_spec = format , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_replacement_field())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def fstring_conversion(self) -> Optional[int]:
        # fstring_conversion: "!" NAME
        mark = self._mark()
        if (
            (conv_token := self.expect("!"))
            and
            (conv := self.name())
        ):
            return self . check_fstring_conversion ( conv_token , conv );
        self._reset(mark)
        return None;

    @memoize
    def fstring_full_format_spec(self) -> Optional[Any]:
        # fstring_full_format_spec: ':' fstring_format_spec*
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect(':'))
            and
            (spec := self._loop0_146(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . JoinedStr ( values = spec if spec and ( len ( spec ) > 1 or spec [0] . value ) else [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        return None;

    @memoize
    def fstring_format_spec(self) -> Optional[Any]:
        # fstring_format_spec: FSTRING_MIDDLE | fstring_replacement_field
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (t := self.fstring_middle())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = t . string , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (fstring_replacement_field := self.fstring_replacement_field())
        ):
            return fstring_replacement_field;
        self._reset(mark)
        return None;

    @memoize
    def fstring(self) -> Optional[Any]:
        # fstring: FSTRING_START fstring_mid* FSTRING_END
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.fstring_start())
            and
            (b := self._loop0_147(),)
            and
            (self.fstring_end())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . JoinedStr ( values = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def strings(self) -> Optional[Any]:
        # strings: ((fstring | STRING))+
        mark = self._mark()
        if (
            (a := self._loop1_148())
        ):
            return self . concatenate_strings ( a ) if sys . version_info >= ( 3 , 12 ) else self . generate_ast_for_string ( a );
        self._reset(mark)
        return None;

    @memoize
    def list(self) -> Optional[ast . List]:
        # list: '[' star_named_expressions? ']'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('['))
            and
            (a := self.star_named_expressions(),)
            and
            (self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . List ( elts = a or [] , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def tuple(self) -> Optional[ast . Tuple]:
        # tuple: '(' [star_named_expression ',' star_named_expressions?] ')'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('('))
            and
            (a := self._tmp_149(),)
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = a or [] , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def set(self) -> Optional[ast . Set]:
        # set: '{' star_named_expressions '}'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('{'))
            and
            (a := self.star_named_expressions())
            and
            (self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Set ( elts = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def dict(self) -> Optional[ast . Dict]:
        # dict: '{' double_starred_kvpairs? '}' | '{' invalid_double_starred_kvpairs '}'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('{'))
            and
            (a := self.double_starred_kvpairs(),)
            and
            (self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Dict ( keys = [kv [0] for kv in ( a or [] )] , values = [kv [1] for kv in ( a or [] )] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.expect('{'))
            and
            (self.invalid_double_starred_kvpairs())
            and
            (self.expect('}'))
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def double_starred_kvpairs(self) -> Optional[list]:
        # double_starred_kvpairs: ','.double_starred_kvpair+ ','?
        mark = self._mark()
        if (
            (a := self._gather_150())
            and
            (self.expect(','),)
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def double_starred_kvpair(self) -> Optional[Any]:
        # double_starred_kvpair: '**' bitwise_or | kvpair
        mark = self._mark()
        if (
            (self.expect('**'))
            and
            (a := self.bitwise_or())
        ):
            return ( None , a );
        self._reset(mark)
        if (
            (kvpair := self.kvpair())
        ):
            return kvpair;
        self._reset(mark)
        return None;

    @memoize
    def kvpair(self) -> Optional[tuple]:
        # kvpair: expression ':' expression
        mark = self._mark()
        if (
            (a := self.expression())
            and
            (self.expect(':'))
            and
            (b := self.expression())
        ):
            return ( a , b );
        self._reset(mark)
        return None;

    @memoize
    def for_if_clauses(self) -> Optional[List [ast . comprehension]]:
        # for_if_clauses: for_if_clause+
        mark = self._mark()
        if (
            (a := self._loop1_152())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def for_if_clause(self) -> Optional[ast . comprehension]:
        # for_if_clause: 'async' 'for' star_targets 'in' ~ disjunction (('if' disjunction))* | 'for' star_targets 'in' ~ disjunction (('if' disjunction))* | invalid_for_target
        mark = self._mark()
        cut = False
        if (
            (self.expect('async'))
            and
            (self.expect('for'))
            and
            (a := self.star_targets())
            and
            (self.expect('in'))
            and
            (cut := True)
            and
            (b := self.disjunction())
            and
            (c := self._loop0_153(),)
        ):
            return self . check_version ( ( 3 , 6 ) , "Async comprehensions are" , ast . comprehension ( target = a , iter = b , ifs = c , is_async = 1 ) );
        self._reset(mark)
        if cut:
            return None;
        cut = False
        if (
            (self.expect('for'))
            and
            (a := self.star_targets())
            and
            (self.expect('in'))
            and
            (cut := True)
            and
            (b := self.disjunction())
            and
            (c := self._loop0_154(),)
        ):
            return ast . comprehension ( target = a , iter = b , ifs = c , is_async = 0 );
        self._reset(mark)
        if cut:
            return None;
        if (
            self.call_invalid_rules
            and
            (self.invalid_for_target())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def listcomp(self) -> Optional[ast . ListComp]:
        # listcomp: '[' named_expression for_if_clauses ']' | invalid_comprehension
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('['))
            and
            (a := self.named_expression())
            and
            (b := self.for_if_clauses())
            and
            (self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ListComp ( elt = a , generators = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_comprehension())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def setcomp(self) -> Optional[ast . SetComp]:
        # setcomp: '{' named_expression for_if_clauses '}' | invalid_comprehension
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('{'))
            and
            (a := self.named_expression())
            and
            (b := self.for_if_clauses())
            and
            (self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . SetComp ( elt = a , generators = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_comprehension())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def genexp(self) -> Optional[ast . GeneratorExp]:
        # genexp: '(' (assignment_expression | expression !':=') for_if_clauses ')' | invalid_comprehension
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('('))
            and
            (a := self._tmp_155())
            and
            (b := self.for_if_clauses())
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . GeneratorExp ( elt = a , generators = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_comprehension())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def dictcomp(self) -> Optional[ast . DictComp]:
        # dictcomp: '{' kvpair for_if_clauses '}' | invalid_dict_comprehension
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('{'))
            and
            (a := self.kvpair())
            and
            (b := self.for_if_clauses())
            and
            (self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . DictComp ( key = a [0] , value = a [1] , generators = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_dict_comprehension())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def arguments(self) -> Optional[Tuple [list , list]]:
        # arguments: args ','? &')' | invalid_arguments
        mark = self._mark()
        if (
            (a := self.args())
            and
            (self.expect(','),)
            and
            (self.positive_lookahead(self.expect, ')'))
        ):
            return a;
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_arguments())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def args(self) -> Optional[Tuple [list , list]]:
        # args: ','.(starred_expression | (assignment_expression | expression !':=') !'=')+ [',' kwargs] | kwargs
        mark = self._mark()
        if (
            (a := self._gather_156())
            and
            (b := self._tmp_158(),)
        ):
            return ( a + ( [e for e in b if isinstance ( e , ast . Starred )] if b else [] ) , ( [e for e in b if not isinstance ( e , ast . Starred )] if b else [] ) );
        self._reset(mark)
        if (
            (a := self.kwargs())
        ):
            return ( [e for e in a if isinstance ( e , ast . Starred )] , [e for e in a if not isinstance ( e , ast . Starred )] );
        self._reset(mark)
        return None;

    @memoize
    def kwargs(self) -> Optional[list]:
        # kwargs: ','.kwarg_or_starred+ ',' ','.kwarg_or_double_starred+ | ','.kwarg_or_starred+ | ','.kwarg_or_double_starred+
        mark = self._mark()
        if (
            (a := self._gather_159())
            and
            (self.expect(','))
            and
            (b := self._gather_161())
        ):
            return a + b;
        self._reset(mark)
        if (
            (_gather_163 := self._gather_163())
        ):
            return _gather_163;
        self._reset(mark)
        if (
            (_gather_165 := self._gather_165())
        ):
            return _gather_165;
        self._reset(mark)
        return None;

    @memoize
    def starred_expression(self) -> Optional[Any]:
        # starred_expression: invalid_starred_expression | '*' expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_starred_expression())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (a := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Starred ( value = a , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def kwarg_or_starred(self) -> Optional[Any]:
        # kwarg_or_starred: invalid_kwarg | NAME '=' expression | starred_expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_kwarg())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (a := self.name())
            and
            (self.expect('='))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . keyword ( arg = a . string , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.starred_expression())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def kwarg_or_double_starred(self) -> Optional[Any]:
        # kwarg_or_double_starred: invalid_kwarg | NAME '=' expression | '**' expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            self.call_invalid_rules
            and
            (self.invalid_kwarg())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (a := self.name())
            and
            (self.expect('='))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . keyword ( arg = a . string , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('**'))
            and
            (a := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . keyword ( arg = None , value = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def star_targets(self) -> Optional[Any]:
        # star_targets: star_target !',' | star_target ((',' star_target))* ','?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.star_target())
            and
            (self.negative_lookahead(self.expect, ','))
        ):
            return a;
        self._reset(mark)
        if (
            (a := self.star_target())
            and
            (b := self._loop0_167(),)
            and
            (self.expect(','),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = [a] + b , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def star_targets_list_seq(self) -> Optional[list]:
        # star_targets_list_seq: ','.star_target+ ','?
        mark = self._mark()
        if (
            (a := self._gather_168())
            and
            (self.expect(','),)
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def star_targets_tuple_seq(self) -> Optional[list]:
        # star_targets_tuple_seq: star_target ((',' star_target))+ ','? | star_target ','
        mark = self._mark()
        if (
            (a := self.star_target())
            and
            (b := self._loop1_170())
            and
            (self.expect(','),)
        ):
            return [a] + b;
        self._reset(mark)
        if (
            (a := self.star_target())
            and
            (self.expect(','))
        ):
            return [a];
        self._reset(mark)
        return None;

    @memoize
    def star_target(self) -> Optional[Any]:
        # star_target: '*' (!'*' star_target) | target_with_star_atom
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('*'))
            and
            (a := self._tmp_171())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Starred ( value = self . set_expr_context ( a , Store ) , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (target_with_star_atom := self.target_with_star_atom())
        ):
            return target_with_star_atom;
        self._reset(mark)
        return None;

    @memoize
    def target_with_star_atom(self) -> Optional[Any]:
        # target_with_star_atom: t_primary '.' NAME !t_lookahead | t_primary '[' slices ']' !t_lookahead | star_atom
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.t_primary())
            and
            (self.expect('.'))
            and
            (b := self.name())
            and
            (self.negative_lookahead(self.t_lookahead, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (self.expect('['))
            and
            (b := self.slices())
            and
            (self.expect(']'))
            and
            (self.negative_lookahead(self.t_lookahead, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Subscript ( value = a , slice = b , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (star_atom := self.star_atom())
        ):
            return star_atom;
        self._reset(mark)
        return None;

    @memoize
    def star_atom(self) -> Optional[Any]:
        # star_atom: NAME | '(' target_with_star_atom ')' | '(' star_targets_tuple_seq? ')' | '[' star_targets_list_seq? ']'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = a . string , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('('))
            and
            (a := self.target_with_star_atom())
            and
            (self.expect(')'))
        ):
            return self . set_expr_context ( a , Store );
        self._reset(mark)
        if (
            (self.expect('('))
            and
            (a := self.star_targets_tuple_seq(),)
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = a , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('['))
            and
            (a := self.star_targets_list_seq(),)
            and
            (self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . List ( elts = a , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def single_target(self) -> Optional[Any]:
        # single_target: single_subscript_attribute_target | NAME | '(' single_target ')'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (single_subscript_attribute_target := self.single_subscript_attribute_target())
        ):
            return single_subscript_attribute_target;
        self._reset(mark)
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = a . string , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('('))
            and
            (a := self.single_target())
            and
            (self.expect(')'))
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def single_subscript_attribute_target(self) -> Optional[Any]:
        # single_subscript_attribute_target: t_primary '.' NAME !t_lookahead | t_primary '[' slices ']' !t_lookahead
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.t_primary())
            and
            (self.expect('.'))
            and
            (b := self.name())
            and
            (self.negative_lookahead(self.t_lookahead, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (self.expect('['))
            and
            (b := self.slices())
            and
            (self.expect(']'))
            and
            (self.negative_lookahead(self.t_lookahead, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Subscript ( value = a , slice = b , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize_left_rec
    def t_primary(self) -> Optional[Any]:
        # t_primary: t_primary '.' NAME &t_lookahead | t_primary '[' slices ']' &t_lookahead | t_primary genexp &t_lookahead | t_primary '(' arguments? ')' &t_lookahead | atom &t_lookahead
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.t_primary())
            and
            (self.expect('.'))
            and
            (b := self.name())
            and
            (self.positive_lookahead(self.t_lookahead, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (self.expect('['))
            and
            (b := self.slices())
            and
            (self.expect(']'))
            and
            (self.positive_lookahead(self.t_lookahead, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Subscript ( value = a , slice = b , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (b := self.genexp())
            and
            (self.positive_lookahead(self.t_lookahead, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Call ( func = a , args = [b] , keywords = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (self.expect('('))
            and
            (b := self.arguments(),)
            and
            (self.expect(')'))
            and
            (self.positive_lookahead(self.t_lookahead, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Call ( func = a , args = b [0] if b else [] , keywords = b [1] if b else [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        if (
            (a := self.atom())
            and
            (self.positive_lookahead(self.t_lookahead, ))
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def t_lookahead(self) -> Optional[Any]:
        # t_lookahead: '(' | '[' | '.'
        mark = self._mark()
        if (
            (literal := self.expect('('))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('['))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('.'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def del_targets(self) -> Optional[Any]:
        # del_targets: ','.del_target+ ','?
        mark = self._mark()
        if (
            (a := self._gather_172())
            and
            (self.expect(','),)
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def del_target(self) -> Optional[Any]:
        # del_target: t_primary '.' NAME !t_lookahead | t_primary '[' slices ']' !t_lookahead | del_t_atom
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.t_primary())
            and
            (self.expect('.'))
            and
            (b := self.name())
            and
            (self.negative_lookahead(self.t_lookahead, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Del , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (self.expect('['))
            and
            (b := self.slices())
            and
            (self.expect(']'))
            and
            (self.negative_lookahead(self.t_lookahead, ))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Subscript ( value = a , slice = b , ctx = Del , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (del_t_atom := self.del_t_atom())
        ):
            return del_t_atom;
        self._reset(mark)
        return None;

    @memoize
    def del_t_atom(self) -> Optional[Any]:
        # del_t_atom: NAME | '(' del_target ')' | '(' del_targets? ')' | '[' del_targets? ']'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = a . string , ctx = Del , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('('))
            and
            (a := self.del_target())
            and
            (self.expect(')'))
        ):
            return self . set_expr_context ( a , Del );
        self._reset(mark)
        if (
            (self.expect('('))
            and
            (a := self.del_targets(),)
            and
            (self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = a , ctx = Del , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('['))
            and
            (a := self.del_targets(),)
            and
            (self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . List ( elts = a , ctx = Del , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def type_expressions(self) -> Optional[list]:
        # type_expressions: ','.expression+ ',' '*' expression ',' '**' expression | ','.expression+ ',' '*' expression | ','.expression+ ',' '**' expression | '*' expression ',' '**' expression | '*' expression | '**' expression | ','.expression+
        mark = self._mark()
        if (
            (a := self._gather_174())
            and
            (self.expect(','))
            and
            (self.expect('*'))
            and
            (b := self.expression())
            and
            (self.expect(','))
            and
            (self.expect('**'))
            and
            (c := self.expression())
        ):
            return a + [b , c];
        self._reset(mark)
        if (
            (a := self._gather_176())
            and
            (self.expect(','))
            and
            (self.expect('*'))
            and
            (b := self.expression())
        ):
            return a + [b];
        self._reset(mark)
        if (
            (a := self._gather_178())
            and
            (self.expect(','))
            and
            (self.expect('**'))
            and
            (b := self.expression())
        ):
            return a + [b];
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (a := self.expression())
            and
            (self.expect(','))
            and
            (self.expect('**'))
            and
            (b := self.expression())
        ):
            return [a , b];
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (a := self.expression())
        ):
            return [a];
        self._reset(mark)
        if (
            (self.expect('**'))
            and
            (a := self.expression())
        ):
            return [a];
        self._reset(mark)
        if (
            (a := self._gather_180())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def func_type_comment(self) -> Optional[Any]:
        # func_type_comment: NEWLINE TYPE_COMMENT &(NEWLINE INDENT) | invalid_double_type_comments | TYPE_COMMENT
        mark = self._mark()
        if (
            (self.expect('NEWLINE'))
            and
            (t := self.type_comment())
            and
            (self.positive_lookahead(self._tmp_182, ))
        ):
            return t . string;
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.invalid_double_type_comments())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (type_comment := self.type_comment())
        ):
            return type_comment;
        self._reset(mark)
        return None;

    @memoize
    def invalid_arguments(self) -> Optional[NoReturn]:
        # invalid_arguments: args ',' '*' | expression for_if_clauses ',' [args | expression for_if_clauses] | NAME '=' expression for_if_clauses | [(args ',')] NAME '=' &(',' | ')') | args for_if_clauses | args ',' expression for_if_clauses | args ',' args
        mark = self._mark()
        if (
            (a := self.args())
            and
            (self.expect(','))
            and
            (self.expect('*'))
        ):
            return self . raise_syntax_error_known_location ( "iterable argument unpacking follows keyword argument unpacking" , a [1] [- 1] if a [1] else a [0] [- 1] , );
        self._reset(mark)
        if (
            (a := self.expression())
            and
            (b := self.for_if_clauses())
            and
            (self.expect(','))
            and
            (self._tmp_183(),)
        ):
            return self . raise_syntax_error_known_range ( "Generator expression must be parenthesized" , a , ( b [- 1] . ifs [- 1] if b [- 1] . ifs else b [- 1] . iter ) );
        self._reset(mark)
        if (
            (a := self.name())
            and
            (b := self.expect('='))
            and
            (self.expression())
            and
            (self.for_if_clauses())
        ):
            return self . raise_syntax_error_known_range ( "invalid syntax. Maybe you meant '==' or ':=' instead of '='?" , a , b );
        self._reset(mark)
        if (
            (self._tmp_184(),)
            and
            (a := self.name())
            and
            (b := self.expect('='))
            and
            (self.positive_lookahead(self._tmp_185, ))
        ):
            return self . raise_syntax_error_known_range ( "expected argument value expression" , a , b );
        self._reset(mark)
        if (
            (a := self.args())
            and
            (b := self.for_if_clauses())
        ):
            return self . raise_syntax_error_known_range ( "Generator expression must be parenthesized" , a [0] [- 1] , ( b [- 1] . ifs [- 1] if b [- 1] . ifs else b [- 1] . iter ) , ) if len ( a [0] ) > 1 else None;
        self._reset(mark)
        if (
            (self.args())
            and
            (self.expect(','))
            and
            (a := self.expression())
            and
            (b := self.for_if_clauses())
        ):
            return self . raise_syntax_error_known_range ( "Generator expression must be parenthesized" , a , ( b [- 1] . ifs [- 1] if b [- 1] . ifs else b [- 1] . iter ) , );
        self._reset(mark)
        if (
            (a := self.args())
            and
            (self.expect(','))
            and
            (self.args())
        ):
            return self . raise_syntax_error ( "positional argument follows keyword argument unpacking" if a [1] [- 1] . arg is None else "positional argument follows keyword argument" , );
        self._reset(mark)
        return None;

    @memoize
    def invalid_kwarg(self) -> Optional[NoReturn]:
        # invalid_kwarg: ('True' | 'False' | 'None') '=' | NAME '=' expression for_if_clauses | !(NAME '=') expression '=' | '**' expression '=' expression
        mark = self._mark()
        if (
            (a := self._tmp_186())
            and
            (b := self.expect('='))
        ):
            return self . raise_syntax_error_known_range ( f"cannot assign to {a.string}" , a , b );
        self._reset(mark)
        if (
            (a := self.name())
            and
            (b := self.expect('='))
            and
            (self.expression())
            and
            (self.for_if_clauses())
        ):
            return self . raise_syntax_error_known_range ( "invalid syntax. Maybe you meant '==' or ':=' instead of '='?" , a , b );
        self._reset(mark)
        if (
            (self.negative_lookahead(self._tmp_187, ))
            and
            (a := self.expression())
            and
            (b := self.expect('='))
        ):
            return self . raise_syntax_error_known_range ( "expression cannot contain assignment, perhaps you meant \"==\"?" , a , b , );
        self._reset(mark)
        if (
            (a := self.expect('**'))
            and
            (self.expression())
            and
            (self.expect('='))
            and
            (b := self.expression())
        ):
            return self . raise_syntax_error_known_range ( "cannot assign to keyword argument unpacking" , a , b );
        self._reset(mark)
        return None;

    @memoize
    def expression_without_invalid(self) -> Optional[ast . AST]:
        # expression_without_invalid: disjunction 'if' disjunction 'else' expression | disjunction | lambdef
        _prev_call_invalid = self.call_invalid_rules
        self.call_invalid_rules = False
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.disjunction())
            and
            (self.expect('if'))
            and
            (b := self.disjunction())
            and
            (self.expect('else'))
            and
            (c := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            self.call_invalid_rules = _prev_call_invalid
            return ast . IfExp ( body = b , test = a , orelse = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (disjunction := self.disjunction())
        ):
            self.call_invalid_rules = _prev_call_invalid
            return disjunction;
        self._reset(mark)
        if (
            (lambdef := self.lambdef())
        ):
            self.call_invalid_rules = _prev_call_invalid
            return lambdef;
        self._reset(mark)
        self.call_invalid_rules = _prev_call_invalid
        return None;

    @memoize
    def invalid_legacy_expression(self) -> Optional[Any]:
        # invalid_legacy_expression: NAME !'(' star_expressions
        mark = self._mark()
        if (
            (a := self.name())
            and
            (self.negative_lookahead(self.expect, '('))
            and
            (b := self.star_expressions())
        ):
            return self . raise_syntax_error_known_range ( f"Missing parentheses in call to '{a.string}' . Did you mean {a.string}(...)?" , a , b , ) if a . string in ( "exec" , "print" ) else None;
        self._reset(mark)
        return None;

    @memoize
    def invalid_expression(self) -> Optional[NoReturn]:
        # invalid_expression: !(NAME STRING | SOFT_KEYWORD) disjunction expression_without_invalid | disjunction 'if' disjunction !('else' | ':') | 'lambda' lambda_params? ':' &(FSTRING_MIDDLE | fstring_replacement_field)
        mark = self._mark()
        if (
            (self.negative_lookahead(self._tmp_188, ))
            and
            (a := self.disjunction())
            and
            (b := self.expression_without_invalid())
        ):
            return ( self . raise_syntax_error_known_range ( "invalid syntax. Perhaps you forgot a comma?" , a , b ) if not isinstance ( a , ast . Name ) or a . id not in ( "print" , "exec" ) else None );
        self._reset(mark)
        if (
            (a := self.disjunction())
            and
            (self.expect('if'))
            and
            (b := self.disjunction())
            and
            (self.negative_lookahead(self._tmp_189, ))
        ):
            return self . raise_syntax_error_known_range ( "expected 'else' after 'if' expression" , a , b );
        self._reset(mark)
        if (
            (a := self.expect('lambda'))
            and
            (self.lambda_params(),)
            and
            (b := self.expect(':'))
            and
            (self.positive_lookahead(self._tmp_190, ))
        ):
            return self . raise_syntax_error_known_range ( "f-string: lambda expressions are not allowed without parentheses" , a , b );
        self._reset(mark)
        return None;

    @memoize
    def invalid_named_expression(self) -> Optional[NoReturn]:
        # invalid_named_expression: expression ':=' expression | NAME '=' bitwise_or !('=' | ':=') | !(list | tuple | genexp | 'True' | 'None' | 'False') bitwise_or '=' bitwise_or !('=' | ':=')
        mark = self._mark()
        if (
            (a := self.expression())
            and
            (self.expect(':='))
            and
            (self.expression())
        ):
            return self . raise_syntax_error_known_location ( f"cannot use assignment expressions with {self.get_expr_name(a)}" , a );
        self._reset(mark)
        if (
            (a := self.name())
            and
            (self.expect('='))
            and
            (b := self.bitwise_or())
            and
            (self.negative_lookahead(self._tmp_191, ))
        ):
            return ( None if self . in_recursive_rule else self . raise_syntax_error_known_range ( "invalid syntax. Maybe you meant '==' or ':=' instead of '='?" , a , b ) );
        self._reset(mark)
        if (
            (self.negative_lookahead(self._tmp_192, ))
            and
            (a := self.bitwise_or())
            and
            (self.expect('='))
            and
            (self.bitwise_or())
            and
            (self.negative_lookahead(self._tmp_193, ))
        ):
            return ( None if self . in_recursive_rule else self . raise_syntax_error_known_location ( f"cannot assign to {self.get_expr_name(a)} here. Maybe you meant '==' instead of '='?" , a ) );
        self._reset(mark)
        return None;

    @memoize
    def invalid_assignment(self) -> Optional[NoReturn]:
        # invalid_assignment: invalid_ann_assign_target ':' expression | star_named_expression ',' star_named_expressions* ':' expression | expression ':' expression | ((star_targets '='))* star_expressions '=' | ((star_targets '='))* yield_expr '=' | star_expressions augassign (yield_expr | star_expressions)
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (a := self.invalid_ann_assign_target())
            and
            (self.expect(':'))
            and
            (self.expression())
        ):
            return self . raise_syntax_error_known_location ( f"only single target (not {self.get_expr_name(a)}) can be annotated" , a );
        self._reset(mark)
        if (
            (a := self.star_named_expression())
            and
            (self.expect(','))
            and
            (self._loop0_194(),)
            and
            (self.expect(':'))
            and
            (self.expression())
        ):
            return self . raise_syntax_error_known_location ( "only single target (not tuple) can be annotated" , a );
        self._reset(mark)
        if (
            (a := self.expression())
            and
            (self.expect(':'))
            and
            (self.expression())
        ):
            return self . raise_syntax_error_known_location ( "illegal target for annotation" , a );
        self._reset(mark)
        if (
            (self._loop0_195(),)
            and
            (a := self.star_expressions())
            and
            (self.expect('='))
        ):
            return self . raise_syntax_error_invalid_target ( Target . STAR_TARGETS , a );
        self._reset(mark)
        if (
            (self._loop0_196(),)
            and
            (a := self.yield_expr())
            and
            (self.expect('='))
        ):
            return self . raise_syntax_error_known_location ( "assignment to yield expression not possible" , a );
        self._reset(mark)
        if (
            (a := self.star_expressions())
            and
            (self.augassign())
            and
            (self._tmp_197())
        ):
            return self . raise_syntax_error_known_location ( f"'{self.get_expr_name(a)}' is an illegal expression for augmented assignment" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_ann_assign_target(self) -> Optional[ast . AST]:
        # invalid_ann_assign_target: list | tuple | '(' invalid_ann_assign_target ')'
        mark = self._mark()
        if (
            (a := self.list())
        ):
            return a;
        self._reset(mark)
        if (
            (a := self.tuple())
        ):
            return a;
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.expect('('))
            and
            (a := self.invalid_ann_assign_target())
            and
            (self.expect(')'))
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def invalid_del_stmt(self) -> Optional[NoReturn]:
        # invalid_del_stmt: 'del' star_expressions
        mark = self._mark()
        if (
            (self.expect('del'))
            and
            (a := self.star_expressions())
        ):
            return self . raise_syntax_error_invalid_target ( Target . DEL_TARGETS , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_block(self) -> Optional[NoReturn]:
        # invalid_block: NEWLINE !INDENT
        mark = self._mark()
        if (
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( "expected an indented block" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_comprehension(self) -> Optional[NoReturn]:
        # invalid_comprehension: ('[' | '(' | '{') starred_expression for_if_clauses | ('[' | '{') star_named_expression ',' star_named_expressions for_if_clauses | ('[' | '{') star_named_expression ',' for_if_clauses
        mark = self._mark()
        if (
            (self._tmp_198())
            and
            (a := self.starred_expression())
            and
            (self.for_if_clauses())
        ):
            return self . raise_syntax_error_known_location ( "iterable unpacking cannot be used in comprehension" , a );
        self._reset(mark)
        if (
            (self._tmp_199())
            and
            (a := self.star_named_expression())
            and
            (self.expect(','))
            and
            (b := self.star_named_expressions())
            and
            (self.for_if_clauses())
        ):
            return self . raise_syntax_error_known_range ( "did you forget parentheses around the comprehension target?" , a , b [- 1] );
        self._reset(mark)
        if (
            (self._tmp_200())
            and
            (a := self.star_named_expression())
            and
            (b := self.expect(','))
            and
            (self.for_if_clauses())
        ):
            return self . raise_syntax_error_known_range ( "did you forget parentheses around the comprehension target?" , a , b );
        self._reset(mark)
        return None;

    @memoize
    def invalid_dict_comprehension(self) -> Optional[NoReturn]:
        # invalid_dict_comprehension: '{' '**' bitwise_or for_if_clauses '}'
        mark = self._mark()
        if (
            (self.expect('{'))
            and
            (a := self.expect('**'))
            and
            (self.bitwise_or())
            and
            (self.for_if_clauses())
            and
            (self.expect('}'))
        ):
            return self . raise_syntax_error_known_location ( "dict unpacking cannot be used in dict comprehension" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_parameters(self) -> Optional[NoReturn]:
        # invalid_parameters: "/" ',' | (slash_no_default | slash_with_default) param_maybe_default* '/' | slash_no_default? param_no_default* invalid_parameters_helper param_no_default | param_no_default* '(' param_no_default+ ','? ')' | [(slash_no_default | slash_with_default)] param_maybe_default* '*' (',' | param_no_default) param_maybe_default* '/' | param_maybe_default+ '/' '*'
        mark = self._mark()
        if (
            (a := self.expect("/"))
            and
            (self.expect(','))
        ):
            return self . raise_syntax_error_known_location ( "at least one argument must precede /" , a );
        self._reset(mark)
        if (
            (self._tmp_201())
            and
            (self._loop0_202(),)
            and
            (a := self.expect('/'))
        ):
            return self . raise_syntax_error_known_location ( "/ may appear only once" , a );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.slash_no_default(),)
            and
            (self._loop0_203(),)
            and
            (self.invalid_parameters_helper())
            and
            (a := self.param_no_default())
        ):
            return self . raise_syntax_error_known_location ( "parameter without a default follows parameter with a default" , a );
        self._reset(mark)
        if (
            (self._loop0_204(),)
            and
            (a := self.expect('('))
            and
            (self._loop1_205())
            and
            (self.expect(','),)
            and
            (b := self.expect(')'))
        ):
            return self . raise_syntax_error_known_range ( "Function parameters cannot be parenthesized" , a , b );
        self._reset(mark)
        if (
            (self._tmp_206(),)
            and
            (self._loop0_207(),)
            and
            (self.expect('*'))
            and
            (self._tmp_208())
            and
            (self._loop0_209(),)
            and
            (a := self.expect('/'))
        ):
            return self . raise_syntax_error_known_location ( "/ must be ahead of *" , a );
        self._reset(mark)
        if (
            (self._loop1_210())
            and
            (self.expect('/'))
            and
            (a := self.expect('*'))
        ):
            return self . raise_syntax_error_known_location ( "expected comma between / and *" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_default(self) -> Optional[Any]:
        # invalid_default: '=' &(')' | ',')
        mark = self._mark()
        if (
            (a := self.expect('='))
            and
            (self.positive_lookahead(self._tmp_211, ))
        ):
            return self . raise_syntax_error_known_location ( "expected default value expression" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_star_etc(self) -> Optional[Any]:
        # invalid_star_etc: '*' (')' | ',' (')' | '**')) | '*' ',' TYPE_COMMENT | '*' param '=' | '*' (param_no_default | ',') param_maybe_default* '*' (param_no_default | ',')
        mark = self._mark()
        if (
            (a := self.expect('*'))
            and
            (self._tmp_212())
        ):
            return self . raise_syntax_error_known_location ( "named arguments must follow bare *" , a );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (self.expect(','))
            and
            (self.type_comment())
        ):
            return self . raise_syntax_error ( "bare * has associated type comment" );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (self.param())
            and
            (a := self.expect('='))
        ):
            return self . raise_syntax_error_known_location ( "var-positional argument cannot have default value" , a );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (self._tmp_213())
            and
            (self._loop0_214(),)
            and
            (a := self.expect('*'))
            and
            (self._tmp_215())
        ):
            return self . raise_syntax_error_known_location ( "* argument may appear only once" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_kwds(self) -> Optional[Any]:
        # invalid_kwds: '**' param '=' | '**' param ',' param | '**' param ',' ('*' | '**' | '/')
        mark = self._mark()
        if (
            (self.expect('**'))
            and
            (self.param())
            and
            (a := self.expect('='))
        ):
            return self . raise_syntax_error_known_location ( "var-keyword argument cannot have default value" , a );
        self._reset(mark)
        if (
            (self.expect('**'))
            and
            (self.param())
            and
            (self.expect(','))
            and
            (a := self.param())
        ):
            return self . raise_syntax_error_known_location ( "arguments cannot follow var-keyword argument" , a );
        self._reset(mark)
        if (
            (self.expect('**'))
            and
            (self.param())
            and
            (self.expect(','))
            and
            (a := self._tmp_216())
        ):
            return self . raise_syntax_error_known_location ( "arguments cannot follow var-keyword argument" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_parameters_helper(self) -> Optional[Any]:
        # invalid_parameters_helper: slash_with_default | param_with_default+
        mark = self._mark()
        if (
            (a := self.slash_with_default())
        ):
            return [a];
        self._reset(mark)
        if (
            (a := self._loop1_217())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def invalid_lambda_parameters(self) -> Optional[NoReturn]:
        # invalid_lambda_parameters: "/" ',' | (lambda_slash_no_default | lambda_slash_with_default) lambda_param_maybe_default* '/' | lambda_slash_no_default? lambda_param_no_default* invalid_lambda_parameters_helper lambda_param_no_default | lambda_param_no_default* '(' ','.lambda_param+ ','? ')' | [(lambda_slash_no_default | lambda_slash_with_default)] lambda_param_maybe_default* '*' (',' | lambda_param_no_default) lambda_param_maybe_default* '/' | lambda_param_maybe_default+ '/' '*'
        mark = self._mark()
        if (
            (a := self.expect("/"))
            and
            (self.expect(','))
        ):
            return self . raise_syntax_error_known_location ( "at least one argument must precede /" , a );
        self._reset(mark)
        if (
            (self._tmp_218())
            and
            (self._loop0_219(),)
            and
            (a := self.expect('/'))
        ):
            return self . raise_syntax_error_known_location ( "/ may appear only once" , a );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.lambda_slash_no_default(),)
            and
            (self._loop0_220(),)
            and
            (self.invalid_lambda_parameters_helper())
            and
            (a := self.lambda_param_no_default())
        ):
            return self . raise_syntax_error_known_location ( "parameter without a default follows parameter with a default" , a );
        self._reset(mark)
        if (
            (self._loop0_221(),)
            and
            (a := self.expect('('))
            and
            (self._gather_222())
            and
            (self.expect(','),)
            and
            (b := self.expect(')'))
        ):
            return self . raise_syntax_error_known_range ( "Lambda expression parameters cannot be parenthesized" , a , b );
        self._reset(mark)
        if (
            (self._tmp_224(),)
            and
            (self._loop0_225(),)
            and
            (self.expect('*'))
            and
            (self._tmp_226())
            and
            (self._loop0_227(),)
            and
            (a := self.expect('/'))
        ):
            return self . raise_syntax_error_known_location ( "/ must be ahead of *" , a );
        self._reset(mark)
        if (
            (self._loop1_228())
            and
            (self.expect('/'))
            and
            (a := self.expect('*'))
        ):
            return self . raise_syntax_error_known_location ( "expected comma between / and *" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_lambda_parameters_helper(self) -> Optional[NoReturn]:
        # invalid_lambda_parameters_helper: lambda_slash_with_default | lambda_param_with_default+
        mark = self._mark()
        if (
            (a := self.lambda_slash_with_default())
        ):
            return [a];
        self._reset(mark)
        if (
            (a := self._loop1_229())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def invalid_lambda_star_etc(self) -> Optional[NoReturn]:
        # invalid_lambda_star_etc: '*' (':' | ',' (':' | '**')) | '*' lambda_param '=' | '*' (lambda_param_no_default | ',') lambda_param_maybe_default* '*' (lambda_param_no_default | ',')
        mark = self._mark()
        if (
            (self.expect('*'))
            and
            (self._tmp_230())
        ):
            return self . raise_syntax_error ( "named arguments must follow bare *" );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (self.lambda_param())
            and
            (a := self.expect('='))
        ):
            return self . raise_syntax_error_known_location ( "var-positional argument cannot have default value" , a );
        self._reset(mark)
        if (
            (self.expect('*'))
            and
            (self._tmp_231())
            and
            (self._loop0_232(),)
            and
            (a := self.expect('*'))
            and
            (self._tmp_233())
        ):
            return self . raise_syntax_error_known_location ( "* argument may appear only once" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_lambda_kwds(self) -> Optional[Any]:
        # invalid_lambda_kwds: '**' lambda_param '=' | '**' lambda_param ',' lambda_param | '**' lambda_param ',' ('*' | '**' | '/')
        mark = self._mark()
        if (
            (self.expect('**'))
            and
            (self.lambda_param())
            and
            (a := self.expect('='))
        ):
            return self . raise_syntax_error_known_location ( "var-keyword argument cannot have default value" , a );
        self._reset(mark)
        if (
            (self.expect('**'))
            and
            (self.lambda_param())
            and
            (self.expect(','))
            and
            (a := self.lambda_param())
        ):
            return self . raise_syntax_error_known_location ( "arguments cannot follow var-keyword argument" , a );
        self._reset(mark)
        if (
            (self.expect('**'))
            and
            (self.lambda_param())
            and
            (self.expect(','))
            and
            (a := self._tmp_234())
        ):
            return self . raise_syntax_error_known_location ( "arguments cannot follow var-keyword argument" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_double_type_comments(self) -> Optional[NoReturn]:
        # invalid_double_type_comments: TYPE_COMMENT NEWLINE TYPE_COMMENT NEWLINE INDENT
        mark = self._mark()
        if (
            (self.type_comment())
            and
            (self.expect('NEWLINE'))
            and
            (self.type_comment())
            and
            (self.expect('NEWLINE'))
            and
            (self.expect('INDENT'))
        ):
            return self . raise_syntax_error ( "Cannot have two type comments on def" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_with_item(self) -> Optional[NoReturn]:
        # invalid_with_item: expression 'as' expression &(',' | ')' | ':')
        mark = self._mark()
        if (
            (self.expression())
            and
            (self.expect('as'))
            and
            (a := self.expression())
            and
            (self.positive_lookahead(self._tmp_235, ))
        ):
            return self . raise_syntax_error_invalid_target ( Target . STAR_TARGETS , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_for_target(self) -> Optional[NoReturn]:
        # invalid_for_target: 'async'? 'for' star_expressions
        mark = self._mark()
        if (
            (self.expect('async'),)
            and
            (self.expect('for'))
            and
            (a := self.star_expressions())
        ):
            return self . raise_syntax_error_invalid_target ( Target . FOR_TARGETS , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_group(self) -> Optional[NoReturn]:
        # invalid_group: '(' starred_expression ')' | '(' '**' expression ')'
        mark = self._mark()
        if (
            (self.expect('('))
            and
            (a := self.starred_expression())
            and
            (self.expect(')'))
        ):
            return self . raise_syntax_error_known_location ( "cannot use starred expression here" , a );
        self._reset(mark)
        if (
            (self.expect('('))
            and
            (a := self.expect('**'))
            and
            (self.expression())
            and
            (self.expect(')'))
        ):
            return self . raise_syntax_error_known_location ( "cannot use double starred expression here" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_import(self) -> Optional[Any]:
        # invalid_import: 'import' ','.dotted_name+ 'from' dotted_name
        mark = self._mark()
        if (
            (a := self.expect('import'))
            and
            (self._gather_236())
            and
            (self.expect('from'))
            and
            (self.dotted_name())
        ):
            return self . raise_syntax_error_starting_from ( "Did you mean to use 'from ... import ...' instead?" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_import_from_targets(self) -> Optional[NoReturn]:
        # invalid_import_from_targets: import_from_as_names ',' NEWLINE
        mark = self._mark()
        if (
            (self.import_from_as_names())
            and
            (self.expect(','))
            and
            (self.expect('NEWLINE'))
        ):
            return self . raise_syntax_error ( "trailing comma not allowed without surrounding parentheses" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_with_stmt(self) -> Optional[None]:
        # invalid_with_stmt: 'async'? 'with' ','.(expression ['as' star_target])+ &&':' | 'async'? 'with' '(' ','.(expressions ['as' star_target])+ ','? ')' &&':'
        mark = self._mark()
        if (
            (self.expect('async'),)
            and
            (self.expect('with'))
            and
            (self._gather_238())
            and
            (self.expect_forced(self.expect(':'), "':'"))
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('async'),)
            and
            (self.expect('with'))
            and
            (self.expect('('))
            and
            (self._gather_240())
            and
            (self.expect(','),)
            and
            (self.expect(')'))
            and
            (self.expect_forced(self.expect(':'), "':'"))
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        return None;

    @memoize
    def invalid_with_stmt_indent(self) -> Optional[NoReturn]:
        # invalid_with_stmt_indent: 'async'? 'with' ','.(expression ['as' star_target])+ ':' NEWLINE !INDENT | 'async'? 'with' '(' ','.(expressions ['as' star_target])+ ','? ')' ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (self.expect('async'),)
            and
            (a := self.expect('with'))
            and
            (self._gather_242())
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'with' statement on line {a.start[0]}" );
        self._reset(mark)
        if (
            (self.expect('async'),)
            and
            (a := self.expect('with'))
            and
            (self.expect('('))
            and
            (self._gather_244())
            and
            (self.expect(','),)
            and
            (self.expect(')'))
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'with' statement on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_try_stmt(self) -> Optional[NoReturn]:
        # invalid_try_stmt: 'try' ':' NEWLINE !INDENT | 'try' ':' block !('except' | 'finally') | 'try' ':' block* except_block+ 'except' '*' expression ['as' NAME] ':' | 'try' ':' block* except_star_block+ 'except' [expression ['as' NAME]] ':'
        mark = self._mark()
        if (
            (a := self.expect('try'))
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'try' statement on line {a.start[0]}" , );
        self._reset(mark)
        if (
            (self.expect('try'))
            and
            (self.expect(':'))
            and
            (self.block())
            and
            (self.negative_lookahead(self._tmp_246, ))
        ):
            return self . raise_syntax_error ( "expected 'except' or 'finally' block" );
        self._reset(mark)
        if (
            (self.expect('try'))
            and
            (self.expect(':'))
            and
            (self._loop0_247(),)
            and
            (self._loop1_248())
            and
            (a := self.expect('except'))
            and
            (b := self.expect('*'))
            and
            (self.expression())
            and
            (self._tmp_249(),)
            and
            (self.expect(':'))
        ):
            return self . raise_syntax_error_known_range ( "cannot have both 'except' and 'except*' on the same 'try'" , a , b );
        self._reset(mark)
        if (
            (self.expect('try'))
            and
            (self.expect(':'))
            and
            (self._loop0_250(),)
            and
            (self._loop1_251())
            and
            (a := self.expect('except'))
            and
            (self._tmp_252(),)
            and
            (self.expect(':'))
        ):
            return self . raise_syntax_error_known_location ( "cannot have both 'except' and 'except*' on the same 'try'" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_except_stmt(self) -> Optional[None]:
        # invalid_except_stmt: 'except' '*'? expression ',' expressions ['as' NAME] ':' | 'except' '*'? expression ['as' NAME] NEWLINE | 'except' '*'? NEWLINE | 'except' '*' (NEWLINE | ':')
        mark = self._mark()
        if (
            (self.expect('except'))
            and
            (self.expect('*'),)
            and
            (a := self.expression())
            and
            (self.expect(','))
            and
            (self.expressions())
            and
            (self._tmp_253(),)
            and
            (self.expect(':'))
        ):
            return self . raise_syntax_error_starting_from ( "multiple exception types must be parenthesized" , a );
        self._reset(mark)
        if (
            (self.expect('except'))
            and
            (self.expect('*'),)
            and
            (self.expression())
            and
            (self._tmp_254(),)
            and
            (self.expect('NEWLINE'))
        ):
            return self . raise_syntax_error ( "expected ':'" );
        self._reset(mark)
        if (
            (self.expect('except'))
            and
            (self.expect('*'),)
            and
            (self.expect('NEWLINE'))
        ):
            return self . raise_syntax_error ( "expected ':'" );
        self._reset(mark)
        if (
            (self.expect('except'))
            and
            (self.expect('*'))
            and
            (self._tmp_255())
        ):
            return self . raise_syntax_error ( "expected one or more exception types" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_finally_stmt(self) -> Optional[NoReturn]:
        # invalid_finally_stmt: 'finally' ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (a := self.expect('finally'))
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'finally' statement on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_except_stmt_indent(self) -> Optional[NoReturn]:
        # invalid_except_stmt_indent: 'except' expression ['as' NAME] ':' NEWLINE !INDENT | 'except' ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (a := self.expect('except'))
            and
            (self.expression())
            and
            (self._tmp_256(),)
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'except' statement on line {a.start[0]}" );
        self._reset(mark)
        if (
            (a := self.expect('except'))
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'except' statement on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_except_star_stmt_indent(self) -> Optional[Any]:
        # invalid_except_star_stmt_indent: 'except' '*' expression ['as' NAME] ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (a := self.expect('except'))
            and
            (self.expect('*'))
            and
            (self.expression())
            and
            (self._tmp_257(),)
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'except*' statement on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_match_stmt(self) -> Optional[NoReturn]:
        # invalid_match_stmt: "match" subject_expr !':' | "match" subject_expr ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (self.expect("match"))
            and
            (self.subject_expr())
            and
            (self.negative_lookahead(self.expect, ':'))
        ):
            return self . check_version ( ( 3 , 10 ) , "Pattern matching is" , self . raise_syntax_error ( "expected ':'" ) );
        self._reset(mark)
        if (
            (a := self.expect("match"))
            and
            (self.subject_expr())
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . check_version ( ( 3 , 10 ) , "Pattern matching is" , self . raise_indentation_error ( f"expected an indented block after 'match' statement on line {a.start[0]}" ) );
        self._reset(mark)
        return None;

    @memoize
    def invalid_case_block(self) -> Optional[NoReturn]:
        # invalid_case_block: "case" patterns guard? !':' | "case" patterns guard? ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (self.expect("case"))
            and
            (self.patterns())
            and
            (self.guard(),)
            and
            (self.negative_lookahead(self.expect, ':'))
        ):
            return self . raise_syntax_error ( "expected ':'" );
        self._reset(mark)
        if (
            (a := self.expect("case"))
            and
            (self.patterns())
            and
            (self.guard(),)
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'case' statement on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_as_pattern(self) -> Optional[NoReturn]:
        # invalid_as_pattern: or_pattern 'as' "_" | or_pattern 'as' !NAME expression
        mark = self._mark()
        if (
            (self.or_pattern())
            and
            (self.expect('as'))
            and
            (a := self.expect("_"))
        ):
            return self . raise_syntax_error_known_location ( "cannot use '_' as a target" , a );
        self._reset(mark)
        if (
            (self.or_pattern())
            and
            (self.expect('as'))
            and
            (self.negative_lookahead(self.name, ))
            and
            (a := self.expression())
        ):
            return self . raise_syntax_error_known_location ( "invalid pattern target" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_class_pattern(self) -> Optional[NoReturn]:
        # invalid_class_pattern: name_or_attr '(' invalid_class_argument_pattern
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self.name_or_attr())
            and
            (self.expect('('))
            and
            (a := self.invalid_class_argument_pattern())
        ):
            return self . raise_syntax_error_known_range ( "positional patterns follow keyword patterns" , a [0] , a [- 1] );
        self._reset(mark)
        return None;

    @memoize
    def invalid_class_argument_pattern(self) -> Optional[list]:
        # invalid_class_argument_pattern: [positional_patterns ','] keyword_patterns ',' positional_patterns
        mark = self._mark()
        if (
            (self._tmp_258(),)
            and
            (self.keyword_patterns())
            and
            (self.expect(','))
            and
            (a := self.positional_patterns())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def invalid_if_stmt(self) -> Optional[NoReturn]:
        # invalid_if_stmt: 'if' named_expression NEWLINE | 'if' named_expression ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (self.expect('if'))
            and
            (self.named_expression())
            and
            (self.expect('NEWLINE'))
        ):
            return self . raise_syntax_error ( "expected ':'" );
        self._reset(mark)
        if (
            (a := self.expect('if'))
            and
            (a_1 := self.named_expression())
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'if' statement on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_elif_stmt(self) -> Optional[NoReturn]:
        # invalid_elif_stmt: 'elif' named_expression NEWLINE | 'elif' named_expression ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (self.expect('elif'))
            and
            (self.named_expression())
            and
            (self.expect('NEWLINE'))
        ):
            return self . raise_syntax_error ( "expected ':'" );
        self._reset(mark)
        if (
            (a := self.expect('elif'))
            and
            (self.named_expression())
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'elif' statement on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_else_stmt(self) -> Optional[NoReturn]:
        # invalid_else_stmt: 'else' ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (a := self.expect('else'))
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'else' statement on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_while_stmt(self) -> Optional[NoReturn]:
        # invalid_while_stmt: 'while' named_expression NEWLINE | 'while' named_expression ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (self.expect('while'))
            and
            (self.named_expression())
            and
            (self.expect('NEWLINE'))
        ):
            return self . raise_syntax_error ( "expected ':'" );
        self._reset(mark)
        if (
            (a := self.expect('while'))
            and
            (self.named_expression())
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'while' statement on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_for_stmt(self) -> Optional[NoReturn]:
        # invalid_for_stmt: 'async'? 'for' star_targets 'in' star_expressions NEWLINE | 'async'? 'for' star_targets 'in' star_expressions ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (self.expect('async'),)
            and
            (self.expect('for'))
            and
            (self.star_targets())
            and
            (self.expect('in'))
            and
            (self.star_expressions())
            and
            (self.expect('NEWLINE'))
        ):
            return self . raise_syntax_error ( "expected ':'" );
        self._reset(mark)
        if (
            (self.expect('async'),)
            and
            (a := self.expect('for'))
            and
            (self.star_targets())
            and
            (self.expect('in'))
            and
            (self.star_expressions())
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'for' statement on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_def_raw(self) -> Optional[NoReturn]:
        # invalid_def_raw: 'async'? 'def' NAME type_params? '(' params? ')' ['->' expression] ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (self.expect('async'),)
            and
            (a := self.expect('def'))
            and
            (self.name())
            and
            (self.type_params(),)
            and
            (self.expect('('))
            and
            (self.params(),)
            and
            (self.expect(')'))
            and
            (self._tmp_259(),)
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after function definition on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_class_def_raw(self) -> Optional[NoReturn]:
        # invalid_class_def_raw: 'class' NAME type_params? ['(' arguments? ')'] NEWLINE | 'class' NAME type_params? ['(' arguments? ')'] ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (self.expect('class'))
            and
            (self.name())
            and
            (self.type_params(),)
            and
            (self._tmp_260(),)
            and
            (self.expect('NEWLINE'))
        ):
            return self . raise_syntax_error ( "expected ':'" );
        self._reset(mark)
        if (
            (a := self.expect('class'))
            and
            (self.name())
            and
            (self.type_params(),)
            and
            (self._tmp_261(),)
            and
            (self.expect(':'))
            and
            (self.expect('NEWLINE'))
            and
            (self.negative_lookahead(self.expect, 'INDENT'))
        ):
            return self . raise_indentation_error ( f"expected an indented block after class definition on line {a.start[0]}" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_double_starred_kvpairs(self) -> Optional[None]:
        # invalid_double_starred_kvpairs: ','.double_starred_kvpair+ ',' invalid_kvpair | expression ':' '*' bitwise_or | expression ':' &('}' | ',')
        mark = self._mark()
        if (
            self.call_invalid_rules
            and
            (self._gather_262())
            and
            (self.expect(','))
            and
            (self.invalid_kvpair())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expression())
            and
            (self.expect(':'))
            and
            (a := self.expect('*'))
            and
            (self.bitwise_or())
        ):
            return self . raise_syntax_error_starting_from ( "cannot use a starred expression in a dictionary value" , a );
        self._reset(mark)
        if (
            (self.expression())
            and
            (a := self.expect(':'))
            and
            (self.positive_lookahead(self._tmp_264, ))
        ):
            return self . raise_syntax_error_known_location ( "expression expected after dictionary key and ':'" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_kvpair(self) -> Optional[None]:
        # invalid_kvpair: expression !(':') | expression ':' '*' bitwise_or | expression ':' &('}' | ',') | expression ':'
        mark = self._mark()
        if (
            (a := self.expression())
            and
            (self.negative_lookahead(self.expect, ':'))
        ):
            return self . raise_raw_syntax_error ( "':' expected after dictionary key" , ( a . lineno , a . col_offset ) , ( a . end_lineno , a . end_col_offset ) );
        self._reset(mark)
        if (
            (self.expression())
            and
            (self.expect(':'))
            and
            (a := self.expect('*'))
            and
            (self.bitwise_or())
        ):
            return self . raise_syntax_error_starting_from ( "cannot use a starred expression in a dictionary value" , a );
        self._reset(mark)
        if (
            (self.expression())
            and
            (a := self.expect(':'))
            and
            (self.positive_lookahead(self._tmp_265, ))
        ):
            return self . raise_syntax_error_known_location ( "expression expected after dictionary key and ':'" , a );
        self._reset(mark)
        if (
            (self.expression())
            and
            (a := self.expect(':'))
        ):
            return self . raise_syntax_error_known_location ( "expression expected after dictionary key and ':'" , a );
        self._reset(mark)
        return None;

    @memoize
    def invalid_starred_expression(self) -> Optional[Any]:
        # invalid_starred_expression: '*' expression '=' expression
        mark = self._mark()
        if (
            (a := self.expect('*'))
            and
            (self.expression())
            and
            (self.expect('='))
            and
            (b := self.expression())
        ):
            return self . raise_syntax_error_known_range ( "cannot assign to iterable argument unpacking" , a , b );
        self._reset(mark)
        return None;

    @memoize
    def invalid_replacement_field(self) -> Optional[Any]:
        # invalid_replacement_field: '{' '=' | '{' '!' | '{' ':' | '{' '}' | '{' !(yield_expr | star_expressions) | '{' (yield_expr | star_expressions) !('=' | '!' | ':' | '}') | '{' (yield_expr | star_expressions) '=' !('!' | ':' | '}') | '{' (yield_expr | star_expressions) '='? invalid_conversion_character | '{' (yield_expr | star_expressions) '='? ['!' NAME] !(':' | '}') | '{' (yield_expr | star_expressions) '='? ['!' NAME] ':' fstring_format_spec* !'}' | '{' (yield_expr | star_expressions) '='? ['!' NAME] !'}'
        mark = self._mark()
        if (
            (self.expect('{'))
            and
            (a := self.expect('='))
        ):
            return self . raise_syntax_error_known_location ( "f-string: valid expression required before '='" , a );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (a := self.expect('!'))
        ):
            return self . raise_syntax_error_known_location ( "f-string: valid expression required before '!'" , a );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (a := self.expect(':'))
        ):
            return self . raise_syntax_error_known_location ( "f-string: valid expression required before ':'" , a );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (a := self.expect('}'))
        ):
            return self . raise_syntax_error_known_location ( "f-string: valid expression required before '}'" , a );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (self.negative_lookahead(self._tmp_266, ))
        ):
            return self . raise_syntax_error_on_next_token ( "f-string: expecting a valid expression after '{'" );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (self._tmp_267())
            and
            (self.negative_lookahead(self._tmp_268, ))
        ):
            return self . raise_syntax_error_on_next_token ( "f-string: expecting '=', or '!', or ':', or '}'" );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (self._tmp_269())
            and
            (self.expect('='))
            and
            (self.negative_lookahead(self._tmp_270, ))
        ):
            return self . raise_syntax_error_on_next_token ( "f-string: expecting '!', or ':', or '}'" );
        self._reset(mark)
        if (
            self.call_invalid_rules
            and
            (self.expect('{'))
            and
            (self._tmp_271())
            and
            (self.expect('='),)
            and
            (self.invalid_conversion_character())
        ):
            return None  # pragma: no cover;
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (self._tmp_272())
            and
            (self.expect('='),)
            and
            (self._tmp_273(),)
            and
            (self.negative_lookahead(self._tmp_274, ))
        ):
            return self . raise_syntax_error_on_next_token ( "f-string: expecting ':' or '}'" );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (self._tmp_275())
            and
            (self.expect('='),)
            and
            (self._tmp_276(),)
            and
            (self.expect(':'))
            and
            (self._loop0_277(),)
            and
            (self.negative_lookahead(self.expect, '}'))
        ):
            return self . raise_syntax_error_on_next_token ( "f-string: expecting '}', or format specs" );
        self._reset(mark)
        if (
            (self.expect('{'))
            and
            (self._tmp_278())
            and
            (self.expect('='),)
            and
            (self._tmp_279(),)
            and
            (self.negative_lookahead(self.expect, '}'))
        ):
            return self . raise_syntax_error_on_next_token ( "f-string: expecting '}'" );
        self._reset(mark)
        return None;

    @memoize
    def invalid_conversion_character(self) -> Optional[Any]:
        # invalid_conversion_character: '!' &(':' | '}') | '!' !NAME
        mark = self._mark()
        if (
            (self.expect('!'))
            and
            (self.positive_lookahead(self._tmp_280, ))
        ):
            return self . raise_syntax_error_on_next_token ( "f-string: missing conversion character" );
        self._reset(mark)
        if (
            (self.expect('!'))
            and
            (self.negative_lookahead(self.name, ))
        ):
            return self . raise_syntax_error_on_next_token ( "f-string: invalid conversion character" );
        self._reset(mark)
        return None;

    @memoize
    def _loop0_1(self) -> Optional[Any]:
        # _loop0_1: enaml_item
        mark = self._mark()
        children = []
        while (
            (enaml_item := self.enaml_item())
        ):
            children.append(enaml_item)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_2(self) -> Optional[Any]:
        # _loop0_2: pragma
        mark = self._mark()
        children = []
        while (
            (pragma := self.pragma())
        ):
            children.append(pragma)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_3(self) -> Optional[Any]:
        # _tmp_3: ':' NAME
        mark = self._mark()
        if (
            (self.expect(':'))
            and
            (z := self.name())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_4(self) -> Optional[Any]:
        # _loop1_4: enamldef_item
        mark = self._mark()
        children = []
        while (
            (enamldef_item := self.enamldef_item())
        ):
            children.append(enamldef_item)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_5(self) -> Optional[Any]:
        # _loop1_5: enamldef_item
        mark = self._mark()
        children = []
        while (
            (enamldef_item := self.enamldef_item())
        ):
            children.append(enamldef_item)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_6(self) -> Optional[Any]:
        # _loop1_6: pragma
        mark = self._mark()
        children = []
        while (
            (pragma := self.pragma())
        ):
            children.append(pragma)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_7(self) -> Optional[Any]:
        # _tmp_7: '(' ','.pragma_arg+ ')'
        mark = self._mark()
        if (
            (self.expect('('))
            and
            (b := self._gather_281())
            and
            (self.expect(')'))
        ):
            return b;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_8(self) -> Optional[Any]:
        # _tmp_8: ':' '.'.NAME+
        mark = self._mark()
        if (
            (self.expect(':'))
            and
            (c := self._gather_283())
        ):
            return c;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_9(self) -> Optional[Any]:
        # _tmp_9: ':' dec_primary
        mark = self._mark()
        if (
            (self.expect(':'))
            and
            (c := self.dec_primary())
        ):
            return c;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_10(self) -> Optional[Any]:
        # _tmp_10: "attr" | "event"
        mark = self._mark()
        if (
            (literal := self.expect("attr"))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect("event"))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_11(self) -> Optional[Any]:
        # _tmp_11: ':' dec_primary
        mark = self._mark()
        if (
            (self.expect(':'))
            and
            (d := self.dec_primary())
        ):
            return d;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_12(self) -> Optional[Any]:
        # _tmp_12: "attr" | "event"
        mark = self._mark()
        if (
            (literal := self.expect("attr"))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect("event"))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_13(self) -> Optional[Any]:
        # _tmp_13: ':' dec_primary
        mark = self._mark()
        if (
            (self.expect(':'))
            and
            (d := self.dec_primary())
        ):
            return d;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_14(self) -> Optional[Any]:
        # _loop1_14: child_def_item
        mark = self._mark()
        children = []
        while (
            (child_def_item := self.child_def_item())
        ):
            children.append(child_def_item)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_16(self) -> Optional[Any]:
        # _loop0_16: '.' NAME
        mark = self._mark()
        children = []
        while (
            (self.expect('.'))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_15(self) -> Optional[Any]:
        # _gather_15: NAME _loop0_16
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_16())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_17(self) -> Optional[Any]:
        # _tmp_17: '=' | '<<'
        mark = self._mark()
        if (
            (literal := self.expect('='))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('<<'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_18(self) -> Optional[Any]:
        # _tmp_18: '>>' | ':='
        mark = self._mark()
        if (
            (literal := self.expect('>>'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(':='))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_19(self) -> Optional[Any]:
        # _tmp_19: '->' expression
        mark = self._mark()
        if (
            (self.expect('->'))
            and
            (z := self.expression())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_20(self) -> Optional[Any]:
        # _tmp_20: '->' expression
        mark = self._mark()
        if (
            (self.expect('->'))
            and
            (z := self.expression())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_21(self) -> Optional[Any]:
        # _loop1_21: template_item
        mark = self._mark()
        children = []
        while (
            (template_item := self.template_item())
        ):
            children.append(template_item)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_22(self) -> Optional[Any]:
        # _loop1_22: template_item
        mark = self._mark()
        children = []
        while (
            (template_item := self.template_item())
        ):
            children.append(template_item)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_24(self) -> Optional[Any]:
        # _loop0_24: ',' template_param
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.template_param())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_23(self) -> Optional[Any]:
        # _gather_23: template_param _loop0_24
        mark = self._mark()
        if (
            (elem := self.template_param())
            is not None
            and
            (seq := self._loop0_24())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_25(self) -> Optional[Any]:
        # _tmp_25: ',' '*' NAME
        mark = self._mark()
        if (
            (self.expect(','))
            and
            (self.expect('*'))
            and
            (c := self.name())
        ):
            return c;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_26(self) -> Optional[Any]:
        # _tmp_26: ':' template_ids
        mark = self._mark()
        if (
            (self.expect(':'))
            and
            (z := self.template_ids())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_28(self) -> Optional[Any]:
        # _loop0_28: ',' template_argument
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.template_argument())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_27(self) -> Optional[Any]:
        # _gather_27: template_argument _loop0_28
        mark = self._mark()
        if (
            (elem := self.template_argument())
            is not None
            and
            (seq := self._loop0_28())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_29(self) -> Optional[Any]:
        # _tmp_29: ',' '*' expression
        mark = self._mark()
        if (
            (self.expect(','))
            and
            (self.expect('*'))
            and
            (z := self.expression())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_31(self) -> Optional[Any]:
        # _loop0_31: ',' NAME
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_30(self) -> Optional[Any]:
        # _gather_30: NAME _loop0_31
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_31())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_32(self) -> Optional[Any]:
        # _tmp_32: ',' '*' NAME
        mark = self._mark()
        if (
            (self.expect(','))
            and
            (self.expect('*'))
            and
            (z := self.name())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_33(self) -> Optional[Any]:
        # _loop1_33: template_inst_item
        mark = self._mark()
        children = []
        while (
            (template_inst_item := self.template_inst_item())
        ):
            children.append(template_inst_item)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_34(self) -> Optional[Any]:
        # _tmp_34: '.' '.'.NAME+
        mark = self._mark()
        if (
            (self.expect('.'))
            and
            (z := self._gather_285())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_35(self) -> Optional[Any]:
        # _loop1_35: statement
        mark = self._mark()
        children = []
        while (
            (statement := self.statement())
        ):
            children.append(statement)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_37(self) -> Optional[Any]:
        # _loop0_37: ';' simple_stmt
        mark = self._mark()
        children = []
        while (
            (self.expect(';'))
            and
            (elem := self.simple_stmt())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_36(self) -> Optional[Any]:
        # _gather_36: simple_stmt _loop0_37
        mark = self._mark()
        if (
            (elem := self.simple_stmt())
            is not None
            and
            (seq := self._loop0_37())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_38(self) -> Optional[Any]:
        # _tmp_38: 'import' | 'from'
        mark = self._mark()
        if (
            (literal := self.expect('import'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('from'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_39(self) -> Optional[Any]:
        # _tmp_39: 'def' | '@' | 'async'
        mark = self._mark()
        if (
            (literal := self.expect('def'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('@'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('async'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_40(self) -> Optional[Any]:
        # _tmp_40: 'class' | '@'
        mark = self._mark()
        if (
            (literal := self.expect('class'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('@'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_41(self) -> Optional[Any]:
        # _tmp_41: 'with' | 'async'
        mark = self._mark()
        if (
            (literal := self.expect('with'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('async'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_42(self) -> Optional[Any]:
        # _tmp_42: 'for' | 'async'
        mark = self._mark()
        if (
            (literal := self.expect('for'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('async'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_43(self) -> Optional[Any]:
        # _tmp_43: '=' annotated_rhs
        mark = self._mark()
        if (
            (self.expect('='))
            and
            (d := self.annotated_rhs())
        ):
            return d;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_44(self) -> Optional[Any]:
        # _tmp_44: '(' single_target ')' | single_subscript_attribute_target
        mark = self._mark()
        if (
            (self.expect('('))
            and
            (b := self.single_target())
            and
            (self.expect(')'))
        ):
            return b;
        self._reset(mark)
        if (
            (single_subscript_attribute_target := self.single_subscript_attribute_target())
        ):
            return single_subscript_attribute_target;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_45(self) -> Optional[Any]:
        # _tmp_45: '=' annotated_rhs
        mark = self._mark()
        if (
            (self.expect('='))
            and
            (d := self.annotated_rhs())
        ):
            return d;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_46(self) -> Optional[Any]:
        # _loop1_46: (star_targets '=')
        mark = self._mark()
        children = []
        while (
            (_tmp_287 := self._tmp_287())
        ):
            children.append(_tmp_287)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_47(self) -> Optional[Any]:
        # _tmp_47: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_48(self) -> Optional[Any]:
        # _tmp_48: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_49(self) -> Optional[Any]:
        # _tmp_49: 'from' expression
        mark = self._mark()
        if (
            (self.expect('from'))
            and
            (z := self.expression())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_51(self) -> Optional[Any]:
        # _loop0_51: ',' NAME
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_50(self) -> Optional[Any]:
        # _gather_50: NAME _loop0_51
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_51())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_53(self) -> Optional[Any]:
        # _loop0_53: ',' NAME
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_52(self) -> Optional[Any]:
        # _gather_52: NAME _loop0_53
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_53())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_54(self) -> Optional[Any]:
        # _tmp_54: ';' | NEWLINE
        mark = self._mark()
        if (
            (literal := self.expect(';'))
        ):
            return literal;
        self._reset(mark)
        if (
            (_newline := self.expect('NEWLINE'))
        ):
            return _newline;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_55(self) -> Optional[Any]:
        # _tmp_55: ',' expression
        mark = self._mark()
        if (
            (self.expect(','))
            and
            (z := self.expression())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_56(self) -> Optional[Any]:
        # _loop0_56: ('.' | '...')
        mark = self._mark()
        children = []
        while (
            (_tmp_288 := self._tmp_288())
        ):
            children.append(_tmp_288)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_57(self) -> Optional[Any]:
        # _loop1_57: ('.' | '...')
        mark = self._mark()
        children = []
        while (
            (_tmp_289 := self._tmp_289())
        ):
            children.append(_tmp_289)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_59(self) -> Optional[Any]:
        # _loop0_59: ',' import_from_as_name
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.import_from_as_name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_58(self) -> Optional[Any]:
        # _gather_58: import_from_as_name _loop0_59
        mark = self._mark()
        if (
            (elem := self.import_from_as_name())
            is not None
            and
            (seq := self._loop0_59())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_60(self) -> Optional[Any]:
        # _tmp_60: 'as' NAME
        mark = self._mark()
        if (
            (self.expect('as'))
            and
            (z := self.name())
        ):
            return z . string;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_62(self) -> Optional[Any]:
        # _loop0_62: ',' dotted_as_name
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.dotted_as_name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_61(self) -> Optional[Any]:
        # _gather_61: dotted_as_name _loop0_62
        mark = self._mark()
        if (
            (elem := self.dotted_as_name())
            is not None
            and
            (seq := self._loop0_62())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_63(self) -> Optional[Any]:
        # _tmp_63: 'as' NAME
        mark = self._mark()
        if (
            (self.expect('as'))
            and
            (z := self.name())
        ):
            return z . string;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_64(self) -> Optional[Any]:
        # _loop1_64: decorator
        mark = self._mark()
        children = []
        while (
            (decorator := self.decorator())
        ):
            children.append(decorator)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_65(self) -> Optional[Any]:
        # _tmp_65: '@' dec_maybe_call NEWLINE
        mark = self._mark()
        if (
            (self.expect('@'))
            and
            (f := self.dec_maybe_call())
            and
            (self.expect('NEWLINE'))
        ):
            return f;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_66(self) -> Optional[Any]:
        # _tmp_66: '@' named_expression NEWLINE
        mark = self._mark()
        if (
            (self.expect('@'))
            and
            (f := self.named_expression())
            and
            (self.expect('NEWLINE'))
        ):
            return f;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_67(self) -> Optional[Any]:
        # _tmp_67: '(' arguments? ')'
        mark = self._mark()
        if (
            (self.expect('('))
            and
            (z := self.arguments(),)
            and
            (self.expect(')'))
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_68(self) -> Optional[Any]:
        # _tmp_68: '->' expression
        mark = self._mark()
        if (
            (self.expect('->'))
            and
            (z := self.expression())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_69(self) -> Optional[Any]:
        # _tmp_69: '->' expression
        mark = self._mark()
        if (
            (self.expect('->'))
            and
            (z := self.expression())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_70(self) -> Optional[Any]:
        # _loop0_70: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_71(self) -> Optional[Any]:
        # _loop0_71: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_72(self) -> Optional[Any]:
        # _loop0_72: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_73(self) -> Optional[Any]:
        # _loop1_73: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_74(self) -> Optional[Any]:
        # _loop0_74: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_75(self) -> Optional[Any]:
        # _loop1_75: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_76(self) -> Optional[Any]:
        # _loop1_76: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_77(self) -> Optional[Any]:
        # _loop1_77: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_78(self) -> Optional[Any]:
        # _loop0_78: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_79(self) -> Optional[Any]:
        # _loop1_79: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_80(self) -> Optional[Any]:
        # _loop0_80: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_81(self) -> Optional[Any]:
        # _loop1_81: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_82(self) -> Optional[Any]:
        # _loop0_82: param_maybe_default
        mark = self._mark()
        children = []
        while (
            (param_maybe_default := self.param_maybe_default())
        ):
            children.append(param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_83(self) -> Optional[Any]:
        # _loop0_83: param_maybe_default
        mark = self._mark()
        children = []
        while (
            (param_maybe_default := self.param_maybe_default())
        ):
            children.append(param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_84(self) -> Optional[Any]:
        # _loop1_84: param_maybe_default
        mark = self._mark()
        children = []
        while (
            (param_maybe_default := self.param_maybe_default())
        ):
            children.append(param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_86(self) -> Optional[Any]:
        # _loop0_86: ',' with_item
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.with_item())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_85(self) -> Optional[Any]:
        # _gather_85: with_item _loop0_86
        mark = self._mark()
        if (
            (elem := self.with_item())
            is not None
            and
            (seq := self._loop0_86())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_88(self) -> Optional[Any]:
        # _loop0_88: ',' with_item
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.with_item())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_87(self) -> Optional[Any]:
        # _gather_87: with_item _loop0_88
        mark = self._mark()
        if (
            (elem := self.with_item())
            is not None
            and
            (seq := self._loop0_88())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_90(self) -> Optional[Any]:
        # _loop0_90: ',' with_item
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.with_item())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_89(self) -> Optional[Any]:
        # _gather_89: with_item _loop0_90
        mark = self._mark()
        if (
            (elem := self.with_item())
            is not None
            and
            (seq := self._loop0_90())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_92(self) -> Optional[Any]:
        # _loop0_92: ',' with_item
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.with_item())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_91(self) -> Optional[Any]:
        # _gather_91: with_item _loop0_92
        mark = self._mark()
        if (
            (elem := self.with_item())
            is not None
            and
            (seq := self._loop0_92())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_93(self) -> Optional[Any]:
        # _tmp_93: ',' | ')' | ':'
        mark = self._mark()
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(')'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(':'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_94(self) -> Optional[Any]:
        # _loop1_94: except_block
        mark = self._mark()
        children = []
        while (
            (except_block := self.except_block())
        ):
            children.append(except_block)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_95(self) -> Optional[Any]:
        # _loop1_95: except_star_block
        mark = self._mark()
        children = []
        while (
            (except_star_block := self.except_star_block())
        ):
            children.append(except_star_block)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_96(self) -> Optional[Any]:
        # _tmp_96: 'as' NAME
        mark = self._mark()
        if (
            (self.expect('as'))
            and
            (z := self.name())
        ):
            return z . string;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_97(self) -> Optional[Any]:
        # _tmp_97: 'as' NAME
        mark = self._mark()
        if (
            (self.expect('as'))
            and
            (z := self.name())
        ):
            return z . string;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_98(self) -> Optional[Any]:
        # _loop1_98: case_block
        mark = self._mark()
        children = []
        while (
            (case_block := self.case_block())
        ):
            children.append(case_block)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_100(self) -> Optional[Any]:
        # _loop0_100: '|' closed_pattern
        mark = self._mark()
        children = []
        while (
            (self.expect('|'))
            and
            (elem := self.closed_pattern())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_99(self) -> Optional[Any]:
        # _gather_99: closed_pattern _loop0_100
        mark = self._mark()
        if (
            (elem := self.closed_pattern())
            is not None
            and
            (seq := self._loop0_100())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_101(self) -> Optional[Any]:
        # _tmp_101: '+' | '-'
        mark = self._mark()
        if (
            (literal := self.expect('+'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('-'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_102(self) -> Optional[Any]:
        # _tmp_102: '+' | '-'
        mark = self._mark()
        if (
            (literal := self.expect('+'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('-'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_103(self) -> Optional[Any]:
        # _tmp_103: '.' | '(' | '='
        mark = self._mark()
        if (
            (literal := self.expect('.'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('('))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('='))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_104(self) -> Optional[Any]:
        # _tmp_104: '.' | '(' | '='
        mark = self._mark()
        if (
            (literal := self.expect('.'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('('))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('='))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_106(self) -> Optional[Any]:
        # _loop0_106: ',' maybe_star_pattern
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.maybe_star_pattern())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_105(self) -> Optional[Any]:
        # _gather_105: maybe_star_pattern _loop0_106
        mark = self._mark()
        if (
            (elem := self.maybe_star_pattern())
            is not None
            and
            (seq := self._loop0_106())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_108(self) -> Optional[Any]:
        # _loop0_108: ',' key_value_pattern
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.key_value_pattern())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_107(self) -> Optional[Any]:
        # _gather_107: key_value_pattern _loop0_108
        mark = self._mark()
        if (
            (elem := self.key_value_pattern())
            is not None
            and
            (seq := self._loop0_108())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_109(self) -> Optional[Any]:
        # _tmp_109: literal_expr | attr
        mark = self._mark()
        if (
            (literal_expr := self.literal_expr())
        ):
            return literal_expr;
        self._reset(mark)
        if (
            (attr := self.attr())
        ):
            return attr;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_111(self) -> Optional[Any]:
        # _loop0_111: ',' pattern
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.pattern())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_110(self) -> Optional[Any]:
        # _gather_110: pattern _loop0_111
        mark = self._mark()
        if (
            (elem := self.pattern())
            is not None
            and
            (seq := self._loop0_111())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_113(self) -> Optional[Any]:
        # _loop0_113: ',' keyword_pattern
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.keyword_pattern())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_112(self) -> Optional[Any]:
        # _gather_112: keyword_pattern _loop0_113
        mark = self._mark()
        if (
            (elem := self.keyword_pattern())
            is not None
            and
            (seq := self._loop0_113())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_115(self) -> Optional[Any]:
        # _loop0_115: ',' type_param
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.type_param())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_114(self) -> Optional[Any]:
        # _gather_114: type_param _loop0_115
        mark = self._mark()
        if (
            (elem := self.type_param())
            is not None
            and
            (seq := self._loop0_115())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_116(self) -> Optional[Any]:
        # _loop1_116: (',' expression)
        mark = self._mark()
        children = []
        while (
            (_tmp_290 := self._tmp_290())
        ):
            children.append(_tmp_290)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_117(self) -> Optional[Any]:
        # _loop1_117: (',' star_expression)
        mark = self._mark()
        children = []
        while (
            (_tmp_291 := self._tmp_291())
        ):
            children.append(_tmp_291)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_119(self) -> Optional[Any]:
        # _loop0_119: ',' star_named_expression
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.star_named_expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_118(self) -> Optional[Any]:
        # _gather_118: star_named_expression _loop0_119
        mark = self._mark()
        if (
            (elem := self.star_named_expression())
            is not None
            and
            (seq := self._loop0_119())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_120(self) -> Optional[Any]:
        # _loop1_120: ('or' conjunction)
        mark = self._mark()
        children = []
        while (
            (_tmp_292 := self._tmp_292())
        ):
            children.append(_tmp_292)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_121(self) -> Optional[Any]:
        # _loop1_121: ('and' inversion)
        mark = self._mark()
        children = []
        while (
            (_tmp_293 := self._tmp_293())
        ):
            children.append(_tmp_293)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_122(self) -> Optional[Any]:
        # _loop1_122: compare_op_bitwise_or_pair
        mark = self._mark()
        children = []
        while (
            (compare_op_bitwise_or_pair := self.compare_op_bitwise_or_pair())
        ):
            children.append(compare_op_bitwise_or_pair)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_124(self) -> Optional[Any]:
        # _loop0_124: ',' (slice | starred_expression)
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self._tmp_294())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_123(self) -> Optional[Any]:
        # _gather_123: (slice | starred_expression) _loop0_124
        mark = self._mark()
        if (
            (elem := self._tmp_294())
            is not None
            and
            (seq := self._loop0_124())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_125(self) -> Optional[Any]:
        # _tmp_125: ':' expression?
        mark = self._mark()
        if (
            (self.expect(':'))
            and
            (d := self.expression(),)
        ):
            return d;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_126(self) -> Optional[Any]:
        # _tmp_126: STRING | FSTRING_START
        mark = self._mark()
        if (
            (string := self.string())
        ):
            return string;
        self._reset(mark)
        if (
            (fstring_start := self.fstring_start())
        ):
            return fstring_start;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_127(self) -> Optional[Any]:
        # _tmp_127: tuple | group | genexp
        mark = self._mark()
        if (
            (tuple := self.tuple())
        ):
            return tuple;
        self._reset(mark)
        if (
            (group := self.group())
        ):
            return group;
        self._reset(mark)
        if (
            (genexp := self.genexp())
        ):
            return genexp;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_128(self) -> Optional[Any]:
        # _tmp_128: list | listcomp
        mark = self._mark()
        if (
            (list := self.list())
        ):
            return list;
        self._reset(mark)
        if (
            (listcomp := self.listcomp())
        ):
            return listcomp;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_129(self) -> Optional[Any]:
        # _tmp_129: dict | set | dictcomp | setcomp
        mark = self._mark()
        if (
            (dict := self.dict())
        ):
            return dict;
        self._reset(mark)
        if (
            (set := self.set())
        ):
            return set;
        self._reset(mark)
        if (
            (dictcomp := self.dictcomp())
        ):
            return dictcomp;
        self._reset(mark)
        if (
            (setcomp := self.setcomp())
        ):
            return setcomp;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_130(self) -> Optional[Any]:
        # _tmp_130: yield_expr | named_expression
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (named_expression := self.named_expression())
        ):
            return named_expression;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_131(self) -> Optional[Any]:
        # _loop0_131: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_132(self) -> Optional[Any]:
        # _loop0_132: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_133(self) -> Optional[Any]:
        # _loop0_133: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_134(self) -> Optional[Any]:
        # _loop1_134: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_135(self) -> Optional[Any]:
        # _loop0_135: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_136(self) -> Optional[Any]:
        # _loop1_136: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_137(self) -> Optional[Any]:
        # _loop1_137: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_138(self) -> Optional[Any]:
        # _loop1_138: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_139(self) -> Optional[Any]:
        # _loop0_139: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_140(self) -> Optional[Any]:
        # _loop1_140: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_141(self) -> Optional[Any]:
        # _loop0_141: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_142(self) -> Optional[Any]:
        # _loop1_142: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_143(self) -> Optional[Any]:
        # _loop0_143: lambda_param_maybe_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_maybe_default := self.lambda_param_maybe_default())
        ):
            children.append(lambda_param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_144(self) -> Optional[Any]:
        # _loop1_144: lambda_param_maybe_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_maybe_default := self.lambda_param_maybe_default())
        ):
            children.append(lambda_param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_145(self) -> Optional[Any]:
        # _tmp_145: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_146(self) -> Optional[Any]:
        # _loop0_146: fstring_format_spec
        mark = self._mark()
        children = []
        while (
            (fstring_format_spec := self.fstring_format_spec())
        ):
            children.append(fstring_format_spec)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_147(self) -> Optional[Any]:
        # _loop0_147: fstring_mid
        mark = self._mark()
        children = []
        while (
            (fstring_mid := self.fstring_mid())
        ):
            children.append(fstring_mid)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_148(self) -> Optional[Any]:
        # _loop1_148: (fstring | STRING)
        mark = self._mark()
        children = []
        while (
            (_tmp_295 := self._tmp_295())
        ):
            children.append(_tmp_295)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_149(self) -> Optional[Any]:
        # _tmp_149: star_named_expression ',' star_named_expressions?
        mark = self._mark()
        if (
            (y := self.star_named_expression())
            and
            (self.expect(','))
            and
            (z := self.star_named_expressions(),)
        ):
            return [y] + ( z or [] );
        self._reset(mark)
        return None;

    @memoize
    def _loop0_151(self) -> Optional[Any]:
        # _loop0_151: ',' double_starred_kvpair
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.double_starred_kvpair())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_150(self) -> Optional[Any]:
        # _gather_150: double_starred_kvpair _loop0_151
        mark = self._mark()
        if (
            (elem := self.double_starred_kvpair())
            is not None
            and
            (seq := self._loop0_151())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_152(self) -> Optional[Any]:
        # _loop1_152: for_if_clause
        mark = self._mark()
        children = []
        while (
            (for_if_clause := self.for_if_clause())
        ):
            children.append(for_if_clause)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_153(self) -> Optional[Any]:
        # _loop0_153: ('if' disjunction)
        mark = self._mark()
        children = []
        while (
            (_tmp_296 := self._tmp_296())
        ):
            children.append(_tmp_296)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_154(self) -> Optional[Any]:
        # _loop0_154: ('if' disjunction)
        mark = self._mark()
        children = []
        while (
            (_tmp_297 := self._tmp_297())
        ):
            children.append(_tmp_297)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_155(self) -> Optional[Any]:
        # _tmp_155: assignment_expression | expression !':='
        mark = self._mark()
        if (
            (assignment_expression := self.assignment_expression())
        ):
            return assignment_expression;
        self._reset(mark)
        if (
            (expression := self.expression())
            and
            (self.negative_lookahead(self.expect, ':='))
        ):
            return expression;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_157(self) -> Optional[Any]:
        # _loop0_157: ',' (starred_expression | (assignment_expression | expression !':=') !'=')
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self._tmp_298())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_156(self) -> Optional[Any]:
        # _gather_156: (starred_expression | (assignment_expression | expression !':=') !'=') _loop0_157
        mark = self._mark()
        if (
            (elem := self._tmp_298())
            is not None
            and
            (seq := self._loop0_157())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_158(self) -> Optional[Any]:
        # _tmp_158: ',' kwargs
        mark = self._mark()
        if (
            (self.expect(','))
            and
            (k := self.kwargs())
        ):
            return k;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_160(self) -> Optional[Any]:
        # _loop0_160: ',' kwarg_or_starred
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.kwarg_or_starred())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_159(self) -> Optional[Any]:
        # _gather_159: kwarg_or_starred _loop0_160
        mark = self._mark()
        if (
            (elem := self.kwarg_or_starred())
            is not None
            and
            (seq := self._loop0_160())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_162(self) -> Optional[Any]:
        # _loop0_162: ',' kwarg_or_double_starred
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.kwarg_or_double_starred())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_161(self) -> Optional[Any]:
        # _gather_161: kwarg_or_double_starred _loop0_162
        mark = self._mark()
        if (
            (elem := self.kwarg_or_double_starred())
            is not None
            and
            (seq := self._loop0_162())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_164(self) -> Optional[Any]:
        # _loop0_164: ',' kwarg_or_starred
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.kwarg_or_starred())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_163(self) -> Optional[Any]:
        # _gather_163: kwarg_or_starred _loop0_164
        mark = self._mark()
        if (
            (elem := self.kwarg_or_starred())
            is not None
            and
            (seq := self._loop0_164())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_166(self) -> Optional[Any]:
        # _loop0_166: ',' kwarg_or_double_starred
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.kwarg_or_double_starred())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_165(self) -> Optional[Any]:
        # _gather_165: kwarg_or_double_starred _loop0_166
        mark = self._mark()
        if (
            (elem := self.kwarg_or_double_starred())
            is not None
            and
            (seq := self._loop0_166())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_167(self) -> Optional[Any]:
        # _loop0_167: (',' star_target)
        mark = self._mark()
        children = []
        while (
            (_tmp_299 := self._tmp_299())
        ):
            children.append(_tmp_299)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_169(self) -> Optional[Any]:
        # _loop0_169: ',' star_target
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.star_target())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_168(self) -> Optional[Any]:
        # _gather_168: star_target _loop0_169
        mark = self._mark()
        if (
            (elem := self.star_target())
            is not None
            and
            (seq := self._loop0_169())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_170(self) -> Optional[Any]:
        # _loop1_170: (',' star_target)
        mark = self._mark()
        children = []
        while (
            (_tmp_300 := self._tmp_300())
        ):
            children.append(_tmp_300)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_171(self) -> Optional[Any]:
        # _tmp_171: !'*' star_target
        mark = self._mark()
        if (
            (self.negative_lookahead(self.expect, '*'))
            and
            (star_target := self.star_target())
        ):
            return star_target;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_173(self) -> Optional[Any]:
        # _loop0_173: ',' del_target
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.del_target())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_172(self) -> Optional[Any]:
        # _gather_172: del_target _loop0_173
        mark = self._mark()
        if (
            (elem := self.del_target())
            is not None
            and
            (seq := self._loop0_173())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_175(self) -> Optional[Any]:
        # _loop0_175: ',' expression
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_174(self) -> Optional[Any]:
        # _gather_174: expression _loop0_175
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_175())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_177(self) -> Optional[Any]:
        # _loop0_177: ',' expression
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_176(self) -> Optional[Any]:
        # _gather_176: expression _loop0_177
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_177())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_179(self) -> Optional[Any]:
        # _loop0_179: ',' expression
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_178(self) -> Optional[Any]:
        # _gather_178: expression _loop0_179
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_179())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_181(self) -> Optional[Any]:
        # _loop0_181: ',' expression
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_180(self) -> Optional[Any]:
        # _gather_180: expression _loop0_181
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_181())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_182(self) -> Optional[Any]:
        # _tmp_182: NEWLINE INDENT
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
        ):
            return [_newline, _indent];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_183(self) -> Optional[Any]:
        # _tmp_183: args | expression for_if_clauses
        mark = self._mark()
        if (
            (args := self.args())
        ):
            return args;
        self._reset(mark)
        if (
            (expression := self.expression())
            and
            (for_if_clauses := self.for_if_clauses())
        ):
            return [expression, for_if_clauses];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_184(self) -> Optional[Any]:
        # _tmp_184: args ','
        mark = self._mark()
        if (
            (args := self.args())
            and
            (literal := self.expect(','))
        ):
            return [args, literal];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_185(self) -> Optional[Any]:
        # _tmp_185: ',' | ')'
        mark = self._mark()
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(')'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_186(self) -> Optional[Any]:
        # _tmp_186: 'True' | 'False' | 'None'
        mark = self._mark()
        if (
            (literal := self.expect('True'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('False'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('None'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_187(self) -> Optional[Any]:
        # _tmp_187: NAME '='
        mark = self._mark()
        if (
            (name := self.name())
            and
            (literal := self.expect('='))
        ):
            return [name, literal];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_188(self) -> Optional[Any]:
        # _tmp_188: NAME STRING | SOFT_KEYWORD
        mark = self._mark()
        if (
            (name := self.name())
            and
            (string := self.string())
        ):
            return [name, string];
        self._reset(mark)
        if (
            (soft_keyword := self.soft_keyword())
        ):
            return soft_keyword;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_189(self) -> Optional[Any]:
        # _tmp_189: 'else' | ':'
        mark = self._mark()
        if (
            (literal := self.expect('else'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(':'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_190(self) -> Optional[Any]:
        # _tmp_190: FSTRING_MIDDLE | fstring_replacement_field
        mark = self._mark()
        if (
            (fstring_middle := self.fstring_middle())
        ):
            return fstring_middle;
        self._reset(mark)
        if (
            (fstring_replacement_field := self.fstring_replacement_field())
        ):
            return fstring_replacement_field;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_191(self) -> Optional[Any]:
        # _tmp_191: '=' | ':='
        mark = self._mark()
        if (
            (literal := self.expect('='))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(':='))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_192(self) -> Optional[Any]:
        # _tmp_192: list | tuple | genexp | 'True' | 'None' | 'False'
        mark = self._mark()
        if (
            (list := self.list())
        ):
            return list;
        self._reset(mark)
        if (
            (tuple := self.tuple())
        ):
            return tuple;
        self._reset(mark)
        if (
            (genexp := self.genexp())
        ):
            return genexp;
        self._reset(mark)
        if (
            (literal := self.expect('True'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('None'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('False'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_193(self) -> Optional[Any]:
        # _tmp_193: '=' | ':='
        mark = self._mark()
        if (
            (literal := self.expect('='))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(':='))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_194(self) -> Optional[Any]:
        # _loop0_194: star_named_expressions
        mark = self._mark()
        children = []
        while (
            (star_named_expressions := self.star_named_expressions())
        ):
            children.append(star_named_expressions)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_195(self) -> Optional[Any]:
        # _loop0_195: (star_targets '=')
        mark = self._mark()
        children = []
        while (
            (_tmp_301 := self._tmp_301())
        ):
            children.append(_tmp_301)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_196(self) -> Optional[Any]:
        # _loop0_196: (star_targets '=')
        mark = self._mark()
        children = []
        while (
            (_tmp_302 := self._tmp_302())
        ):
            children.append(_tmp_302)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_197(self) -> Optional[Any]:
        # _tmp_197: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_198(self) -> Optional[Any]:
        # _tmp_198: '[' | '(' | '{'
        mark = self._mark()
        if (
            (literal := self.expect('['))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('('))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('{'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_199(self) -> Optional[Any]:
        # _tmp_199: '[' | '{'
        mark = self._mark()
        if (
            (literal := self.expect('['))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('{'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_200(self) -> Optional[Any]:
        # _tmp_200: '[' | '{'
        mark = self._mark()
        if (
            (literal := self.expect('['))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('{'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_201(self) -> Optional[Any]:
        # _tmp_201: slash_no_default | slash_with_default
        mark = self._mark()
        if (
            (slash_no_default := self.slash_no_default())
        ):
            return slash_no_default;
        self._reset(mark)
        if (
            (slash_with_default := self.slash_with_default())
        ):
            return slash_with_default;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_202(self) -> Optional[Any]:
        # _loop0_202: param_maybe_default
        mark = self._mark()
        children = []
        while (
            (param_maybe_default := self.param_maybe_default())
        ):
            children.append(param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_203(self) -> Optional[Any]:
        # _loop0_203: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_204(self) -> Optional[Any]:
        # _loop0_204: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_205(self) -> Optional[Any]:
        # _loop1_205: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_206(self) -> Optional[Any]:
        # _tmp_206: slash_no_default | slash_with_default
        mark = self._mark()
        if (
            (slash_no_default := self.slash_no_default())
        ):
            return slash_no_default;
        self._reset(mark)
        if (
            (slash_with_default := self.slash_with_default())
        ):
            return slash_with_default;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_207(self) -> Optional[Any]:
        # _loop0_207: param_maybe_default
        mark = self._mark()
        children = []
        while (
            (param_maybe_default := self.param_maybe_default())
        ):
            children.append(param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_208(self) -> Optional[Any]:
        # _tmp_208: ',' | param_no_default
        mark = self._mark()
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        if (
            (param_no_default := self.param_no_default())
        ):
            return param_no_default;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_209(self) -> Optional[Any]:
        # _loop0_209: param_maybe_default
        mark = self._mark()
        children = []
        while (
            (param_maybe_default := self.param_maybe_default())
        ):
            children.append(param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_210(self) -> Optional[Any]:
        # _loop1_210: param_maybe_default
        mark = self._mark()
        children = []
        while (
            (param_maybe_default := self.param_maybe_default())
        ):
            children.append(param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_211(self) -> Optional[Any]:
        # _tmp_211: ')' | ','
        mark = self._mark()
        if (
            (literal := self.expect(')'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_212(self) -> Optional[Any]:
        # _tmp_212: ')' | ',' (')' | '**')
        mark = self._mark()
        if (
            (literal := self.expect(')'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(','))
            and
            (_tmp_303 := self._tmp_303())
        ):
            return [literal, _tmp_303];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_213(self) -> Optional[Any]:
        # _tmp_213: param_no_default | ','
        mark = self._mark()
        if (
            (param_no_default := self.param_no_default())
        ):
            return param_no_default;
        self._reset(mark)
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_214(self) -> Optional[Any]:
        # _loop0_214: param_maybe_default
        mark = self._mark()
        children = []
        while (
            (param_maybe_default := self.param_maybe_default())
        ):
            children.append(param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_215(self) -> Optional[Any]:
        # _tmp_215: param_no_default | ','
        mark = self._mark()
        if (
            (param_no_default := self.param_no_default())
        ):
            return param_no_default;
        self._reset(mark)
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_216(self) -> Optional[Any]:
        # _tmp_216: '*' | '**' | '/'
        mark = self._mark()
        if (
            (literal := self.expect('*'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('**'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('/'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_217(self) -> Optional[Any]:
        # _loop1_217: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_218(self) -> Optional[Any]:
        # _tmp_218: lambda_slash_no_default | lambda_slash_with_default
        mark = self._mark()
        if (
            (lambda_slash_no_default := self.lambda_slash_no_default())
        ):
            return lambda_slash_no_default;
        self._reset(mark)
        if (
            (lambda_slash_with_default := self.lambda_slash_with_default())
        ):
            return lambda_slash_with_default;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_219(self) -> Optional[Any]:
        # _loop0_219: lambda_param_maybe_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_maybe_default := self.lambda_param_maybe_default())
        ):
            children.append(lambda_param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_220(self) -> Optional[Any]:
        # _loop0_220: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_221(self) -> Optional[Any]:
        # _loop0_221: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_223(self) -> Optional[Any]:
        # _loop0_223: ',' lambda_param
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.lambda_param())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_222(self) -> Optional[Any]:
        # _gather_222: lambda_param _loop0_223
        mark = self._mark()
        if (
            (elem := self.lambda_param())
            is not None
            and
            (seq := self._loop0_223())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_224(self) -> Optional[Any]:
        # _tmp_224: lambda_slash_no_default | lambda_slash_with_default
        mark = self._mark()
        if (
            (lambda_slash_no_default := self.lambda_slash_no_default())
        ):
            return lambda_slash_no_default;
        self._reset(mark)
        if (
            (lambda_slash_with_default := self.lambda_slash_with_default())
        ):
            return lambda_slash_with_default;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_225(self) -> Optional[Any]:
        # _loop0_225: lambda_param_maybe_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_maybe_default := self.lambda_param_maybe_default())
        ):
            children.append(lambda_param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_226(self) -> Optional[Any]:
        # _tmp_226: ',' | lambda_param_no_default
        mark = self._mark()
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        if (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            return lambda_param_no_default;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_227(self) -> Optional[Any]:
        # _loop0_227: lambda_param_maybe_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_maybe_default := self.lambda_param_maybe_default())
        ):
            children.append(lambda_param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_228(self) -> Optional[Any]:
        # _loop1_228: lambda_param_maybe_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_maybe_default := self.lambda_param_maybe_default())
        ):
            children.append(lambda_param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_229(self) -> Optional[Any]:
        # _loop1_229: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_230(self) -> Optional[Any]:
        # _tmp_230: ':' | ',' (':' | '**')
        mark = self._mark()
        if (
            (literal := self.expect(':'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(','))
            and
            (_tmp_304 := self._tmp_304())
        ):
            return [literal, _tmp_304];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_231(self) -> Optional[Any]:
        # _tmp_231: lambda_param_no_default | ','
        mark = self._mark()
        if (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            return lambda_param_no_default;
        self._reset(mark)
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_232(self) -> Optional[Any]:
        # _loop0_232: lambda_param_maybe_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_maybe_default := self.lambda_param_maybe_default())
        ):
            children.append(lambda_param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_233(self) -> Optional[Any]:
        # _tmp_233: lambda_param_no_default | ','
        mark = self._mark()
        if (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            return lambda_param_no_default;
        self._reset(mark)
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_234(self) -> Optional[Any]:
        # _tmp_234: '*' | '**' | '/'
        mark = self._mark()
        if (
            (literal := self.expect('*'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('**'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('/'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_235(self) -> Optional[Any]:
        # _tmp_235: ',' | ')' | ':'
        mark = self._mark()
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(')'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(':'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_237(self) -> Optional[Any]:
        # _loop0_237: ',' dotted_name
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.dotted_name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_236(self) -> Optional[Any]:
        # _gather_236: dotted_name _loop0_237
        mark = self._mark()
        if (
            (elem := self.dotted_name())
            is not None
            and
            (seq := self._loop0_237())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_239(self) -> Optional[Any]:
        # _loop0_239: ',' (expression ['as' star_target])
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self._tmp_305())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_238(self) -> Optional[Any]:
        # _gather_238: (expression ['as' star_target]) _loop0_239
        mark = self._mark()
        if (
            (elem := self._tmp_305())
            is not None
            and
            (seq := self._loop0_239())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_241(self) -> Optional[Any]:
        # _loop0_241: ',' (expressions ['as' star_target])
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self._tmp_306())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_240(self) -> Optional[Any]:
        # _gather_240: (expressions ['as' star_target]) _loop0_241
        mark = self._mark()
        if (
            (elem := self._tmp_306())
            is not None
            and
            (seq := self._loop0_241())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_243(self) -> Optional[Any]:
        # _loop0_243: ',' (expression ['as' star_target])
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self._tmp_307())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_242(self) -> Optional[Any]:
        # _gather_242: (expression ['as' star_target]) _loop0_243
        mark = self._mark()
        if (
            (elem := self._tmp_307())
            is not None
            and
            (seq := self._loop0_243())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_245(self) -> Optional[Any]:
        # _loop0_245: ',' (expressions ['as' star_target])
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self._tmp_308())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_244(self) -> Optional[Any]:
        # _gather_244: (expressions ['as' star_target]) _loop0_245
        mark = self._mark()
        if (
            (elem := self._tmp_308())
            is not None
            and
            (seq := self._loop0_245())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_246(self) -> Optional[Any]:
        # _tmp_246: 'except' | 'finally'
        mark = self._mark()
        if (
            (literal := self.expect('except'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('finally'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_247(self) -> Optional[Any]:
        # _loop0_247: block
        mark = self._mark()
        children = []
        while (
            (block := self.block())
        ):
            children.append(block)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_248(self) -> Optional[Any]:
        # _loop1_248: except_block
        mark = self._mark()
        children = []
        while (
            (except_block := self.except_block())
        ):
            children.append(except_block)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_249(self) -> Optional[Any]:
        # _tmp_249: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (name := self.name())
        ):
            return [literal, name];
        self._reset(mark)
        return None;

    @memoize
    def _loop0_250(self) -> Optional[Any]:
        # _loop0_250: block
        mark = self._mark()
        children = []
        while (
            (block := self.block())
        ):
            children.append(block)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop1_251(self) -> Optional[Any]:
        # _loop1_251: except_star_block
        mark = self._mark()
        children = []
        while (
            (except_star_block := self.except_star_block())
        ):
            children.append(except_star_block)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_252(self) -> Optional[Any]:
        # _tmp_252: expression ['as' NAME]
        mark = self._mark()
        if (
            (expression := self.expression())
            and
            (opt := self._tmp_309(),)
        ):
            return [expression, opt];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_253(self) -> Optional[Any]:
        # _tmp_253: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (name := self.name())
        ):
            return [literal, name];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_254(self) -> Optional[Any]:
        # _tmp_254: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (name := self.name())
        ):
            return [literal, name];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_255(self) -> Optional[Any]:
        # _tmp_255: NEWLINE | ':'
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
        ):
            return _newline;
        self._reset(mark)
        if (
            (literal := self.expect(':'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_256(self) -> Optional[Any]:
        # _tmp_256: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (name := self.name())
        ):
            return [literal, name];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_257(self) -> Optional[Any]:
        # _tmp_257: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (name := self.name())
        ):
            return [literal, name];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_258(self) -> Optional[Any]:
        # _tmp_258: positional_patterns ','
        mark = self._mark()
        if (
            (positional_patterns := self.positional_patterns())
            and
            (literal := self.expect(','))
        ):
            return [positional_patterns, literal];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_259(self) -> Optional[Any]:
        # _tmp_259: '->' expression
        mark = self._mark()
        if (
            (literal := self.expect('->'))
            and
            (expression := self.expression())
        ):
            return [literal, expression];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_260(self) -> Optional[Any]:
        # _tmp_260: '(' arguments? ')'
        mark = self._mark()
        if (
            (literal := self.expect('('))
            and
            (opt := self.arguments(),)
            and
            (literal_1 := self.expect(')'))
        ):
            return [literal, opt, literal_1];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_261(self) -> Optional[Any]:
        # _tmp_261: '(' arguments? ')'
        mark = self._mark()
        if (
            (literal := self.expect('('))
            and
            (opt := self.arguments(),)
            and
            (literal_1 := self.expect(')'))
        ):
            return [literal, opt, literal_1];
        self._reset(mark)
        return None;

    @memoize
    def _loop0_263(self) -> Optional[Any]:
        # _loop0_263: ',' double_starred_kvpair
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.double_starred_kvpair())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_262(self) -> Optional[Any]:
        # _gather_262: double_starred_kvpair _loop0_263
        mark = self._mark()
        if (
            (elem := self.double_starred_kvpair())
            is not None
            and
            (seq := self._loop0_263())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_264(self) -> Optional[Any]:
        # _tmp_264: '}' | ','
        mark = self._mark()
        if (
            (literal := self.expect('}'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_265(self) -> Optional[Any]:
        # _tmp_265: '}' | ','
        mark = self._mark()
        if (
            (literal := self.expect('}'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(','))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_266(self) -> Optional[Any]:
        # _tmp_266: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_267(self) -> Optional[Any]:
        # _tmp_267: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_268(self) -> Optional[Any]:
        # _tmp_268: '=' | '!' | ':' | '}'
        mark = self._mark()
        if (
            (literal := self.expect('='))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('!'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(':'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('}'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_269(self) -> Optional[Any]:
        # _tmp_269: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_270(self) -> Optional[Any]:
        # _tmp_270: '!' | ':' | '}'
        mark = self._mark()
        if (
            (literal := self.expect('!'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect(':'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('}'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_271(self) -> Optional[Any]:
        # _tmp_271: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_272(self) -> Optional[Any]:
        # _tmp_272: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_273(self) -> Optional[Any]:
        # _tmp_273: '!' NAME
        mark = self._mark()
        if (
            (literal := self.expect('!'))
            and
            (name := self.name())
        ):
            return [literal, name];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_274(self) -> Optional[Any]:
        # _tmp_274: ':' | '}'
        mark = self._mark()
        if (
            (literal := self.expect(':'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('}'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_275(self) -> Optional[Any]:
        # _tmp_275: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_276(self) -> Optional[Any]:
        # _tmp_276: '!' NAME
        mark = self._mark()
        if (
            (literal := self.expect('!'))
            and
            (name := self.name())
        ):
            return [literal, name];
        self._reset(mark)
        return None;

    @memoize
    def _loop0_277(self) -> Optional[Any]:
        # _loop0_277: fstring_format_spec
        mark = self._mark()
        children = []
        while (
            (fstring_format_spec := self.fstring_format_spec())
        ):
            children.append(fstring_format_spec)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _tmp_278(self) -> Optional[Any]:
        # _tmp_278: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr;
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_279(self) -> Optional[Any]:
        # _tmp_279: '!' NAME
        mark = self._mark()
        if (
            (literal := self.expect('!'))
            and
            (name := self.name())
        ):
            return [literal, name];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_280(self) -> Optional[Any]:
        # _tmp_280: ':' | '}'
        mark = self._mark()
        if (
            (literal := self.expect(':'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('}'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_282(self) -> Optional[Any]:
        # _loop0_282: ',' pragma_arg
        mark = self._mark()
        children = []
        while (
            (self.expect(','))
            and
            (elem := self.pragma_arg())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_281(self) -> Optional[Any]:
        # _gather_281: pragma_arg _loop0_282
        mark = self._mark()
        if (
            (elem := self.pragma_arg())
            is not None
            and
            (seq := self._loop0_282())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_284(self) -> Optional[Any]:
        # _loop0_284: '.' NAME
        mark = self._mark()
        children = []
        while (
            (self.expect('.'))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_283(self) -> Optional[Any]:
        # _gather_283: NAME _loop0_284
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_284())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_286(self) -> Optional[Any]:
        # _loop0_286: '.' NAME
        mark = self._mark()
        children = []
        while (
            (self.expect('.'))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_285(self) -> Optional[Any]:
        # _gather_285: NAME _loop0_286
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_286())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_287(self) -> Optional[Any]:
        # _tmp_287: star_targets '='
        mark = self._mark()
        if (
            (z := self.star_targets())
            and
            (self.expect('='))
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_288(self) -> Optional[Any]:
        # _tmp_288: '.' | '...'
        mark = self._mark()
        if (
            (literal := self.expect('.'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('...'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_289(self) -> Optional[Any]:
        # _tmp_289: '.' | '...'
        mark = self._mark()
        if (
            (literal := self.expect('.'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('...'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_290(self) -> Optional[Any]:
        # _tmp_290: ',' expression
        mark = self._mark()
        if (
            (self.expect(','))
            and
            (c := self.expression())
        ):
            return c;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_291(self) -> Optional[Any]:
        # _tmp_291: ',' star_expression
        mark = self._mark()
        if (
            (self.expect(','))
            and
            (c := self.star_expression())
        ):
            return c;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_292(self) -> Optional[Any]:
        # _tmp_292: 'or' conjunction
        mark = self._mark()
        if (
            (self.expect('or'))
            and
            (c := self.conjunction())
        ):
            return c;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_293(self) -> Optional[Any]:
        # _tmp_293: 'and' inversion
        mark = self._mark()
        if (
            (self.expect('and'))
            and
            (c := self.inversion())
        ):
            return c;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_294(self) -> Optional[Any]:
        # _tmp_294: slice | starred_expression
        mark = self._mark()
        if (
            (slice := self.slice())
        ):
            return slice;
        self._reset(mark)
        if (
            (starred_expression := self.starred_expression())
        ):
            return starred_expression;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_295(self) -> Optional[Any]:
        # _tmp_295: fstring | STRING
        mark = self._mark()
        if (
            (fstring := self.fstring())
        ):
            return fstring;
        self._reset(mark)
        if (
            (string := self.string())
        ):
            return string;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_296(self) -> Optional[Any]:
        # _tmp_296: 'if' disjunction
        mark = self._mark()
        if (
            (self.expect('if'))
            and
            (z := self.disjunction())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_297(self) -> Optional[Any]:
        # _tmp_297: 'if' disjunction
        mark = self._mark()
        if (
            (self.expect('if'))
            and
            (z := self.disjunction())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_298(self) -> Optional[Any]:
        # _tmp_298: starred_expression | (assignment_expression | expression !':=') !'='
        mark = self._mark()
        if (
            (starred_expression := self.starred_expression())
        ):
            return starred_expression;
        self._reset(mark)
        if (
            (_tmp_310 := self._tmp_310())
            and
            (self.negative_lookahead(self.expect, '='))
        ):
            return _tmp_310;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_299(self) -> Optional[Any]:
        # _tmp_299: ',' star_target
        mark = self._mark()
        if (
            (self.expect(','))
            and
            (c := self.star_target())
        ):
            return c;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_300(self) -> Optional[Any]:
        # _tmp_300: ',' star_target
        mark = self._mark()
        if (
            (self.expect(','))
            and
            (c := self.star_target())
        ):
            return c;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_301(self) -> Optional[Any]:
        # _tmp_301: star_targets '='
        mark = self._mark()
        if (
            (star_targets := self.star_targets())
            and
            (literal := self.expect('='))
        ):
            return [star_targets, literal];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_302(self) -> Optional[Any]:
        # _tmp_302: star_targets '='
        mark = self._mark()
        if (
            (star_targets := self.star_targets())
            and
            (literal := self.expect('='))
        ):
            return [star_targets, literal];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_303(self) -> Optional[Any]:
        # _tmp_303: ')' | '**'
        mark = self._mark()
        if (
            (literal := self.expect(')'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('**'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_304(self) -> Optional[Any]:
        # _tmp_304: ':' | '**'
        mark = self._mark()
        if (
            (literal := self.expect(':'))
        ):
            return literal;
        self._reset(mark)
        if (
            (literal := self.expect('**'))
        ):
            return literal;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_305(self) -> Optional[Any]:
        # _tmp_305: expression ['as' star_target]
        mark = self._mark()
        if (
            (expression := self.expression())
            and
            (opt := self._tmp_311(),)
        ):
            return [expression, opt];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_306(self) -> Optional[Any]:
        # _tmp_306: expressions ['as' star_target]
        mark = self._mark()
        if (
            (expressions := self.expressions())
            and
            (opt := self._tmp_312(),)
        ):
            return [expressions, opt];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_307(self) -> Optional[Any]:
        # _tmp_307: expression ['as' star_target]
        mark = self._mark()
        if (
            (expression := self.expression())
            and
            (opt := self._tmp_313(),)
        ):
            return [expression, opt];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_308(self) -> Optional[Any]:
        # _tmp_308: expressions ['as' star_target]
        mark = self._mark()
        if (
            (expressions := self.expressions())
            and
            (opt := self._tmp_314(),)
        ):
            return [expressions, opt];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_309(self) -> Optional[Any]:
        # _tmp_309: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (name := self.name())
        ):
            return [literal, name];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_310(self) -> Optional[Any]:
        # _tmp_310: assignment_expression | expression !':='
        mark = self._mark()
        if (
            (assignment_expression := self.assignment_expression())
        ):
            return assignment_expression;
        self._reset(mark)
        if (
            (expression := self.expression())
            and
            (self.negative_lookahead(self.expect, ':='))
        ):
            return expression;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_311(self) -> Optional[Any]:
        # _tmp_311: 'as' star_target
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (star_target := self.star_target())
        ):
            return [literal, star_target];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_312(self) -> Optional[Any]:
        # _tmp_312: 'as' star_target
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (star_target := self.star_target())
        ):
            return [literal, star_target];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_313(self) -> Optional[Any]:
        # _tmp_313: 'as' star_target
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (star_target := self.star_target())
        ):
            return [literal, star_target];
        self._reset(mark)
        return None;

    @memoize
    def _tmp_314(self) -> Optional[Any]:
        # _tmp_314: 'as' star_target
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (star_target := self.star_target())
        ):
            return [literal, star_target];
        self._reset(mark)
        return None;

    KEYWORDS = ('False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield')
    SOFT_KEYWORDS = ('_', 'alias', 'attr', 'case', 'const', 'enamldef', 'event', 'func', 'match', 'pragma', 'template', 'type')


if __name__ == '__main__':
    from pegen.parser import simple_parser_main
    simple_parser_main(EnamlParser)
