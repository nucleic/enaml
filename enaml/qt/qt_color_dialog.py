#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.colors import Color
from enaml.widgets.color_dialog import ProxyColorDialog

from .QtCore import Signal
from .QtGui import QColor
from .QtWidgets import QColorDialog

from .qt_toolkit_dialog import QtToolkitDialog


def color_from_qcolor(q):
    """ Convert a QColor into an Enaml Color.

    Parameters
    ----------
    q : QColor
        The Qt color to convert to Enaml Color.

    Returns
    -------
    result : Color or None
        An Enaml Color or None if the QColor is not valid.

    """
    if not q.isValid():
        return None
    return Color(q.red(), q.green(), q.blue(), q.alpha())


# Guard flags
CURRENT_GUARD = 0x1


class QColorDialogEx(QColorDialog):
    """ A custom QColorDialog which emits a custom finished signal.

    """
    #: A signal emitted at the end of the 'done' method. This works
    #: around the standard QColorDialog behavior which emits the
    #: 'colorSelected' signal *after* the 'finished' signal.
    reallyFinished = Signal(int)

    def done(self, result):
        """ A reimplemented done method.

        This method emits the 'reallyFinished' signal on completion.

        """
        super(QColorDialogEx, self).done(result)
        self.reallyFinished.emit(result)


class QtColorDialog(QtToolkitDialog, ProxyColorDialog):
    """ A Qt implementation of an Enaml ProxyColorDialog.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QColorDialogEx)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    def create_widget(self):
        """ Create the underlying QColorDialog.

        """
        self.widget = QColorDialogEx(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtColorDialog, self).init_widget()
        d = self.declaration
        self.set_current_color(d.current_color)
        self.set_show_alpha(d.show_alpha)
        self.set_show_buttons(d.show_buttons)
        widget = self.widget
        widget.currentColorChanged.connect(self.on_current_color_changed)
        widget.colorSelected.connect(self.on_color_selected)
        # use the custom finished signal instead of the superclass'
        widget.finished.disconnect(self.on_finished)
        widget.reallyFinished.connect(self.on_finished)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def get_default_title(self):
        """ Get the default window title for the color dialog.

        """
        return u'Select Color'

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_current_color_changed(self, qcolor):
        """ Handle the 'currentColorChanged' signal from the widget.

        """
        d = self.declaration
        if d is not None:
            self._guard |= CURRENT_GUARD
            try:
                d.current_color = color_from_qcolor(qcolor)
            finally:
                self._guard &= ~CURRENT_GUARD

    def on_color_selected(self, qcolor):
        """ Handle the 'colorSelected' signal from the widget.

        """
        d = self.declaration
        if d is not None:
            d.selected_color = color_from_qcolor(qcolor)

    #--------------------------------------------------------------------------
    # ProxyColorDialog API
    #--------------------------------------------------------------------------
    @staticmethod
    def custom_count():
        """ Get the number of available custom colors.

        """
        return QColorDialog.customCount()

    @staticmethod
    def custom_color(index):
        """ Get the custom color for the given index.

        """
        qrgb = QColorDialog.customColor(index)
        return color_from_qcolor(QColor.fromRgba(qrgb))

    @staticmethod
    def set_custom_color(index, color):
        """ Set the custom color for the given index.

        """
        QColorDialog.setCustomColor(index, color.argb)

    def set_current_color(self, color):
        """ Set the current color for the underlying widget.

        """
        if not self._guard & CURRENT_GUARD:
            if color is not None:
                qcolor = QColor.fromRgba(color.argb)
            else:
                qcolor = QColor()
            self.widget.setCurrentColor(qcolor)

    def set_show_alpha(self, show):
        """ Set the show alpha option on the underlying widget.

        """
        widget = self.widget
        opt = widget.options()
        if show:
            opt |= QColorDialog.ShowAlphaChannel
        else:
            opt &= ~QColorDialog.ShowAlphaChannel
        widget.setOptions(opt)

    def set_show_buttons(self, show):
        """ Set the show buttons option on the underlying widget.

        """
        widget = self.widget
        opt = widget.options()
        if show:
            opt &= ~QColorDialog.NoButtons
        else:
            opt |= QColorDialog.NoButtons
        widget.setOptions(opt)
