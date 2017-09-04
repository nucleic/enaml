#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from atom.api import Typed

from enaml.widgets.group_box import ProxyGroupBox

from .QtCore import Qt, QSize, Signal
from .QtWidgets import QGroupBox

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


class QtGroupBox(QtContainer, ProxyGroupBox):
    """ A Qt implementation of an Enaml ProxyGroupBox.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QResizingGroupBox)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QGroupBox control.

        """
        widget = QResizingGroupBox(self.parent_widget())
        if sys.platform == 'darwin':
            # On OSX, the widget item layout rect is too small.
            # Setting this attribute forces the widget item to
            # use the widget rect for layout.
            widget.setAttribute(Qt.WA_LayoutUsesWidgetRect, True)
        self.widget = widget

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtGroupBox, self).init_widget()
        d = self.declaration
        self.set_title(d.title, cm_update=False)
        self.set_flat(d.flat)
        self.set_title_align(d.title_align)

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    @staticmethod
    def margins_func(widget_item):
        """ Get the margins for the given widget item.

        """
        m = widget_item.widget().contentsMargins()
        return (m.top(), m.right(), m.bottom(), m.left())

    #--------------------------------------------------------------------------
    # ProxyGroupBox API
    #--------------------------------------------------------------------------
    def set_title(self, title, cm_update=True):
        """ Updates the title of group box.

        """
        if not cm_update:
            self.widget.setTitle(title)
            return
        widget = self.widget
        old_margins = widget.contentsMargins()
        widget.setTitle(title)
        new_margins = widget.contentsMargins()
        if old_margins != new_margins:
            self.margins_updated()

    def set_flat(self, flat):
        """ Updates the flattened appearance of the group box.

        """
        self.widget.setFlat(flat)

    def set_title_align(self, align):
        """ Updates the alignment of the title of the group box.

        """
        qt_align = QT_ALIGNMENTS[align]
        self.widget.setAlignment(qt_align)

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def set_border(self, border):
        """ An overridden parent class method.

        Borders are not supported on a group box, so this method is a
        no-op.

        """
        pass
