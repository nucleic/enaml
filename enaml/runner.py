#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" Command-line tool to run .enaml files.

"""
import optparse
import os
import sys
import types
import warnings

from enaml import imports
from enaml.stdlib.sessions import show_simple_view
from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler


def prepare_toolkit(toolkit_option):
    """ Prepare the toolkit to be used by Enaml.

    This function determines the Enaml toolkit based on the values of
    the toolkit option and the ETS_TOOLKIT environment variable. ETS
    gui components default to Wx when ETS_TOOLKIT is not defined, but
    Enaml defaults to Qt. Under this condition, ETS_TOOLKIT is updated
    to be consistent with Enaml. If ETS_TOOLKIT is already set and it
    is incompatibile with the -t option, a warning is raised.

    Parameters
    ----------
    toolkit_option : str
        The toolkit option provided to the enaml-run script.

    Returns
    -------
    result : str
       The toolkit to be used by enaml.

    """
    if 'ETS_TOOLKIT' in os.environ:
        ets_toolkit = os.environ['ETS_TOOLKIT'].lower().split('.')[0][:2]
        if toolkit_option == 'default' and ets_toolkit in ('wx', 'qt'):
            enaml_toolkit = ets_toolkit
        else:
            enaml_toolkit = 'wx' if toolkit_option == 'wx' else 'qt'
            if ets_toolkit != enaml_toolkit:
                msg = (
                    'The --toolkit option is different from the ETS_TOOLKIT '
                    'environment variable, which can cause incompatibility '
                    'issues when using enable or chaco components.'
                )
                warnings.warn(msg)
    else:
        if toolkit_option == 'wx':
            enaml_toolkit = 'wx'
            os.environ['ETS_TOOLKIT'] = 'wx'
        else:
            enaml_toolkit = 'qt'
            os.environ['ETS_TOOLKIT'] = 'qt4'
    return enaml_toolkit


def main():
    usage = 'usage: %prog [options] enaml_file [script arguments]'
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    parser.allow_interspersed_args = False
    parser.add_option(
        '-c', '--component', default='Main', help='The component to view'
    )
    parser.add_option(
        '-t', '--toolkit', default='default',
        help='The GUI toolkit to use [default: qt or ETS_TOOLKIT].'
    )

    options, args = parser.parse_args()
    toolkit = prepare_toolkit(options.toolkit)

    if len(args) == 0:
        print 'No .enaml file specified'
        sys.exit()
    else:
        enaml_file = args[0]
        script_argv = args[1:]

    with open(enaml_file, 'rU') as f:
        enaml_code = f.read()

    # Parse and compile the Enaml source into a code object
    ast = parse(enaml_code, filename=enaml_file)
    code = EnamlCompiler.compile(ast, enaml_file)

    # Create a proper module in which to execute the compiled code so
    # that exceptions get reported with better meaning
    module = types.ModuleType('__main__')
    module.__file__ = enaml_file
    ns = module.__dict__

    # Put the directory of the Enaml file first in the path so relative
    # imports can work.
    sys.path.insert(0, os.path.abspath(os.path.dirname(enaml_file)))
    # Bung in the command line arguments.
    sys.argv = [enaml_file] + script_argv
    with imports():
        exec code in ns

    requested = options.component
    if requested in ns:
        component = ns[requested]
        descr = 'Enaml-run "%s" view' % requested
        show_simple_view(component(), toolkit, descr)
    elif 'main' in ns:
        ns['main']()
    else:
        msg = "Could not find component '%s'" % options.component
        print msg


if __name__ == '__main__':
    main()
