#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Enum, Bool, Typed, ForwardTyped, Unicode, observe, set_default
)

from enaml.core.declarative import d_

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .page import Page


class ProxyNotebook(ProxyConstraintsWidget):
    """ The abstract definition of a proxy Notebook object.

    """
    #: A reference to the Notebook declaration.
    declaration = ForwardTyped(lambda: Notebook)

    def set_tab_style(self, style):
        raise NotImplementedError

    def set_tab_position(self, position):
        raise NotImplementedError

    def set_tabs_closable(self, closable):
        raise NotImplementedError

    def set_tabs_movable(self, movable):
        raise NotImplementedError

    def set_selected_tab(self, name):
        raise NotImplementedError

    def set_size_hint_mode(self, mode):
        raise NotImplementedError


class Notebook(ConstraintsWidget):
    """ A component which displays its children as tabbed pages.

    """
    #: The style of tabs to use in the notebook. Preferences style
    #: tabs are appropriate for configuration dialogs and the like.
    #: Document style tabs are appropriate for multi-page editing
    #: in code editors and the like.
    tab_style = d_(Enum('document', 'preferences'))

    #: The position of tabs in the notebook.
    tab_position = d_(Enum('top', 'bottom', 'left', 'right'))

    #: Whether or not the tabs in the notebook should be closable.
    tabs_closable = d_(Bool(True))

    #: Whether or not the tabs in the notebook should be movable.
    tabs_movable = d_(Bool(True))

    #: The object name for the selected tab in the notebook.
    selected_tab = d_(Unicode())

    #: The size hint mode for the stack. The default is 'union' and
    #: means that the size hint of the notebook is the union of all
    #: the tab size hints. 'current' means the size hint of the
    #: notebook will be the size hint of the current tab.
    size_hint_mode = d_(Enum('union', 'current'))

    #: A notebook expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyNotebook object.
    proxy = Typed(ProxyNotebook)

    def pages(self):
        """ Get the Page children defined on the notebook.

        """
        return [c for c in self.children if isinstance(c, Page)]

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('tab_style', 'tab_position', 'tabs_closable', 'tabs_movable',
        'selected_tab', 'size_hint_mode')
    def _update_proxy(self, change):
        """ Send the state change to the proxy.

        """
        # The superclass implementation is sufficient.
        super(Notebook, self)._update_proxy(change)
