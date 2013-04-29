#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QEvent
from PyQt4.QtGui import QFrame


class QDockFrame(QFrame):
    """ A QFrame base class for creating dock frames.

    """
    def __init__(self, manager, parent=None):
        """ Initialize a QDockFrame.

        Parameters
        ----------
        manager : DockManager
            The manager which owns the frame.

        parent : QWidget or None
            The parent of the QDockFrame.

        """
        super(QDockFrame, self).__init__(parent)
        self._manager = manager

    def manager(self):
        """ Get a reference to the manager which owns the frame.

        Returns
        -------
        result : DockManager
            The dock manager which owns this dock frame.

        """
        return self._manager

    def destroy(self):
        """ Destroy the dock frame.

        This method should only be called when the frame is being
        discarded and will no longer be used. It will release all
        internal references to objects.

        """
        self.hide()
        self.setParent(None)
        self._manager = None

    def event(self, event):
        """ Handle the window activated event for the frame.

        This handler maintains proper Z-order of the frames within
        the manager's frame list.

        """
        if event.type() == QEvent.WindowActivate:
            if self.isWindow():
                self.manager().raise_frame(self)
        return super(QDockFrame, self).event(event)
