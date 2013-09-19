#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.parser import parse


def compile_source(source, item, filename='<test>'):
    """ Compile Enaml source code and return the target item.

    Parameters
    ----------
    source : str
        The Enaml source code string to compile.

    item : str
        The name of the item in the resulting namespace to return.

    filename : str, optional
        The filename to use when compiling the code. The default
        is '<test>'.

    Returns
    -------
    result : object
        The named object from the resulting namespace.

    """
    ast = parse(source, filename)
    code = EnamlCompiler.compile(ast, filename)
    namespace = {}
    exec code in namespace
    return namespace[item]
