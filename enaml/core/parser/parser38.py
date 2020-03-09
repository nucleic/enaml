#------------------------------------------------------------------------------
# Copyright (c) 2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import ast

from .parser36 import Python36EnamlParser


class Python38EnamlParser(Python36EnamlParser):
    """Enaml parser supporting Python 3.8 syntax.

    Main differences from 3.6 parser are :

    - set type_ignore to [] on Module

    """
    parser_id = '38'

    def create_module(self, body, **kwargs):
        """Create a module object with the given body.

        We set type_ignores to [].

        """
        return ast.Module(body=body, type_ignores=[])

    def _make_args(self, args, defaults=[], vararg=None, kwonlyargs=[],
                   kw_defaults=[], kwarg=None, posonlyargs=[]):
        """Build an ast node for function arguments.

        """
        return ast.arguments(posonlyargs=posonlyargs, args=args,
                             defaults=defaults, vararg=vararg,
                             kwonlyargs=kwonlyargs, kw_defaults=kw_defaults,
                             kwarg=kwarg)
