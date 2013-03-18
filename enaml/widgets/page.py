#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Unicode, Bool, Event, Typed, ForwardTyped, observe

from enaml.core.declarative import d_
from enaml.icon import Icon

from .container import Container
from .widget import Widget, ProxyWidget


class ProxyPage(ProxyWidget):
    """ The abstract definition for a proxy Page.

    """
    #: A reference to the Page declaration.
    declaration = ForwardTyped(lambda: Page)

    def set_title(self, title):
        raise NotImplementedError

    def set_icon(self, icon):
        raise NotImplementedError

    def set_closable(self, closable):
        raise NotImplementedError


class Page(Widget):
    """ A widget which can be used as a page in a Notebook control.

    A Page is a widget which can be used as a child of a Notebook
    control. It can have at most a single child widget which is an
    instance of Container.

    """
    #: The title to use for the page in the notebook.
    title = d_(Unicode())

    #: The icon to use for the page tab.
    icon = d_(Typed(Icon))

    #: Whether or not this individual page is closable. Note that the
    #: 'tabs_closable' flag on the parent Notebook must be set to True
    #: for this to have any effect.
    closable = d_(Bool(True))

    #: An event fired when the user closes the page by clicking on
    #: the tab's close button.
    closed = d_(Event(), writable=False)

    #: A reference to the ProxyPage object.
    proxy = Typed(ProxyPage)

    def page_widget(self):
        """ Get the page widget defined for the page.

        The last child Container is the page widget.

        """

        for child in reversed(self.children):
            if isinstance(child, Container):
                return child

    def open(self):
        """ Open the page in the Notebook.

        Calling this method will also set the page visibility to True.
        This method is deprectated, use 'show()' instead.

        """
        self.show()

    def close(self):
        """ Close the page in the Notebook.

        Calling this method will set the page visibility to False.
        This method is deprectated, use 'hide()' instead.

        """
        self.hide()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('title', 'closable', 'icon'))
    def _update_proxy(self, change):
        """ Send the member state change to the proxy.

        """
        # The superclass implementation is suffient
        super(Page, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _handle_close(self):
        """ A method called by the proxy when the user closes the page.

        """
        self.visible = False
        self.closed()
