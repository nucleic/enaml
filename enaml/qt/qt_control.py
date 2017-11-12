#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.widgets.control import ProxyControl

from .qt_constraints_widget import QtConstraintsWidget


class QtControl(QtConstraintsWidget, ProxyControl):
    """ A Qt implementation of an Enaml Control.

    """
    # The QtConstraintsWidget superclass is a sufficient implementation.
    pass
