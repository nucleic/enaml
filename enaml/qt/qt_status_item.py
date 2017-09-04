#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Constant

from enaml.widgets.status_item import ProxyStatusItem

from .qt_toolkit_object import QtToolkitObject


class QtStatusItem(QtToolkitObject, ProxyStatusItem):
    """ A Qt implementation of an Enaml ProxyStatusItem.

    """
    #: The status has no widget representation. All child widgets will
    #: be reparented by the status bar during the layout pass.
    widget = Constant(None)

    def create_widget(self):
        """ A reimplemented parent class method.

        """
        pass

    def destroy(self):
        """ A reimplemented parent class destructor.

        """
        del self.declaration

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def status_widget(self):
        """ Get the status widget defined for this item.

        """
        d = self.declaration.status_widget()
        if d is not None:
            return d.proxy.widget

    def is_permanent(self):
        """ Get whether this status item should be permanent.

        """
        return self.declaration.mode == 'permanent'

    def stretch(self):
        """ Get the stretch factor to apply to the item.

        """
        return self.declaration.stretch

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for the status item.

        """
        parent = self.parent()
        if parent is not None:
            parent.refresh_item(self)

    def child_removed(self, child):
        """ Handle the child removed event for the status item.

        """
        parent = self.parent()
        if parent is not None:
            parent.refresh_item(self)

    #--------------------------------------------------------------------------
    # ProxyStatusItem API
    #--------------------------------------------------------------------------
    def set_mode(self, mode):
        """ Set the mode of the status item.

        """
        parent = self.parent()
        if parent is not None:
            parent.refresh_item(self)

    def set_stretch(self, stretch):
        """ Set the stretch factor of the status item.

        """
        parent = self.parent()
        if parent is not None:
            parent.refresh_item(self)
