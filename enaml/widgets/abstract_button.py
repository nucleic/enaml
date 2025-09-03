#------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, Str, Coerced, Event, Typed, ForwardTyped, set_default
)

from enaml.core.declarative import d_, observe
from enaml.icon import Icon
from enaml.layout.geometry import Size

from .control import Control, ProxyControl


def ButtonGroup():
    from .button_group import ButtonGroup
    return ButtonGroup


class ProxyAbstractButton(ProxyControl):
    """ The abstract definition of a proxy AbstractButton object.

    """
    #: A reference to the AbstractButton declaration.
    declaration = ForwardTyped(lambda: AbstractButton)

    def set_text(self, text):
        raise NotImplementedError

    def set_icon(self, icon):
        raise NotImplementedError

    def set_icon_size(self, size):
        raise NotImplementedError

    def set_group(self, group):
        raise NotImplementedError

    def set_checkable(self, checkable):
        raise NotImplementedError

    def set_checked(self, checked):
        raise NotImplementedError


class AbstractButton(Control):
    """ A base class for creating button-like controls.

    """
    #: The text to use as the button's label.
    text = d_(Str())

    #: The source url for the icon to use for the button.
    icon = d_(Typed(Icon))

    #: The size to use for the icon. The default is an invalid size
    #: and indicates that an appropriate default should be used.
    icon_size = d_(Coerced(Size, (-1, -1)))

    #: Group to which this button belongs to.
    group = d_(ForwardTyped(ButtonGroup))

    #: Whether or not the button is checkable. The default is False.
    checkable = d_(Bool(False))

    #: Whether a checkable button is currently checked.
    checked = d_(Bool(False))

    #: Fired when the button is pressed then released. The payload will
    #: be the current checked state. This event is triggered by the
    #: proxy object when the button is clicked.
    clicked = d_(Event(bool), writable=False)

    #: Fired when a checkable button is toggled. The payload will be
    #: the current checked state. This event is triggered by the
    #: proxy object when a togglable button is toggled.
    toggled = d_(Event(bool), writable=False)

    #: Buttons hug their contents' width weakly by default.
    hug_width = set_default('weak')

    #: A reference to the ProxyAbstractButton object.
    proxy = Typed(ProxyAbstractButton)

    def __init__(self, parent=None, **kwargs):
        super(AbstractButton, self).__init__(parent, **kwargs)
        # Overridden to synchronize the group_members member of the group
        if self.group:
            self.group.group_members.add(self)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('text', 'icon', 'icon_size', 'group', 'checkable', 'checked')
    def _update_proxy(self, change):
        """ An observer which updates the proxy widget.

        """
        # The superclass implementation is sufficient.
        super(AbstractButton, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Post Setattr Handlers
    #--------------------------------------------------------------------------
    def _post_setattr_group(self, old, new):
        """ Update the group_members of the group this button belongs too.

        """
        if old:
            old.group_members.remove(self)
        if new:
            new.group_members.add(self)
