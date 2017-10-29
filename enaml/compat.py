#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys
import re
import codecs

IS_PY3 = sys.version_info >= (3,)

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

if IS_PY3:
    import tokenize

    def read_source(filename):
        with tokenize.open(filename) as f:
            return f.read()

    def detect_encoding(filename):
        with open(filename, 'rb') as fileobj:
            return tokenize.detect_encoding(fileobj.readline)

else:
    # Adapted from https://stackoverflow.com/questions/38374489/
    # get-encoding-specified-in-magic-line-shebang-from-within-module
    import re
    from codecs import lookup, BOM_UTF8
    from types import CodeType

    cookie_re = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)')
    blank_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)')

    def _get_normal_name(orig_enc):
        """Imitates get_normal_name in tokenizer.c."""
        # Only care about the first 12 characters.
        enc = orig_enc[:12].lower().replace("_", "-")
        if enc == "utf-8" or enc.startswith("utf-8-"):
            return "utf-8"
        if enc in ("latin-1", "iso-8859-1", "iso-latin-1") or \
           enc.startswith(("latin-1-", "iso-8859-1-", "iso-latin-1-")):
            return "iso-8859-1"
        return orig_enc

    def detect_encoding(filename):
        bom_found = False
        encoding = None
        default = 'ascii'

        def find_cookie(line):
            match = cookie_re.match(line)
            if not match:
                return None
            encoding = _get_normal_name(match.group(1))
            try:
                lookup(encoding)
            except LookupError:
                # This behaviour mimics the Python interpreter
                raise SyntaxError(
                    "unknown encoding for {!r}: {}".format(
                        filename, encoding))

            if bom_found:
                if encoding != 'utf-8':
                    # This behaviour mimics the Python interpreter
                    raise SyntaxError(
                        'encoding problem for {!r}: utf-8'.format(filename))
                encoding += '-sig'
            return encoding

        with open(filename, 'rb') as fileobj:
            first = next(fileobj, '')
            if first.startswith(BOM_UTF8):
                bom_found = True
                first = first[3:]
                default = 'utf-8-sig'
            if not first:
                return default

            encoding = find_cookie(first)
            if encoding:
                return encoding
            if not blank_re.match(first):
                return default

            second = next(fileobj, '')

        if not second:
            return default
        return find_cookie(second) or default

    # As per PEP 263:
    #  - read the file
    #  - decode it assuming a fixed per file encoding
    #  - convert to a utf-8 byte string (ie encode)
    #  - tokenize utf-8 content
    def read_source(filename):
        enc = detect_encoding(filename)
        with open(filename, 'rU') as f:
            src = f.read()
        return src.decode(enc).encode('utf-8')
