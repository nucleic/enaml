#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Event, ForwardTyped

from .extensionpoint import ExtensionPointEvent


def Workbench():
    from .workbench import Workbench
    return Workbench


class Plugin(Atom):
    """

    """
    extensions_changed = Event(ExtensionPointEvent)

    workbench = ForwardTyped(Workbench)

    def start(self):
        pass

    def stop(self):
        pass

    def dispose(self):
        pass

    def get_extension_points(self):
        pass

    def contributions(self):
        return []
