#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.object_combo import ProxyObjectCombo

from .QtCore import QTimer
from .QtGui import QComboBox

from .q_resource_helpers import get_cached_qicon
from .qt_control import QtControl


# cyclic notification guard flags
SELECTED_GUARD = 0x1


class ComboRefreshTimer(QTimer):
    """ A QTimer used for collapsing items refresh requests.

    This is a single shot timer which automatically cleans itself up
    when its timer event is triggered.

    """
    def __init__(self, owner):
        """ Initialize a ComboRefreshTimer.

        Parameters
        ----------
        owner : QtObjectCombo
            The object combo which owns the timer.

        """
        super(ComboRefreshTimer, self).__init__()
        self.setSingleShot(True)
        self.owner = owner

    def timerEvent(self, event):
        """ Handle the timer event for the timer.

        This handler will call the 'refresh_items' method on the owner
        and then release all references to itself and the owner.

        """
        super(ComboRefreshTimer, self).timerEvent(event)
        owner = self.owner
        if owner is not None:
            del owner.refresh_timer
            self.owner = None
            owner.refresh_items()


class QtObjectCombo(QtControl, ProxyObjectCombo):
    """ A Qt implementation of an Enaml ProxyObjectCombo.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QComboBox)

    #: A single shot refresh timer for queing combo refreshes.
    refresh_timer = Typed(ComboRefreshTimer)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Default Value Handlers
    #--------------------------------------------------------------------------
    def _default_refresh_timer(self):
        """ Get a refresh timer for the object combo box.

        """
        return ComboRefreshTimer(self)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QComboBox widget.

        """
        self.widget = QComboBox(self.parent_widget())
        self.widget.setInsertPolicy(QComboBox.NoInsert)

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(QtObjectCombo, self).init_widget()
        self.refresh_items()
        self.widget.currentIndexChanged.connect(self.on_index_changed)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_index_changed(self, index):
        """ The signal handler for the index changed signal.

        """
        if not self._guard & SELECTED_GUARD:
            self._guard |= SELECTED_GUARD
            try:
                item = self.declaration.items[index]
                self.declaration.selected = item
            finally:
                self._guard &= ~SELECTED_GUARD

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def refresh_items(self):
        """ Refresh the items in the combo box.

        """
        d = self.declaration
        selected = d.selected
        to_string = d.to_string
        to_icon = d.to_icon
        widget = self.widget
        self._guard |= SELECTED_GUARD
        try:
            widget.clear()
            target_index = -1
            for index, item in enumerate(d.items):
                text = to_string(item)
                icon = to_icon(item)
                if icon is None:
                    qicon = None
                else:
                    qicon = get_cached_qicon(icon)
                if qicon is None:
                    widget.addItem(text)
                else:
                    widget.addItem(qicon, text)
                if item == selected:
                    target_index = index
            widget.setCurrentIndex(target_index)
        finally:
            self._guard &= ~SELECTED_GUARD

    #--------------------------------------------------------------------------
    # ProxyObjectCombo API
    #--------------------------------------------------------------------------
    def set_selected(self, selected):
        """ Set the selected object in the combo box.

        """
        if not self._guard & SELECTED_GUARD:
            self._guard |= SELECTED_GUARD
            try:
                d = self.declaration
                try:
                    index = d.items.index(selected)
                except ValueError:
                    index = -1
                self.widget.setCurrentIndex(index)
            finally:
                self._guard &= ~SELECTED_GUARD

    def set_editable(self, editable):
        """ Set whether the combo box is editable.

        """
        # The update is needed to avoid artificats (at least on Windows)
        widget = self.widget
        widget.setEditable(editable)
        widget.update()

    def request_items_refresh(self):
        """ Request a refresh of the combo box items.

        """
        self.refresh_timer.start()
