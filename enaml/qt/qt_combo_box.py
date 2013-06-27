#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.combo_box import ProxyComboBox

from .QtGui import QComboBox

from .qt_control import QtControl


# cyclic notification guard flags
INDEX_GUARD = 0x1


class QtComboBox(QtControl, ProxyComboBox):
    """ A Qt implementation of an Enaml ComboBox.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QComboBox)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QComboBox widget.

        """
        box = QComboBox(self.parent_widget())
        box.setInsertPolicy(QComboBox.NoInsert)
        self.widget = box

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(QtComboBox, self).init_widget()
        d = self.declaration
        self.set_items(d.items)
        self.set_index(d.index)
        self.set_editable(d.editable)
        self.widget.currentIndexChanged.connect(self.on_index_changed)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_index_changed(self):
        """ The signal handler for the index changed signal.

        """
        if not self._guard & INDEX_GUARD:
            self.declaration.index = self.widget.currentIndex()

    #--------------------------------------------------------------------------
    # ProxyComboBox API
    #--------------------------------------------------------------------------
    def set_items(self, items):
        """ Set the items of the ComboBox.

        """
        widget = self.widget
        count = widget.count()
        nitems = len(items)
        for idx, item in enumerate(items[:count]):
            widget.setItemText(idx, item)
        if nitems > count:
            for item in items[count:]:
                widget.addItem(item)
        elif nitems < count:
            for idx in reversed(xrange(nitems, count)):
                widget.removeItem(idx)

    def set_index(self, index):
        """ Set the current index of the ComboBox.

        """
        self._guard |= INDEX_GUARD
        try:
            self.widget.setCurrentIndex(index)
        finally:
            self._guard &= ~INDEX_GUARD

    def set_editable(self, editable):
        """ Set whether the combo box is editable.

        """
        # The update is needed to avoid artificats (at least on Windows)
        widget = self.widget
        widget.setEditable(editable)
        widget.update()
