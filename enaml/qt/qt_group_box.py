#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from .qt.QtCore import Qt, QSize, Signal
from .qt.QtGui import QGroupBox
from .qt_container import QtContainer


QT_ALIGNMENTS = {
    'left': Qt.AlignLeft,
    'right': Qt.AlignRight,
    'center': Qt.AlignHCenter,
}


class QResizingGroupBox(QGroupBox):
    """ A subclass of QGroupBox which behaves like a container.

    """
    #: A signal which is emitted on a resize event.
    resized = Signal()

    #: The internally cached size hint.
    _size_hint = QSize()

    def resizeEvent(self, event):
        """ Converts a resize event into a signal.

        """
        super(QResizingGroupBox, self).resizeEvent(event)
        self.resized.emit()

    def sizeHint(self):
        """ Returns the previously set size hint. If that size hint is
        invalid, the superclass' sizeHint will be used.

        """
        hint = self._size_hint
        if not hint.isValid():
            return super(QResizingGroupBox, self).sizeHint()
        return QSize(hint)

    def setSizeHint(self, hint):
        """ Sets the size hint to use for this widget.

        """
        self._size_hint = QSize(hint)

    def minimumSizeHint(self):
        """ Returns the minimum size hint of the widget.

        The minimum size hint for a QResizingGroupBox is conceptually
        the same as its size hint, so we just return that value.

        """
        return self.sizeHint()


class QtGroupBox(QtContainer):
    """ A Qt implementation of an Enaml GroupBox.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying QGroupBox control.

        """
        widget = QResizingGroupBox(parent)
        if sys.platform == 'darwin':
            # On OSX, the widget item layout rect is too small.
            # Setting this attribute forces the widget item to
            # use the widget rect for layout.
            widget.setAttribute(Qt.WA_LayoutUsesWidgetRect, True)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtGroupBox, self).create(tree)
        self.set_title(tree['title'])
        self.set_flat(tree['flat'])
        self.set_title_align(tree['title_align'])

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def contents_margins(self):
        """ Get the current contents margins for the group box.

        """
        m = self.widget().contentsMargins()
        return (m.top(), m.right(), m.bottom(), m.left())

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        widget = self.widget()
        old_margins = widget.contentsMargins()
        self.set_title(content['title'])
        new_margins = widget.contentsMargins()
        if old_margins != new_margins:
            self.contents_margins_updated()

    def on_action_set_title_align(self, content):
        """ Handle the 'set_title_align' action from the Enaml widget.

        """
        self.set_title_align(content['title_align'])

    def on_action_set_flat(self, content):
        """ Handle the 'set_flat' action from the Enaml widget.

        """
        self.set_flat(content['flat'])

    #--------------------------------------------------------------------------
    # Widget Update methods
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Updates the title of group box.

        """
        self.widget().setTitle(title)

    def set_flat(self, flat):
        """ Updates the flattened appearance of the group box.

        """
        self.widget().setFlat(flat)

    def set_title_align(self, align):
        """ Updates the alignment of the title of the group box.

        """
        qt_align = QT_ALIGNMENTS[align]
        self.widget().setAlignment(qt_align)

