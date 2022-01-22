#------------------------------------------------------------------------------
# Copyright (c) 2013-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import ast
import os
import tokenize
from typing import Optional, Callable, Iterator

from pegen.tokenizer import Tokenizer

from .enaml_parser import EnamlParser

def parse(
    path: str,
    py_version: Optional[tuple]=None,
    token_stream_factory: Optional[
        Callable[[Callable[[], str]], Iterator[tokenize.TokenInfo]]
    ] = None,
    verbose:bool = False,
) -> ast.Module:
    """Parse an enaml source file."""
    with open(path) as f:
        tok_stream = (
            token_stream_factory(f.readline)
            if token_stream_factory else
            tokenize.generate_tokens(f.readline)
        )
        tokenizer = Tokenizer(tok_stream, verbose=verbose, path=path)
        parser = EnamlParser(
            tokenizer,
            verbose=verbose,
            filename=os.path.basename(path),
            py_version=py_version
        )
        return parser.parse("file")
