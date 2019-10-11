#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from .base_parser import ParsingError

py_version = sys.version_info
if py_version < (3,):
    from .parser2 import Python2EnamlParser
    _parser = Python2EnamlParser()
else:
    if py_version[1] < 3:
        raise ImportError('Python < 3.3 is not supported')
    elif py_version[1] == 3:
        from .parser3 import Python3EnamlParser
        _parser = Python3EnamlParser()
    elif py_version[1] == 4:
        from .parser34 import Python34EnamlParser
        _parser = Python34EnamlParser()
    elif py_version[1] == 5:
        from .parser35 import Python35EnamlParser
        _parser = Python35EnamlParser()
    else:
        from .parser36 import Python36EnamlParser
        _parser = Python36EnamlParser()


def write_tables():
    _parser.lexer().write_tables()
    _parser.write_tables()


def parse(enaml_source, filename='Enaml'):
    """Parse an enaml file source. """
    return _parser.parse(enaml_source, filename)
