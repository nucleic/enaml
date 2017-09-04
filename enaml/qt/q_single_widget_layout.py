#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .QtCore import QSize
from .QtWidgets import QLayout, QWidgetItem


class QSingleWidgetItem(QWidgetItem):
    """ A QWidgetItem subclass for use with the QSingleWidgetLayout.

    The semantics of this widget item are slightly different from that
    of the standard QWidgetItem; it always aligns its widget with the
    top left of the layout rect. This class is expressly meant for use
    by the QSingleWidgetLayout.

    """
    def setGeometry(self, rect):
        """ Set the rectangle covered by this layout item.

        Parameters
        ----------
        rect : QRect
            The rectangle that this layout item should cover.

        """
        if self.isEmpty():
            return
        s = rect.size().boundedTo(self.maximumSize())
        self.widget().setGeometry(rect.x(), rect.y(), s.width(), s.height())


class QSingleWidgetLayout(QLayout):
    """ A QLayout subclass which can have at most one layout item.

    The layout item is expanded to fit the allowable space; similar to
    how a central widget behaves in a QMainWindow. Unlike QMainWindow,
    this layout respects the maximum size of the widget. The default
    contents margins of this layout is 0px in all directions.

    """
    #: The initial value of the internal widget item.
    _item = None

    def __init__(self, parent=None):
        """ Initialize a QSingleWidgetLayout.

        Parameters
        ----------
        parent : QWidget or None
            The parent widget owner of the layout.

        """
        super(QSingleWidgetLayout, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

    # Note: do not name this method `widget` since that is a virtual
    # method on QLayoutItem which is a parent class of QLayout.
    def getWidget(self):
        """ Get the widget being managed by this layout.

        Returns
        -------
        result : QWidget or None
            The widget being managed by this layout or None if it does
            not exist.

        """
        item = self._item
        if item is not None:
            return item.widget()

    def setWidget(self, widget):
        """ Set the widget for this layout.

        Parameters
        ----------
        widget : QWidget
            The widget to manage with this layout.

        """
        old = self.getWidget()
        if old is widget:
            return
        if old is not None:
            old.setParent(None)
        if widget is not None:
            self.addChildWidget(widget)
            self._item = QSingleWidgetItem(widget)
            widget.show()
            self.invalidate()

    def addWidget(self, widget):
        """ Overridden parent class method. This method redirects to the
        `setWidget` method. User code should call `setWidget` instead.

        """
        import warnings
        msg = ('`QSingleWidgetLayout.addWidget`: use the '
               '`QSingleWidgetLayout.setWidget` method instead.')
        warnings.warn(msg)
        self.setWidget(widget)

    def addItem(self, item):
        """ A virtual method implementation which sets the layout item
        in the layout. The old item will be overridden.

        This method should not be used. The method `setWidget` should be
        used instead.

        """
        msg = 'Use `setWidget` instead.'
        raise NotImplementedError(msg)

    def count(self):
        """ A virtual method implementation which returns 0 if no layout
        item is supplied, or 1 if there is a current layout item.

        """
        return 0 if self._item is None else 1

    def itemAt(self, idx):
        """ A virtual method implementation which returns the layout item
        for the given index or None if one does not exist.

        """
        if idx == 0:
            return self._item

    def takeAt(self, idx):
        """ A virtual method implementation which removes and returns the
        item at the given index or None if one does not exist.

        """
        if idx == 0:
            item = self._item
            self._item = None
            if item is not None:
                item.widget().hide()
                self.invalidate()
            # The creation path of the layout item bypasses the virtual
            # wrapper methods, this means that the ownership of the cpp
            # pointer is never transferred to Qt. If the item is returned
            # here it will be deleted by Qt, which doesn't own the pointer.
            # A double free occurs once the Python item falls out of scope.
            # To avoid this, this method always returns None and the item
            # cleanup is performed by Python, which owns the cpp pointer.

    def sizeHint(self):
        """ A virtual method implementation which returns the size hint
        for the layout.

        """
        item = self._item
        if item is not None:
            hint = item.sizeHint()
            left, top, right, bottom = self.getContentsMargins()
            hint.setHeight(hint.height() + top + bottom)
            hint.setWidth(hint.width() + left + right)
            return hint
        return QSize()

    def setGeometry(self, rect):
        """ A reimplemented method which sets the geometry of the managed
        widget to fill the given rect.

        """
        super(QSingleWidgetLayout, self).setGeometry(rect)
        item = self._item
        if item is not None:
            item.setGeometry(self.contentsRect())

    def minimumSize(self):
        """ A reimplemented method which returns the minimum size hint
        of the layout item widget as the minimum size of the window.

        """
        item = self._item
        if item is not None:
            s = item.minimumSize()
            left, top, right, bottom = self.getContentsMargins()
            s.setHeight(s.height() + top + bottom)
            s.setWidth(s.width() + left + right)
            return s
        return super(QSingleWidgetLayout, self).minimumSize()

    def maximumSize(self):
        """ A reimplemented method which returns the maximum size hint
        of the layout item widget as the maximum size of the window.

        """
        item = self._item
        if item is not None:
            s = item.maximumSize()
            left, top, right, bottom = self.getContentsMargins()
            s.setHeight(s.height() + top + bottom)
            s.setWidth(s.width() + left + right)
            return s
        return super(QSingleWidgetLayout, self).maximumSize()
