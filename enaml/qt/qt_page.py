#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import logging

from .qt.QtCore import Signal
from .qt.QtGui import QFrame, QIcon, QImage, QPixmap
from .q_single_widget_layout import QSingleWidgetLayout
from .qt_container import QtContainer
from .qt_widget import QtWidget


logger = logging.getLogger(__name__)


class QPage(QFrame):
    """ A QFrame subclass which acts as a page in a QNotebook.

    """
    #: A signal emitted when the page has been closed by the user.
    pageClosed = Signal()

    def __init__(self, *args, **kwargs):
        """ Initialize a QPage.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a QWidget.

        """
        super(QPage, self).__init__(*args, **kwargs)
        self._title = u''
        self._tool_tip = u''
        self._icon = QIcon()
        self._closable = True
        self._is_enabled = True
        self._is_open = True
        self._page_widget = None
        self.setLayout(QSingleWidgetLayout())

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _findNotebook(self):
        """ Get the parent QNotebook for this page.

        Returns
        -------
        result : QNotebook or None
            The parent QNotebook for this page, or None if one cannot
            be found.

        """
        # Avoid a circular import with the qt_notebook module
        from .qt_notebook import QNotebook
        # Depending on where we are during initialization, the notebook
        # will be either our parent or grandparent because of how the
        # QTabWidget reparents things internally.
        parent = self.parent()
        if isinstance(parent, QNotebook):
            return parent
        if parent is not None:
            parent = parent.parent()
            if isinstance(parent, QNotebook):
                return parent

    def _pageIndexOperation(self, closure):
        """ A private method which will run the given closure if there
        is a valid index for this page.

        """
        notebook = self._findNotebook()
        if notebook is not None:
            index = notebook.indexOf(self)
            if index != -1:
                closure(notebook, index)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def requestClose(self):
        """ A method called by the parent notebook when the user has
        requested that this page be closed.

        If the page is marked as closable, then it will be closed and
        the 'pageClosed' signal will be emitted.

        """
        if self.isClosable():
            self.close()
            self.pageClosed.emit()

    def pageWidget(self):
        """ Get the page widget for this page.

        Returns
        -------
        result : QWidget or None
            The page widget being managed by this page.

        """
        return self._page_widget

    def setPageWidget(self, widget):
        """ Set the page widget for this page.

        Parameters
        ----------
        widget : QWudget
            The Qt widget to use as the page widget in this page.

        """
        self._page_widget = widget
        self.layout().setWidget(widget)

    def isOpen(self):
        """ Get whether or not the page is open.

        Returns
        -------
        result : bool
            True if the page is open, False otherwise.

        """
        return self._is_open

    def open(self):
        """ Open the page in the notebook.

        """
        self._is_open = True
        notebook = self._findNotebook()
        if notebook is not None:
            notebook.showPage(self)

    def close(self):
        """ Close the page in the notebook.

        """
        self._is_open = False
        notebook = self._findNotebook()
        if notebook is not None:
            notebook.hidePage(self)

    def isTabEnabled(self):
        """ Return whether or not the tab for this page is enabled.

        This method should be used in favor of isEnabled.

        Returns
        -------
        result : bool
            True if the tab for this page is enabled, False otherwise.

        """
        return self._is_enabled

    def setTabEnabled(self, enabled):
        """ Set whether the tab for this page is enabled.

        This method should be used in favor of isEnabled.

        Parameters
        ----------
        enabled : bool
            True if the tab should be enabled, False otherwise.

        """
        self._is_enabled = enabled
        def closure(nb, index):
            nb.setTabEnabled(index, enabled)
        self._pageIndexOperation(closure)

    def title(self):
        """ Returns the tab title for this page.

        Returns
        -------
        result : unicode
            The title string for the page's tab.

        """
        return self._title

    def setTitle(self, title):
        """ Set the title for the tab for this page.

        Parameters
        ----------
        title : unicode
            The string to use for this page's tab title.

        """
        self._title = title
        def closure(nb, index):
            nb.setTabText(index, title)
        self._pageIndexOperation(closure)

    def isClosable(self):
        """ Returns whether or not the tab for this page is closable.

        Returns
        -------
        result : bool
            True if this page's tab is closable, False otherwise.

        """
        return self._closable

    def setClosable(self, closable):
        """ Set whether the tab for this page is closable.

        Parameters
        ----------
        closable : bool
            True if the tab should be closable, False otherwise.

        """
        self._closable = closable
        def closure(nb, index):
            nb.setTabCloseButtonVisible(index, closable)
        self._pageIndexOperation(closure)

    def toolTip(self):
        """ Returns the tool tip for the tab for this page.

        Returns
        -------
        result : unicode
            The tool tip string for the page's tab.

        """
        return self._tool_tip

    def setToolTip(self, tool_tip):
        """ Set the tool tip for the tab for this page.

        This overrides the default implementation to set the tool tip
        on the notebook tab.

        Parameters
        ----------
        title : unicode
            The string to use for this page's tab tool tip.

        """
        self._tool_tip = tool_tip
        def closure(nb, index):
            nb.setTabToolTip(index, tool_tip)
        self._pageIndexOperation(closure)

    def icon(self):
        """ Get the icon for the page.

        Returns
        -------
        result : QIcon
            The icon for the page.

        """
        return self._icon

    def setIcon(self, icon):
        """ Set the icon for the page.

        Parameters
        ----------
        icon : QIcon
            The icon for the page.

        """
        self._icon = icon
        def closure(nb, index):
            nb.setTabIcon(index, icon)
        self._pageIndexOperation(closure)


