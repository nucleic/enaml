#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from future.utils import exec_

from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.parsing import parse


def compile_source(source, item, filename='<test>', namespace=None):
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

    namespace : dict
        Namespace in which to execute the code

    Returns
    -------
    result : object
        The named object from the resulting namespace.

    """
    ast = parse(source, filename)
    code = EnamlCompiler.compile(ast, filename)
    namespace = namespace or {}
    exec_(code, namespace)
    return namespace[item]
