#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from .base_lexer import BaseEnamlLexer
from ...compat import decode_escapes, encode_escapes


class Python3EnamlLexer(BaseEnamlLexer):
    """Lexer specialized for Python.

    """
    operators = BaseEnamlLexer.operators + ((r'->', 'RETURNARROW'),)

    delimiters = BaseEnamlLexer.delimiters + ('BYTES',)

    t_RETURNARROW = r'->'

    reserved = dict(list(BaseEnamlLexer.reserved.items()) +
                    [('nonlocal', 'NONLOCAL'),
                     ]
                    )

    def format_string(self, string, quote_type):
        """Python support u, r and b as quote type.

        """
        if quote_type == "" or quote_type == "u":
            # Turn escaped characters into what they should be.
            return decode_escapes(string), 'STRING'
        elif quote_type == "r":
            return string, 'STRING'
        elif quote_type == "b":
            # Only ascii characters are allowed in byte string literals so this
            # is safe, and handle correctly \u0394\n by only processing escaped
            # characters that can be represented in ascii
            return encode_escapes(string), 'BYTES'
        elif quote_type in ('br', 'rb'):
            # Only ascii characters are allowed in byte string literals
            return bytes(string, 'ascii'), 'BYTES'
        else:
            msg = 'Unknown string quote type: %r' % quote_type
            raise AssertionError(msg)


class Python34EnamlLexer(Python3EnamlLexer):
    """Lexer specialized for Python.

    """
    reserved = dict(list(Python3EnamlLexer.reserved.items()) +
                    [('True', 'TRUE'),
                     ('False', 'FALSE'),
                     ('None', 'NONE'),
                     ]
                    )


class Python35EnamlLexer(Python34EnamlLexer):
    """Lexer specialized for Python > 3.5.

    """

    lex_id = '35'

    operators = Python34EnamlLexer.operators + ((r'@=', 'ATEQUAL'),)

    t_ATEQUAL = r'@='

    reserved = dict(list(Python34EnamlLexer.reserved.items()) +
                    [('async', 'ASYNC'),
                     ('await', 'AWAIT'),
                     ]
                    )

    def make_token_stream(self):
        """Add analysis of ASYNC/AWAIT.

        """
        token_stream = super(Python35EnamlLexer, self).make_token_stream()
        token_stream = self.analyse_async(token_stream)
        return token_stream

    def analyse_async(self, token_stream):
        """Transform ASYNC/AWAIT tokens to NAME outside async function.

        """
        for tok in token_stream:

            if tok.type == 'ASYNC':
                next_token = next(token_stream)
                if next_token.type not in ('DEF', 'WITH', 'FOR', 'NAME'):
                    tok.type = 'NAME'
                yield tok
                yield next_token
                continue
            elif tok.type == 'AWAIT':
                next_token = next(token_stream)
                if next_token.type != 'NAME':
                    tok.type = 'NAME'
                yield tok
                yield next_token
                continue

            yield tok


class Python36EnamlLexer(Python35EnamlLexer):
    """Lexer specialized for Python 3.6.

    Support for _ in numeric literals (comes from stdlib tokenize.NUMBER)

    """
    lex_id = '36'

    delimiters = Python35EnamlLexer.delimiters + ('FSTRING',)

    def format_string(self, string, quote_type):
        """Python support u, r and b as quote type.

        """
        if 'f' in quote_type.lower():
            if 'r' not in quote_type.lower():
                string =  decode_escapes(string)
            return string, 'FSTRING'
        return super(Python36EnamlLexer, self).format_string(string,
                                                             quote_type)


class Python37EnamlLexer(Python36EnamlLexer):
    """Lexer specialized for Python 3.7.

    Make async and await keywords

    """
    lex_id = '37'

    def analyse_async(self, token_stream):
        for tok in token_stream:
            yield tok
