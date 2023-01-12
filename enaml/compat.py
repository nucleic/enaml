#------------------------------------------------------------------------------
# Copyright (c) 2013-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import sys
import re
import codecs
import tokenize

PY38 = POS_ONLY_ARGS = sys.version_info >= (3, 8)

PY39 = sys.version_info >= (3, 9)

PY310 = sys.version_info >= (3, 10)

# Functions used to update the co_filename slot of a code object
# Available in Python 3.5+ (tested up to 3.8)
from _imp import _fix_co_filename

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


# Source file reading and encoding detection
def read_source(filename):
    with tokenize.open(filename) as f:
        return f.read()

detect_encoding = tokenize.detect_encoding
