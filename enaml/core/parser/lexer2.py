#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .base_lexer import BaseEnamlLexer
from ...compat import decode_escapes


class Python2EnamlLexer(BaseEnamlLexer):
    """Lexer specialized for Python 2.

    Under Python 2 the lexer is always passed utf-8 encoded byte string

    """

    lex_id = '2'

    reserved = dict(list(BaseEnamlLexer.reserved.items()) +
                    [('exec', 'EXEC'),
                     ('print', 'PRINT'),
                     ]
                    )

    def format_string(self, string, quote_type):
        """Python 2 support only u, b and r as quote type.

        """
        if quote_type == "" or quote_type == "b":
            return string.decode("string_escape"), 'STRING'
        elif quote_type == "u":
            return decode_escapes(string.decode('utf-8')), 'STRING'
        elif quote_type == "ur":
            return string.decode("raw_unicode_escape"), 'STRING'
        elif quote_type in ("r", "br"):
            return string, 'STRING'
        else:
            msg = 'Unknown string quote type: %r' % quote_type
            raise AssertionError(msg)
