#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QComboBox
from .qt_control import QtControl


class QtComboBox(QtControl):
    """ A Qt implementation of an Enaml ComboBox.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying combo box widget.

        """
        box = QComboBox(parent)
        box.setInsertPolicy(QComboBox.NoInsert)
        return box

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtComboBox, self).create(tree)
        self.set_items(tree['items'])
        self.set_index(tree['index'])
        self.set_editable(tree['editable'])
        self.widget().currentIndexChanged.connect(self.on_index_changed)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_index(self, content):
        """ Handle the 'set_index' action from the Enaml widget.

        """
        self.set_index(content['index'])

    def on_action_set_items(self, content):
        """ Handle the 'set_items' action from the Enaml widget.

        """
        self.set_items(content['items'])

    def on_action_set_editable(self, content):
        """ Handle the 'set_editable' action from the Enaml widget.

        """
        self.set_editable(content['editable'])
        # The update is needed to avoid artificats (at least on Windows)
        self.widget().update()

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_index_changed(self):
        """ The signal handler for the index changed signal.

        """
        if 'index' not in self.loopback_guard:
            content = {'index': self.widget().currentIndex()}
            self.send_action('index_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_items(self, items):
        """ Set the items of the ComboBox.

        """
        widget = self.widget()
        count = widget.count()
        nitems = len(items)
        for idx, item in enumerate(items[:count]):
            widget.setItemText(idx, item)
        if nitems > count:
            for item in items[count:]:
                widget.addItem(item)
        elif nitems < count:
            for idx in reversed(range(nitems, count)):
                widget.removeItem(idx)

    def set_index(self, index):
        """ Set the current index of the ComboBox.

        """
        with self.loopback_guard('index'):
            self.widget().setCurrentIndex(index)

    def set_editable(self, editable):
        """ Set whether the combo box is editable.

        """
        self.widget().setEditable(editable)

