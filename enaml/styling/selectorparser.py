#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os

import ply.lex as lex
import ply.yacc as yacc


# Get a save directory for the lex and parse tables
_lex_dir = os.path.join(os.path.dirname(__file__), 'parse_tab')
_lex_mod = 'enaml.styling.parse_tab.lextab'
_parse_mod = 'enaml.styling.parse_tab.parsetab'


class SelectorSyntaxError(Exception):
    pass


#------------------------------------------------------------------------------
# Lexer
#------------------------------------------------------------------------------
tokens = (
    'COLON',
    'COMMA',
    'DOUBLE_COLON',
    'DOT',
    'EQUAL',
    'GREATER',
    'HASH',
    'IDENT',
    'LSQB',
    'NOT',
    'RPAR',
    'RSQB',
    'STAR',
    'STRING',
    'WS',

    # string token sentinels
    'STRING_START_SINGLE',
    'STRING_CONTINUE',
    'STRING_END',
)


states = (
    ('SINGLEQ1', 'exclusive'),
    ('SINGLEQ2', 'exclusive'),
)


t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'
t_DOUBLE_COLON = r'::'
t_EQUAL = r'='
t_GREATER = r'\>'
t_HASH = r'\#'
t_IDENT = r'-?[a-zA-Z_][a-zA-Z0-9_-]*'
t_LSQB = r'\['
t_NOT = r':not\('
t_RPAR = r'\)'
t_RSQB = r'\]'
t_STAR = r'\*'
t_WS = r'[ \t\r\n\f]+'


def t_start_single_quoted_q1_string(t):
    r"'"
    t.lexer.push_state("SINGLEQ1")
    t.type = "STRING_START_SINGLE"
    return t


def t_SINGLEQ1_simple(t):
    r"[^'\\\n]+"
    t.type = "STRING_CONTINUE"
    return t


def t_SINGLEQ1_end(t):
    r"'"
    t.type = "STRING_END"
    t.lexer.pop_state()
    return t


# supress PLY warning
t_SINGLEQ1_ignore = ''


def t_SINGLEQ1_error(t):
    raise SelectorSyntaxError('EOL while scanning single quoted string')


def t_start_single_quoted_q2_string(t):
    r'"'
    t.lexer.push_state("SINGLEQ2")
    t.type = "STRING_START_SINGLE"
    return t


def t_SINGLEQ2_simple(t):
    r'[^"\\\n]+'
    t.type = "STRING_CONTINUE"
    return t


def t_SINGLEQ2_end(t):
    r'"'
    t.type = "STRING_END"
    t.lexer.pop_state()
    return t


# supress PLY warning
t_SINGLEQ2_ignore = ''


def t_SINGLEQ2_error(t):
    raise SelectorSyntaxError('EOL while scanning single quoted string')


def t_error(t):
    raise SelectorSyntaxError('invalid syntax')


def collect_strings(token_stream):
    for tok in token_stream:
        if not tok.type.startswith("STRING_START_"):
            yield tok
            continue
        start_tok = tok
        string_toks = []
        for tok in token_stream:
            if tok.type == "STRING_END":
                break
            else:
                assert tok.type == "STRING_CONTINUE", tok.type
                string_toks.append(tok)
        else:
            msg = 'EOF while scanning single quoted string'
            raise SelectorSyntaxError(msg)
        s = "".join(tok.value for tok in string_toks)
        s = s.decode("string_escape")
        start_tok.type = "STRING"
        start_tok.value = s
        yield start_tok


class SelectorLexer(object):

    def __init__(self):
        self.lexer = lex.lex(outputdir=_lex_dir, lextab=_lex_mod, optimize=1)
        self.token_stream = None

    def input(self, txt):
        self.lexer.input(txt)
        self.token_stream = collect_strings(iter(self.lexer.token, None))

    def token(self):
        try:
            return self.token_stream.next()
        except StopIteration:
            pass


#------------------------------------------------------------------------------
# Lexer
#------------------------------------------------------------------------------
def p_selectors_group1(p):
    ''' selectors_group : selector '''


def p_selectors_group2(p):
    ''' selectors_group : selector COMMA selector '''


def p_selectors_group3(p):
    ''' selectors_group : selector COMMA WS selector '''


def p_selector1(p):
    ''' selector : simple_selector_seq '''


def p_selector2(p):
    ''' selector : simple_selector_seq combinator_list '''


def p_combinator_list1(p):
    ''' combinator_list : combinator simple_selector_seq '''


def p_combinator_list2(p):
    ''' combinator_list : combinator simple_selector_seq combinator_list '''


def p_combinator1(p):
    ''' combinator : greater_opt '''


def p_combinator2(p):
    ''' combinator : WS '''


def p_greater_opt1(p):
    ''' greater_opt : GREATER '''


def p_greater_opt2(p):
    ''' greater_opt : GREATER WS '''


def p_greater_opt3(p):
    ''' greater_opt : WS GREATER '''


def p_greater_opt4(p):
    ''' greater_opt : WS GREATER WS '''


def p_simple_selector_seq1(p):
    ''' simple_selector_seq : type_selector '''


def p_simple_selector_seq2(p):
    ''' simple_selector_seq : universal '''


def p_simple_selector_seq3(p):
    ''' simple_selector_seq : type_selector secondary_list '''


def p_simple_selector_seq4(p):
    ''' simple_selector_seq : universal secondary_list '''


def p_simple_selector_seq5(p):
    ''' simple_selector_seq : secondary_list '''


def p_type_selector(p):
    ''' type_selector : IDENT '''


def p_universal(p):
    ''' universal : STAR '''


def p_secondary_list1(p):
    ''' secondary_list : secondary_item '''


def p_secondary_list2(p):
    ''' secondary_list : secondary_item secondary_list '''


def p_secondary_item(p):
    ''' secondary_item : hash
                       | class
                       | pseudo
                       | negation '''


def p_hash(p):
    ''' hash : HASH IDENT '''


def p_class(p):
    ''' class : DOT IDENT '''


def p_pseudo1(p):
    ''' pseudo : COLON IDENT '''


def p_pseudo2(p):
    ''' pseudo : DOUBLE_COLON IDENT '''


def p_negation(p):
    ''' negation : NOT negation_arg_opt RPAR '''


def p_negation_arg_opt1(p):
    ''' negation_arg_opt : negation_arg '''


def p_negation_arg_opt2(p):
    ''' negation_arg_opt : negation_arg WS '''


def p_negation_arg_opt3(p):
    ''' negation_arg_opt : WS negation_arg '''


def p_negation_arg_opt4(p):
    ''' negation_arg_opt : WS negation_arg WS '''


def p_negation_arg(p):
    ''' negation_arg : type_selector
                     | universal
                     | hash
                     | class
                     | pseudo '''


def p_error(p):
    raise SelectorSyntaxError('invalid syntax')


_parser = yacc.yacc(
    debug=0, outputdir=_lex_dir, tabmodule=_parse_mod, optimize=1,
    errorlog=yacc.NullLogger(),
)


def parse_selector(selector):
    try:
        r = _parser.parse(selector.strip(), debug=0, lexer=SelectorLexer())
        return r
    except SelectorSyntaxError:
        print 'invalid selector: %s' % selector