class QtPage(QtWidget):
    """ A Qt implementation of an Enaml notebook Page.

    """
    #: Temporary internal storage for the icon source url.
    _icon_source = ''

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying page widget.

        """
        return QPage(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtPage, self).create(tree)
        self.set_title(tree['title'])
        self.set_closable(tree['closable'])
        self._icon_source = tree['icon_source']
        self.widget().pageClosed.connect(self.on_page_closed)

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(QtPage, self).init_layout()
        self.widget().setPageWidget(self.page_widget())

    def activate(self):
        """ Activate the page widget.

        """
        self.set_icon_source(self._icon_source)
        super(QtPage, self).activate()

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def page_widget(self):
        """ Find and return the page widget child for this widget.

        Returns
        -------
        result : QWidget or None
            The page widget defined for this widget, or None if one is
            not defined.

        """
        widget = None
        for child in self.children():
            if isinstance(child, QtContainer):
                widget = child.widget()
        return widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtPage.

        """
        if isinstance(child, QtContainer):
            self.widget().setPageWidget(self.page_widget())

    def child_added(self, child):
        """ Handle the child added event for a QtPage.

        """
        if isinstance(child, QtContainer):
            self.widget().setPageWidget(self.page_widget())

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_page_closed(self):
        """ The signal handler for the 'pageClosed' signal.

        """
        self.send_action('closed', {})

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    def on_action_set_closable(self, content):
        """ Handle the 'set_closable' action from the Enaml widget.

        """
        self.set_closable(content['closable'])

    def on_action_set_icon_source(self, content):
        """ Handle the 'set_icon_source' action from the Enaml widget.

        """
        self.set_icon_source(content['icon_source'])

    def on_action_open(self, content):
        """ Handle the 'open' action from the Enaml widget.

        """
        self.widget().open()

    def on_action_close(self, content):
        """ Handle the 'close' action from the Enaml widget.

        """
        self.widget().close()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ An overridden visibility setter which to opens|closes the
        notebook page.

        """
        widget = self.widget()
        if visible:
            widget.open()
        else:
            widget.close()

    def set_enabled(self, enabled):
        """ An overridden enabled setter which sets the tab enabled
        state.

        """
        self.widget().setTabEnabled(enabled)

    def set_title(self, title):
        """ Set the title of the tab for this page.

        """
        self.widget().setTitle(title)

    def set_closable(self, closable):
        """ Set whether or not this page is closable.

        """
        self.widget().setClosable(closable)

    def set_icon_source(self, icon_source):
        """ Sets the widget's icon to the provided image.

        """
        if icon_source:
            loader = self._session.load_resource(icon_source)
            loader.on_load(self._on_icon_load)
        else:
            self._on_icon_load(QIcon())

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_icon_load(self, icon):
        """ A private resource loader callback.

        This method is invoked when the requested icon is successfully
        loaded. It will update the icon on the page widget.

        Parameters
        ----------
        icon : QIcon or QImage
            The icon or image that was loaded by the request.

        """
        if isinstance(icon, QImage):
            icon = QIcon(QPixmap.fromImage(icon))
        elif not isinstance(icon, QIcon):
            msg = 'got incorrect type for icon: `%s`'
            logger.error(msg % type(icon).__name__)
            icon = QIcon()
        self.widget().setIcon(icon)

