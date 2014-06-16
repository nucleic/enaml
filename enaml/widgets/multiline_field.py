#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Typed, ForwardTyped, Unicode, observe, set_default

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyMultilineField(ProxyControl):
    """ The abstract definition of a proxy MultilineField object.

    """
    #: A reference to the MultilineField declaration.
    declaration = ForwardTyped(lambda: MultilineField)

    def set_text(self, text):
        raise NotImplementedError

    def set_read_only(self, read_only):
        raise NotImplementedError

    def set_auto_sync_text(self, sync):
        raise NotImplementedError

    def sync_text(self):
        raise NotImplementedError

    def field_text(self):
        raise NotImplementedError


class MultilineField(Control):
    """ A simple multiline editable text widget.

    """
    #: The unicode text to display in the field.
    text = d_(Unicode())

    #: Whether or not the field is read only.
    read_only = d_(Bool(False))

    #: Whether the text in the control should be auto-synchronized with
    #: the text attribute on the field. If this is True, the text will
    #: be updated every time the user edits the control. In order to be
    #: efficient, the toolkit will batch updates on a collapsing timer.
    auto_sync_text = d_(Bool(True))

    #: Multiline fields expand freely in width and height by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyMultilineField object.
    proxy = Typed(ProxyMultilineField)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('text', 'read_only', 'auto_sync_text')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(MultilineField, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def sync_text(self):
        """ Synchronize the text with the text in the control.

        """
        if self.proxy_is_active:
            self.proxy.sync_text()

    def field_text(self):
        """ Get the text stored in the field control.

        Depending on the state of the field, this text may be different
        than that stored in the 'text' attribute.

        Returns
        -------
        result : unicode
            The unicode text stored in the field.

        """
        if self.proxy_is_active:
            return self.proxy.field_text()
        return u''
