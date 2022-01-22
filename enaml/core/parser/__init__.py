# ------------------------------------------------------------------------------
# Copyright (c) 2013-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
import io
import os
import tokenize
from typing import Optional, Callable, Iterator, Union

from pegen.tokenizer import Tokenizer

from ..enaml_ast import Module
from .enaml_parser import EnamlParser


def _parse(
    stream: io.TextIOBase,
    path: str = "Enaml",
    py_version: Optional[tuple] = None,
    token_stream_factory: Optional[
        Callable[[Callable[[], str]], Iterator[tokenize.TokenInfo]]
    ] = None,
    verbose: bool = False,
) -> Module:
    tok_stream = (
        token_stream_factory(stream.readline)
        if token_stream_factory
        else tokenize.generate_tokens(stream.readline)
    )
    tokenizer = Tokenizer(tok_stream, verbose=verbose, path=path)
    parser = EnamlParser(
        tokenizer,
        verbose=verbose,
        filename=os.path.basename(path),
        py_version=py_version,
    )
    return parser.parse("start")

# XXX document
# filename is named so for back ward compat
def parse(
    source: str,
    filename: str = "Enaml",
    py_version: Optional[tuple] = None,
    token_stream_factory: Optional[
        Callable[[Callable[[], str]], Iterator[tokenize.TokenInfo]]
    ] = None,
    verbose: bool = False,
) -> Module:
    """Parse enaml source text.

    This function is meant for in memory sources and one should prefer parse_file
    for sources existing in a file.

    Parameters
    ----------


    """
    return _parse(
        io.StringIO(source), filename, py_version, token_stream_factory, verbose
    )


# XXX document
def parse_file(
    path: Union[str, os.PathLike],
    py_version: Optional[tuple] = None,
    token_stream_factory: Optional[
        Callable[[Callable[[], str]], Iterator[tokenize.TokenInfo]]
    ] = None,
    verbose: bool = False,
) -> Module:
    """Optimized parsing function for parsing source files."""
    with tokenize.open(path) as f:
        return _parse(f, path, py_version, token_stream_factory, verbose)
