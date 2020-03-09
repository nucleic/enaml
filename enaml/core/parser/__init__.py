#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import sys

from .base_parser import ParsingError

py_version = sys.version_info
if py_version < (3,):
    raise ImportError('Only Python 3 is supported.')
else:
    if py_version[1] < 3:
        raise ImportError('Python < 3.3 is not supported.')
    elif py_version[1] == 3:
        from .parser3 import Python3EnamlParser
        _parser = Python3EnamlParser()
    elif py_version[1] == 4:
        from .parser34 import Python34EnamlParser
        _parser = Python34EnamlParser()
    elif py_version[1] == 5:
        from .parser35 import Python35EnamlParser
        _parser = Python35EnamlParser()
    elif py_version[1] in (6, 7):
        from .parser36 import Python36EnamlParser
        _parser = Python36EnamlParser()
    else:
        from .parser38 import Python38EnamlParser
        _parser = Python38EnamlParser()


def write_tables():
    _parser.lexer().write_tables()
    _parser.write_tables()


def parse(enaml_source, filename='Enaml'):
    """Parse an enaml file source. """
    return _parser.parse(enaml_source, filename)
