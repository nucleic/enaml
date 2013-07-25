#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4 import Qsci


def python_tokens():
    Lexer = Qsci.QsciLexerPython
    token_map = {
        'class_name': Lexer.ClassName,
        'comment': Lexer.Comment,
        'comment_block': Lexer.CommentBlock,
        'decorator': Lexer.Decorator,
        'default': Lexer.Default,
        'double_quoted_string': Lexer.DoubleQuotedString,
        'function_method_name': Lexer.FuntionMethodName,
        'highlighted_identifier': Lexer.HighlightedIdentifier,
        'identifier': Lexer.Identifier,
        'keyword': Lexer.Keyword,
        'number': Lexer.Number,
        'operator': Lexer.Operator,
        'unclosed_string': Lexer.UnicodeString,
        'single_quoted_string': Lexer.SingleQuotedString,
        'triple_double_quoted_string': Lexer.TripleDoubleQuotedString,
        'triple_single_quoted_string': Lexer.TripleSingleQuotedString,
    }
    return Lexer, token_map
