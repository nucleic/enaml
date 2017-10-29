#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" Command-line tool to run .enaml files.

"""
from __future__ import print_function

import optparse
import os
import sys
import types

from future.utils import exec_

from enaml import imports
from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.compat import read_source


def main():
    usage = 'usage: %prog [options] enaml_file [script arguments]'
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    parser.allow_interspersed_args = False
    parser.add_option(
        '-c', '--component', default='Main', help='The component to view'
    )

    options, args = parser.parse_args()

    if len(args) == 0:
        print('No .enaml file specified')
        sys.exit()
    else:
        enaml_file = args[0]
        script_argv = args[1:]

    enaml_code = read_source(enaml_file)

    # Parse and compile the Enaml source into a code object
    ast = parse(enaml_code, filename=enaml_file)
    code = EnamlCompiler.compile(ast, enaml_file)

    # Create a proper module in which to execute the compiled code so
    # that exceptions get reported with better meaning
    module = types.ModuleType('__main__')
    module.__file__ = os.path.abspath(enaml_file)
    sys.modules['__main__'] = module
    ns = module.__dict__

    # Put the directory of the Enaml file first in the path so relative
    # imports can work.
    sys.path.insert(0, os.path.abspath(os.path.dirname(enaml_file)))
    # Bung in the command line arguments.
    sys.argv = [enaml_file] + script_argv
    with imports():
        exec_(code, ns)

    requested = options.component
    if requested in ns:
        from enaml.qt.qt_application import QtApplication
        app = QtApplication()
        window = ns[requested]()
        window.show()
        window.send_to_front()
        app.start()
    elif 'main' in ns:
        ns['main']()
    else:
        msg = "Could not find component '%s'" % options.component
        print(msg)


if __name__ == '__main__':
    main()
