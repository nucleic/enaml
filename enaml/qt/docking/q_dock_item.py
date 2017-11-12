#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from future.builtins import str
from enaml.qt.QtCore import Qt, QRect, QSize, QPoint, QTimer, Signal
from enaml.qt.QtWidgets import QApplication, QFrame, QLayout

from .event_types import (
    QDockItemEvent, DockItemShown, DockItemHidden, DockItemClosed
)
from .q_dock_tab_widget import QDockTabWidget
from .q_dock_title_bar import QDockTitleBar
from .utils import repolish


class _AlertData(object):
    """ A private class which stores the data needed for item alerts.

    """
    def __init__(self, timer, level, on, off, repeat, persist):
        self.timer = timer
        self.level = level
        self.on = on
        self.off = off
        self.repeat = repeat
        self.persist = persist
        self.remaining = repeat
        self.active = False


class QDockItemLayout(QLayout):
    """ A QLayout subclass for laying out a dock item.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockAreaLayout.

        Parameters
        ----------
        parent : QWidget or None
            The parent widget owner of the layout.

        """
        super(QDockItemLayout, self).__init__(parent)
        self._size_hint = QSize()
        self._min_size = QSize()
        self._max_size = QSize()
        self._title_bar = None
        self._dock_widget = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def titleBarWidget(self):
        """ Get the title bar widget set for the layout.

        Returns
        -------
        result : IDockItemTitleBar or None
            The title bar widget for the layout, or None if no widget
            is applied.

        """
        return self._title_bar

    def setTitleBarWidget(self, title_bar):
        """ Set the title bar widget for the layout.

        The old widget will be hidden and unparented, but not destroyed.

        Parameters
        ----------
        title_bar : IDockItemTitleBar or None
            A concrete implementor of the title bar interface, or None.

        """
        old_bar = self._title_bar
        if old_bar is not None:
            old_bar.hide()
            old_bar.setParent(None)
        self._title_bar = title_bar
        if title_bar is not None:
            title_bar.setParent(self.parentWidget())
        self.invalidate()

    def dockWidget(self):
        """ Get the dock widget set for the layout.

        Returns
        -------
        result : QWidget
            The primary widget set in the dock item layout.

        """
        return self._dock_widget

    def setDockWidget(self, widget):
        """ Set the dock widget for the layout.

        The old widget will be hidden and unparented, but not destroyed.

        Parameters
        ----------
        widget : QWidget
            The widget to use as the primary content in the layout.

        """
        old_widget = self._dock_widget
        if widget is old_widget:
            return
        if old_widget is not None:
            old_widget.hide()
            old_widget.setParent(None)
        self._dock_widget = widget
        if widget is not None:
            widget.setParent(self.parentWidget())
        self.invalidate()

    #--------------------------------------------------------------------------
    # QLayout API
    #--------------------------------------------------------------------------
    def invalidate(self):
        """ Invalidate the layout.

        """
        super(QDockItemLayout, self).invalidate()
        self._size_hint = QSize()
        self._min_size = QSize()
        self._max_size = QSize()

    def setGeometry(self, rect):
        """ Set the geometry for the items in the layout.

        """
        super(QDockItemLayout, self).setGeometry(rect)
        title = self._title_bar
        widget = self._dock_widget
        title_rect = QRect(rect)
        widget_rect = QRect(rect)
        if title is not None and not title.isHidden():
            msh = title.minimumSizeHint()
            title_rect.setHeight(msh.height())
            widget_rect.setTop(title_rect.bottom() + 1)
            title.setGeometry(title_rect)
        if widget is not None and not widget.isHidden():
            widget.setGeometry(widget_rect)

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        sh = self._size_hint
        if not sh.isValid():
            width = height = 0
            title = self._title_bar
            widget = self._dock_widget
            if title is not None and not title.isHidden():
                hint = title.sizeHint()
                width += hint.width()
                height += hint.height()
            if widget is not None and not widget.isHidden():
                hint = widget.sizeHint()
                width = max(width, hint.width())
                height += hint.height()
            sh = self._size_hint = QSize(width, height)
        return sh

    def minimumSize(self):
        """ Get the minimum size for the layout.

        """
        ms = self._min_size
        if not ms.isValid():
            width = height = 0
            title = self._title_bar
            widget = self._dock_widget
            if title is not None and not title.isHidden():
                hint = title.minimumSizeHint()
                width += hint.width()
                height += hint.height()
            if widget is not None and not widget.isHidden():
                hint = widget.minimumSizeHint()
                width = max(width, hint.width())
                height += hint.height()
            ms = self._min_size = QSize(width, height)
        return ms

    def maximumSize(self):
        """ Get the maximum size for the layout.

        """
        ms = self._max_size
        if not ms.isValid():
            widget = self._dock_widget
            parent = self.parentWidget()
            if widget is not None and parent.isFloating():
                ms = widget.maximumSize()
                title = self._title_bar
                if title is not None and not title.isHidden():
                    height = ms.height() + title.minimumSizeHint().height()
                    ms.setHeight(min(16777215, height))
            else:
                ms = QSize(16777215, 16777215)
            self._max_size = ms
        return ms

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        """
        msg = 'Use `setTitleBarWidget | setDockWidget` instead.'
        raise NotImplementedError(msg)

    def count(self):
        """ A required virtual method implementation.

        This method should not be used and returns a constant value.

        """
        return 0

    def itemAt(self, idx):
        """ A virtual method implementation which returns None.

        """
        return None

    def takeAt(self, idx):
        """ A virtual method implementation which does nothing.

        """
        return None


class QDockItem(QFrame):
    """ A QFrame subclass which acts as an item QDockArea.

    """
    #: A signal emitted when the maximize button is clicked. This
    #: signal is proxied from the current dock item title bar.
    maximizeButtonClicked = Signal(bool)

    #: A signal emitted when the restore button is clicked. This
    #: signal is proxied from the current dock item title bar.
    restoreButtonClicked = Signal(bool)

    #: A signal emitted when the close button is clicked. This
    #: signal is proxied from the current dock item title bar.
    closeButtonClicked = Signal(bool)

    #: A signal emitted when the link button is toggled. This
    #: signal is proxied from the current dock item title bar.
    linkButtonToggled = Signal(bool)

    #: A signal emitted when the pin button is toggled. This
    #: signal is proxied from the current dock item title bar.
    pinButtonToggled = Signal(bool)

    #: A signal emitted when the title is edited by the user. This
    #: signal is proxied from the current dock item title bar.
    titleEdited = Signal(str)

    #: A signal emitted when the empty area is left double clicked.
    #: This signal is proxied from the current dock item title bar.
    titleBarLeftDoubleClicked = Signal(QPoint)

    #: A signal emitted when the empty area is right clicked. This
    #: signal is proxied from the current dock item title bar.
    titleBarRightClicked = Signal(QPoint)

    #: A signal emitted when the item is alerted. The payload is the
    #: new alert level. An empty string indicates no alert.
    alerted = Signal(str)

    def __init__(self, parent=None):
        """ Initialize a QDockItem.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the dock item.

        """
        super(QDockItem, self).__init__(parent)
        layout = QDockItemLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self.setTitleBarWidget(QDockTitleBar())
        self.alerted.connect(self._onAlerted)
        self._manager = None  # Set and cleared by the DockManager
        self._alert_data = None
        self._vis_changed = None
        self._closable = True
        self._closing = False

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def close(self):
        """ Handle the close request for the dock item.

        """
        self._closing = True
        try:
            super(QDockItem, self).close()
        finally:
            self._closing = False

    def closeEvent(self, event):
        """ Handle the close event for the dock item.

        This handler will reject the event if the item is not closable.

        """
        event.ignore()
        if self._closable:
            event.accept()
            area = self.rootDockArea()
            if area is not None and area.dockEventsEnabled():
                event = QDockItemEvent(DockItemClosed, self.objectName())
                QApplication.postEvent(area, event)

    def showEvent(self, event):
        """ Handle the show event for the container.

        This handler posts a visibility change event.

        """
        super(QDockItem, self).showEvent(event)
        self._postVisibilityChange(True)

    def hideEvent(self, event):
        """ Handle the hide event for the container.

        This handler posts a visibility change event.

        """
        super(QDockItem, self).hideEvent(event)
        # Don't post when closing; A closed event is posted instead.
        if not self._closing:
            self._postVisibilityChange(False)

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the dock item.

        This handler will clear any alert level on a left click.

        """
        if event.button() == Qt.LeftButton:
            self.clearAlert()
        super(QDockItem, self).mousePressEvent(event)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def manager(self):
        """ Get the dock manager for this dock item.

        Returns
        -------
        result : DockManager or None
            The dock manager which is managing this item.

        """
        return self._manager

    def rootDockArea(self):
        """ Get the root dock area for this dock item.

        Returns
        -------
        result : QDockArea or None
            The root dock area for this dock item.

        """
        manager = self._manager
        if manager is not None:
            return manager.dock_area()

    def title(self):
        """ Get the title for the dock item.

        Returns
        -------
        result : unicode
            The unicode title for the dock item.

        """
        return self.titleBarWidget().title()

    def setTitle(self, title):
        """ Set the title for the dock item.

        Parameters
        ----------
        title : unicode
            The unicode title to use for the dock item.

        """
        self.titleBarWidget().setTitle(title)
        # A concession to practicality: walk the ancestry and update
        # the tab title if this item lives in a dock tab.
        container = self.parent()
        if container is not None:
            stacked = container.parent()
            if stacked is not None:
                tabs = stacked.parent()
                if isinstance(tabs, QDockTabWidget):
                    index = tabs.indexOf(container)
                    tabs.setTabText(index, title)

    def icon(self):
        """ Get the icon for the dock item.

        Returns
        -------
        result : QIcon
            The icon in use for the dock item.

        """
        return self.titleBarWidget().icon()

    def setIcon(self, icon):
        """ Set the icon for the dock item.

        Parameters
        ----------
        icon : QIcon
            The icon to use for the dock item.

        """
        self.titleBarWidget().setIcon(icon)
        # A concession to practicality: walk the ancestry and update
        # the tab icon if this item lives in a dock tab.
        container = self.parent()
        if container is not None:
            stacked = container.parent()
            if stacked is not None:
                tabs = stacked.parent()
                if isinstance(tabs, QDockTabWidget):
                    index = tabs.indexOf(container)
                    tabs.setTabIcon(index, icon)

    def iconSize(self):
        """ Get the icon size for the title bar.

        Returns
        -------
        result : QSize
            The size to use for the icons in the title bar.

        """
        return self.titleBarWidget().iconSize()

    def setIconSize(self, size):
        """ Set the icon size for the title bar.

        Parameters
        ----------
        icon : QSize
            The icon size to use for the title bar. Icons smaller than
            this size will not be scaled up.

        """
        self.titleBarWidget().setIconSize(size)

    def isLinked(self):
        """ Get whether or not this dock item is linked.

        Returns
        -------
        result : bool
            True if the item is linked, False otherwise.

        """
        return self.titleBarWidget().isLinked()

    def setLinked(self, linked):
        """ Set whether or not the dock item is linked.

        Parameters
        ----------
        linked : bool
            True if the dock item should be linked, False otherwise.

        """
        self.titleBarWidget().setLinked(linked)

    def isPinned(self):
        """ Get whether or not this dock item is pinned.

        Returns
        -------
        result : bool
            True if the item is pinned, False otherwise.

        """
        return self.titleBarWidget().isPinned()

    def setPinned(self, pinned, quiet=False):
        """ Set whether or not the dock item is pinned.

        Parameters
        ----------
        pinned : bool
            True if the dock item should be pinned, False otherwise.

        quiet : bool, optional
            True if the state should be set without emitted the toggled
            signal. The default is False.

        """
        self.titleBarWidget().setPinned(pinned, quiet)

    def isFloating(self):
        """ Get whether the dock item is free floating.

        """
        container = self.parent()
        if container is not None:
            return container.isWindow()
        return self.isWindow()

    def titleEditable(self):
        """ Get whether the title is user editable.

        Returns
        -------
        result : bool
            True if the title is user editable, False otherwise.

        """
        return self.titleBarWidget().isEditable()

    def setTitleEditable(self, editable):
        """ Set whether or not the title is user editable.

        Parameters
        ----------
        editable : bool
            True if the title is user editable, False otherwise.

        """
        self.titleBarWidget().setEditable(editable)

    def titleBarForceHidden(self):
        """ Get whether or not the title bar is force hidden.

        Returns
        -------
        result : bool
            Whether or not the title bar is force hidden.

        """
        return self.titleBarWidget().isForceHidden()

    def setTitleBarForceHidden(self, hidden):
        """ Set the force hidden state of the title bar.

        Parameters
        ----------
        hidden : bool
            True if the title bar should be hidden, False otherwise.

        """
        self.titleBarWidget().setForceHidden(hidden)

    def closable(self):
        """ Get whether or not the dock item is closable.

        Returns
        -------
        result : bool
            True if the dock item is closable, False otherwise.

        """
        return self._closable

    def setClosable(self, closable):
        """ Set whether or not the dock item is closable.

        Parameters
        ----------
        closable : bool
            True if the dock item is closable, False otherwise.

        """
        if closable != self._closable:
            self._closable = closable
            bar = self.titleBarWidget()
            buttons = bar.buttons()
            if closable:
                buttons |= bar.CloseButton
            else:
                buttons &= ~bar.CloseButton
            bar.setButtons(buttons)
            # A concession to practicality: walk the ancestry and update
            # the tab close button if this item lives in a dock tab.
            container = self.parent()
            if container is not None:
                stacked = container.parent()
                if stacked is not None:
                    tabs = stacked.parent()
                    if isinstance(tabs, QDockTabWidget):
                        index = tabs.indexOf(container)
                        tabs.setCloseButtonVisible(index, closable)

    def titleBarWidget(self):
        """ Get the title bar widget for the dock item.

        If a custom title bar has not been assigned, a default title
        bar will be returned. To prevent showing a title bar, set the
        visibility on the returned title bar to False.

        Returns
        -------
        result : IDockItemTitleBar
            An implementation of IDockItemTitleBar. This will never be
            None.

        """
        layout = self.layout()
        bar = layout.titleBarWidget()
        if bar is None:
            bar = QDockTitleBar()
            self.setTitleBarWidget(bar)
        return bar

    def setTitleBarWidget(self, title_bar):
        """ Set the title bar widget for the dock item.

        Parameters
        ----------
        title_bar : IDockItemTitleBar or None
            A custom implementation of IDockItemTitleBar, or None. If
            None, then the default title bar will be restored.

        """
        layout = self.layout()
        old = layout.titleBarWidget()
        if old is not None:
            old.maximizeButtonClicked.disconnect(self.maximizeButtonClicked)
            old.restoreButtonClicked.disconnect(self.restoreButtonClicked)
            old.closeButtonClicked.disconnect(self.closeButtonClicked)
            old.linkButtonToggled.disconnect(self.linkButtonToggled)
            old.pinButtonToggled.disconnect(self.pinButtonToggled)
            old.titleEdited.disconnect(self.titleEdited)
            old.leftDoubleClicked.disconnect(self.titleBarLeftDoubleClicked)
            old.rightClicked.disconnect(self.titleBarRightClicked)
        title_bar = title_bar or QDockTitleBar()
        title_bar.maximizeButtonClicked.connect(self.maximizeButtonClicked)
        title_bar.restoreButtonClicked.connect(self.restoreButtonClicked)
        title_bar.closeButtonClicked.connect(self.closeButtonClicked)
        title_bar.linkButtonToggled.connect(self.linkButtonToggled)
        title_bar.pinButtonToggled.connect(self.pinButtonToggled)
        title_bar.titleEdited.connect(self.titleEdited)
        title_bar.leftDoubleClicked.connect(self.titleBarLeftDoubleClicked)
        title_bar.rightClicked.connect(self.titleBarRightClicked)
        layout.setTitleBarWidget(title_bar)

    def dockWidget(self):
        """ Get the dock widget for this dock item.

        Returns
        -------
        result : QWidget or None
            The dock widget being managed by this item.

        """
        return self.layout().dockWidget()

    def setDockWidget(self, widget):
        """ Set the dock widget for this dock item.

        Parameters
        ----------
        widget : QWidget
            The QWidget to use as the dock widget in this item.

        """
        self.layout().setDockWidget(widget)

    def alert(self, level, on=250, off=250, repeat=4, persist=False):
        """ Set the alert level on the dock item.

        This will override any currently applied alert level.

        Parameters
        ----------
        level : unicode
            The alert level token to apply to the dock item.

        on : int
            The duration of the 'on' cycle, in ms. A value of -1 means
            always on.

        off : int
            The duration of the 'off' cycle, in ms. If 'on' is -1, this
            value is ignored.

        repeat : int
            The number of times to repeat the on-off cycle. If 'on' is
            -1, this value is ignored.

        persist : bool
            Whether to leave the alert in the 'on' state when the cycles
            finish. If 'on' is -1, this value is ignored.

        """
        if self._alert_data is not None:
            self.clearAlert()
        app = QApplication.instance()
        app.focusChanged.connect(self._onAppFocusChanged)
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._onAlertTimer)
        on, off, repeat = max(-1, on), max(0, off), max(1, repeat)
        self._alert_data = _AlertData(timer, level, on, off, repeat, persist)
        if on < 0:
            self.alerted.emit(level)
        else:
            self._onAlertTimer()

    def clearAlert(self):
        """ Clear the current alert level, if any.

        """
        if self._alert_data is not None:
            self._alert_data.timer.stop()
            self._alert_data = None
            app = QApplication.instance()
            app.focusChanged.disconnect(self._onAppFocusChanged)
            self.alerted.emit(u'')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onAlertTimer(self):
        """ Handle the alert data timer timeout.

        This handler will refresh the alert level for the current tick,
        or clear|persist the alert level if the ticks have expired.

        """
        data = self._alert_data
        if data is not None:
            if not data.active:
                data.active = True
                data.timer.start(data.on)
                self.alerted.emit(data.level)
            else:
                data.active = False
                data.remaining -= 1
                if data.remaining > 0:
                    data.timer.start(data.off)
                    self.alerted.emit(u'')
                elif data.persist:
                    data.timer.stop()
                    self.alerted.emit(data.level)
                else:
                    self.clearAlert()

    def _onAlerted(self, level):
        """ A signal handler for the 'alerted' signal.

        This handler will set the 'alert' dynamic property on the
        dock item, the title bar, and the title bar label, and then
        repolish all three items.

        """
        level = level or None
        title_bar = self.titleBarWidget()
        label = title_bar.label()
        self.setProperty(u'alert', level)
        title_bar.setProperty(u'alert', level)
        label.setProperty(u'alert', level)
        repolish(label)
        repolish(title_bar)
        repolish(self)

    def _onAppFocusChanged(self, old, new):
        """ A signal handler for the 'focusChanged' app signal

        This handler will clear the alert if one of the descendant
        widgets or the item itself gains focus.

        """
        while new is not None:
            if new is self:
                self.clearAlert()
                break
            new = new.parent()

    def _onVisibilityTimer(self):
        """ Handle the visibility timer timeout.

        This handler will post the dock item visibility event to the
        root dock area.

        """
        area = self.rootDockArea()
        if area is not None and area.dockEventsEnabled():
            timer, visible = self._vis_changed
            evt_type = DockItemShown if visible else DockItemHidden
            event = QDockItemEvent(evt_type, self.objectName())
            QApplication.postEvent(area, event)
            self._vis_changed = None

    def _postVisibilityChange(self, visible):
        """ Post a visibility changed event for the dock item.

        This method collapses the post on a timer and will not emit
        the event when the visibility temporarily toggles bettwen
        states.

        Parameters
        ----------
        visible : bool
            True if the item was show, False if the item was hidden.

        """
        area = self.rootDockArea()
        if area is not None and area.dockEventsEnabled():
            vis_changed = self._vis_changed
            if vis_changed is None:
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(self._onVisibilityTimer)
                self._vis_changed = (timer, visible)
                timer.start()
            else:
                timer, old_visible = vis_changed
                if old_visible != visible:
                    self._vis_changed = None
                    timer.stop()
