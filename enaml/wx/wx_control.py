#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.widgets.control import ProxyControl

from .wx_constraints_widget import WxConstraintsWidget


class WxControl(WxConstraintsWidget, ProxyControl):
    """ A Wx implementation of an Enaml Control.

    """
    # The WxConstraintsWidget superclass is a sufficient implementation.
    pass
