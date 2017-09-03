#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from future.builtins import bytes

from .base_lexer import BaseEnamlLexer


class Python3EnamlLexer(BaseEnamlLexer):
    """Lexer specialized for Python.

    """
    operators = BaseEnamlLexer.operators + ((r'->', 'RETURNARROW'),)

    t_RETURNARROW = r'->'

    reserved = dict(list(BaseEnamlLexer.reserved.items()) +
                    [('nonlocal', 'NONLOCAL'),
                     ]
                    )

    def format_string(self, string, quote_type):
        """Python support u r and b as quote type.

        """
        if quote_type == "" or quote_type == "u" or quote_type == "ur":
            u8 = string.encode('utf-8')
            if quote_type == "ur":
                aux = u8.decode('raw_unicode_escape')
            else:
                aux = u8.decode('unicode_escape')
            return aux.encode('latin-1').decode('utf-8')
        elif quote_type == "r":
            return string
        elif quote_type == "b":
            return bytes(string)
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
        seen_async_def = False
        async_depth = 0

        for tok in token_stream:

            if seen_async_def and tok.type == 'INDENT':
                async_depth += 1
                seen_async_def = False

            elif tok.type == 'ASYNC':
                next_token = next(token_stream)
                if next_token.type == 'DEF':
                    seen_async_def = True
                else:
                    self.handle_async_token(tok, async_depth)
                yield tok
                yield next_token
                continue

            elif tok.type == 'AWAIT':
                self.handle_async_token(tok, async_depth)

            elif async_depth and tok.type == 'DEDENT':
                async_depth -= 1

            yield tok

    def handle_async_token(self, tok, async_depth):
        """Handle an ASYNC/AWAIT token depending on whether or not we are
        inside a coroutine definition.

        """
        if not async_depth:
            tok.type = 'NAME'
