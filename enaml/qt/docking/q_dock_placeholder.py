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
            index = parent.indexOf(widget)
            parent.replaceWidget(index, self)
        else:
            index = 0
            layout = parent.layout()
            layout.replaceWidget(widget, self)
        widget.hide()

    def restore(self):
        """ Restore the placeholder widget back into it's original position.

        """
        parent = self.parent
        if parent is None:
            return
        widget = self.widget
        if isinstance(parent, QSplitter):
            index = parent.indexOf(self)
            parent.replaceWidget(index, widget)
        else:
            index = 0
            layout = parent.layout()
            layout.replaceWidget(self, widget)
        widget.show()

    def getPlaceholder(self):
        """ Get the widget this is holding a place for.

        """
        return self.widget

