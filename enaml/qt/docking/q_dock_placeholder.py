#------------------------------------------------------------------------------
# Copyright (c) 2021, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.QtWidgets import QWidget, QSplitter


class QDockPlaceholder(QWidget):
    """ A placeholder widget which temporarily holds the spot for a tab widget.

    """
    def __init__(self, widget):
        super(QDockPlaceholder, self).__init__()

        parent = self.parent = widget.parent()
        self.widget = widget

        if isinstance(parent, QSplitter):
            # Save position in splitter
            index = parent.indexOf(widget)
            layout = parent
        else:
            layout = parent.layout()
            index = 0

        widget.hide()
        widget.setParent(None)
        layout.insertWidget(index, self)

    def restore(self):
        """ Restore the placeholder widget back into it's original position.

        """
        parent = self.parent
        if parent is None:
            return
        if isinstance(parent, QSplitter):
            # Save position in splitter
            index = parent.indexOf(self)
            layout = parent
        else:
            layout = parent.layout()
            index = 0
        self.setParent(None)
        widget = self.widget
        layout.insertWidget(index, widget)
        widget.show()

    def getPlaceholder(self):
        return self.widget
