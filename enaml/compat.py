#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys
import re
import builtins
import codecs
import tokenize
from types import CodeType

USE_WORDCODE = sys.version_info >= (3, 6)

STRING_ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)


BYTES_ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)


def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return STRING_ESCAPE_SEQUENCE_RE.sub(decode_match, s)


def encode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return bytes(BYTES_ESCAPE_SEQUENCE_RE.sub(decode_match, s), 'ascii')

# Functions used to update the co_filename slot of a code object
try:
    from _imp import _fix_co_filename
except ImportError:
    try:
        from .c_compat import _fix_co_filename
    except ImportError:
        _fix_co_filename = None

if _fix_co_filename:
    def update_code_co_filename(code, src_path):
        """Update the co_filename attribute of the code.

        Parameters
        ----------
        code : types.CodeType
            Code object from which the co_filename should be updated.

        src_path : string
            Path to the source file for the code object

        Returns
        -------
        updated_code : types.CodeType
            Code object whose co_filename field is set to src_path.

        """
        _fix_co_filename(code, src_path)
        return code
else:
    def update_code_co_filename(code, src_path):
        """Update the co_filename attribute of the code.

        Parameters
        ----------
        code : types.CodeType
            Code object from which the co_filename should be updated.

        src_path : string
            Path to the source file for the code object

        Returns
        -------
        updated_code : types.CodeType
            Code object whose co_filename field is set to src_path.

        """
        if src_path == code.co_filename:
            return code
        new_consts = tuple(c if not isinstance(c, CodeType)
                           else update_code_co_filename(c, src_path)
                           for c in code.co_consts)
        updated_code = CodeType(code.co_argcount,
                                code.co_nlocals,
                                code.co_stacksize,
                                code.co_flags,
                                code.co_code,
                                new_consts,
                                code.co_names,
                                code.co_varnames,
                                src_path,
                                code.co_name,
                                code.co_firstlineno,
                                code.co_lnotab,
                                code.co_freevars,
                                code.co_cellvars)
        return updated_code


# Source file reading and encoding detection
def read_source(filename):
    with tokenize.open(filename) as f:
        return f.read()

detect_encoding = tokenize.detect_encoding
