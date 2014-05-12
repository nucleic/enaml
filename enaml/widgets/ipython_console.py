#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, set_default

from .control import Control, ProxyControl


class ProxyIPythonConsole(ProxyControl):
    """ The abstract defintion of a proxy IPythonConsole object.

    """
    #: A reference to the IPythonConsole declaration.
    declaration = ForwardTyped(lambda: IPythonConsole)


class IPythonConsole(Control):
    """ A widget which hosts an embedded IPython console.

    """
    #: The ipython console expands freely by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyIPythonConsole object.
    proxy = Typed(ProxyIPythonConsole)
