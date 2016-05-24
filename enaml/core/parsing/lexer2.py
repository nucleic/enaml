#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .base_lexer import BaseEnamlLexer


class Python2EnamlLexer(BaseEnamlLexer):
    """Lexer specialized for Python 2.

    """

    lex_id = '2'

    reserved = dict(list(BaseEnamlLexer.reserved.items()) +
                    [('exec', 'EXEC'),
                     ('print', 'PRINT'),
                     ]
                    )

    def format_string(self, string, quote_type):
        """Python 2 support only u and r as quote type.

        """
        if quote_type == "":
            return string.decode("string_escape")
        elif quote_type == "u":
            return string.decode("unicode_escape")
        elif quote_type == "ur":
            return string.decode("raw_unicode_escape")
        elif quote_type == "r" or quote_type == "b":
            return string
        else:
            msg = 'Unknown string quote type: %r' % quote_type
            raise AssertionError(msg)
