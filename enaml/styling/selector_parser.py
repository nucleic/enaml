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
_lex_module = 'enaml.styling.parse_tab.lextab'


class SelectorLexer(object):

    tokens = (
        'BANG',
        'COLON',
        'COMMA',
        'DOUBLE_COLON',
        'DOT',
        'ENDMARKER',
        'EQUAL',
        'GREATER',
        'HASH',
        'LSQB',
        'NAME',
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

    t_BANG = r'!'
    t_COLON = r':'
    t_COMMA = r','
    t_DOT = r'\.'
    t_DOUBLE_COLON = r'::'
    t_EQUAL = r'='
    t_GREATER = r'\>'
    t_HASH = r'\#'
    t_LSQB = r'\['
    t_NAME = r'[a-zA-Z_][a-zA-Z0-9_-]*'
    t_RSQB = r'\]'
    t_STAR = r'\*'
    t_WS = r'[ \t\r\n\f]+'

    def t_start_single_quoted_q1_string(self, t):
        r"'"
        t.lexer.push_state("SINGLEQ1")
        t.type = "STRING_START_SINGLE"
        return t

    def t_SINGLEQ1_simple(self, t):
        r"[^'\\\n]+"
        t.type = "STRING_CONTINUE"
        return t

    def t_SINGLEQ1_end(self, t):
        r"'"
        t.type = "STRING_END"
        t.lexer.pop_state()
        return t

    # supress PLY warning
    t_SINGLEQ1_ignore = ''

    def t_SINGLEQ1_error(self, t):
        raise SyntaxError('EOL while scanning single quoted string')

    def t_start_single_quoted_q2_string(self, t):
        r'"'
        t.lexer.push_state("SINGLEQ2")
        t.type = "STRING_START_SINGLE"
        return t

    def t_SINGLEQ2_simple(self, t):
        r'[^"\\\n]+'
        t.type = "STRING_CONTINUE"
        return t

    def t_SINGLEQ2_end(self, t):
        r'"'
        t.type = "STRING_END"
        t.lexer.pop_state()
        return t

    # supress PLY warning
    t_SINGLEQ2_ignore = ''

    def t_SINGLEQ2_error(self, t):
        raise SyntaxError('EOL while scanning single quoted string')

    def t_error(self, t):
        raise SyntaxError('invalid syntax')

    def __init__(self):
        self.lexer = lex.lex(
            module=self, outputdir=_lex_dir, lextab=_lex_module, optimize=1,
        )
        self.token_stream = None

    def input(self, txt):
        self.lexer.input(txt)
        self.next_token = self.make_token_stream().next

    def token(self):
        try:
            tok = self.next_token()
            return tok
        except StopIteration:
            pass

    def make_token_stream(self):
        token_stream = iter(self.lexer.token, None)
        token_stream = self.create_strings(token_stream)
        token_stream = self.add_endmarker(token_stream)
        return token_stream

    def create_strings(self, token_stream):
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
                msg = 'EOF while scanning single-quoted string.'
                raise SyntaxError(msg)

            s = "".join(tok.value for tok in string_toks)
            s = s.decode("string_escape")
            start_tok.type = "STRING"
            start_tok.value = s

            yield start_tok

    def add_endmarker(self, token_stream):
        for tok in token_stream:
            yield tok

        end_marker = lex.LexToken()
        end_marker.type = 'ENDMARKER'
        end_marker.value = None
        end_marker.lineno = -1
        end_marker.lexpos = -1
        end_marker.lexer = self.lexer
        yield end_marker


def tokenize(text):
    lexer = SelectorLexer()
    lexer.input(text)
    toks = []
    while True:
        t = lexer.token()
        if t is None:
            break
        toks.append(t)
    return toks


def p_selector_list1(p):
    ''' selector_list : selector ENDMARKER '''


def p_selector_list2(p):
    ''' selector_list : selector selector_comma selector_list ENDMARKER '''


def p_selector_comma1(p):
    ''' selector_comma : COMMA '''


def p_selector_comma2(p):
    ''' selector_comma : COMMA WS '''


def p_selector1(p):
    ''' selector : simple_selector '''


def p_selector2(p):
    ''' selector : simple_selector combinator selector '''


def p_selector3(p):
    ''' selector : simple_selector WS '''


def p_selector4(p):
    ''' selector : simple_selector WS selector '''


def p_selector5(p):
    ''' selector : simple_selector WS combinator selector '''


def p_combinator1(p):
    ''' combinator : GREATER '''


def p_combinator2(p):
    ''' combinator : GREATER WS '''


def p_simple_selector1(p):
    ''' simple_selector : element_name '''


def p_simple_selector2(p):
    ''' simple_selector : element_name secondary_list '''


def p_simple_selector3(p):
    ''' simple_selector : secondary_list '''


def p_secondary_list1(p):
    ''' secondary_list : secondary_item '''


def p_secondary_list2(p):
    ''' secondary_list : secondary_item secondary_list '''


def p_secondary_item(p):
    ''' secondary_item : hash_name
                       | class_name
                       | attribute
                       | pseudostate
                       | subcontrol '''


def p_element_name(p):
    ''' element_name : NAME
                     | STAR '''


def p_hash_name(p):
    ''' hash_name : HASH NAME '''


def p_class_name(p):
    ''' class_name : DOT NAME '''


def p_attribute(p):
    ''' attribute : lbracket NAME equals STRING rbracket '''


def p_pseudostate1(p):
    ''' pseudostate : COLON NAME '''


def p_pseudostate2(p):
    ''' pseudostate : COLON BANG NAME '''


def p_subcontrol(p):
    ''' subcontrol : DOUBLE_COLON NAME '''


def p_lbracket1(p):
    ''' lbracket : LSQB '''


def p_lbacket2(p):
    ''' lbracket : LSQB WS '''


def p_equals1(p):
    ''' equals : EQUAL '''


def p_equals2(p):
    ''' equals : WS EQUAL '''


def p_equals3(p):
    ''' equals : EQUAL WS '''


def p_equals4(p):
    ''' equals : WS EQUAL WS '''


def p_rbracket1(p):
    ''' rbracket : RSQB '''


def p_rbracket2(p):
    ''' rbracket : WS RSQB '''


def p_error(p):
    print 'error'


tokens = SelectorLexer.tokens


_parse_module = 'enaml.styling.parse_tab.parsetab'
_parser = yacc.yacc(
    debug=1, outputdir=_lex_dir, tabmodule=_parse_module, optimize=1,
    #errorlog=yacc.NullLogger(),
)


def parse(selector):
    try:
        import time
        t1 = time.clock()
        r = _parser.parse(selector, debug=0, lexer=SelectorLexer())
        t2 = time.clock()
        print t2 - t1
        return r
    except SyntaxError:
        print 'invalid selector: %s' % selector
