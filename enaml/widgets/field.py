#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, Int, Unicode, Enum, List, Typed, ForwardTyped, observe, set_default
)

from enaml.core.declarative import d_
from enaml.validator import Validator

from .control import Control, ProxyControl


class ProxyField(ProxyControl):
    """ The abstract definition of a proxy Field object.

    """
    #: A reference to the Field declaration.
    declaration = ForwardTyped(lambda: Field)

    def set_text(self, text):
        raise NotImplementedError

    def set_mask(self, mask):
        raise NotImplementedError

    def set_submit_triggers(self, triggers):
        raise NotImplementedError

    def set_placeholder(self, placeholder):
        raise NotImplementedError

    def set_echo_mode(self, mode):
        raise NotImplementedError

    def set_max_length(self, length):
        raise NotImplementedError

    def set_read_only(self, read_only):
        raise NotImplementedError

    def set_text_align(self, text_align):
        raise NotImplementedError

    def field_text(self):
        raise NotImplementedError


class Field(Control):
    """ A single line editable text widget.

    """
    #: The unicode text to display in the field.
    text = d_(Unicode())

    #: The mask to use for text input:
    #:  http://qt-project.org/doc/qt-4.8/qlineedit.html#inputMask-prop
    #:
    #: The summary of the mask grammar is as follows:
    #: A   ASCII alphabetic character required. A-Z, a-z.
    #: a   ASCII alphabetic character permitted but not required.
    #: N   ASCII alphanumeric character required. A-Z, a-z, 0-9.
    #: n   ASCII alphanumeric character permitted but not required.
    #: X   Any character required.
    #: x   Any character permitted but not required.
    #: 9   ASCII digit required. 0-9.
    #: 0   ASCII digit permitted but not required.
    #: D   ASCII digit required. 1-9.
    #: d   ASCII digit permitted but not required (1-9).
    #: #   ASCII digit or plus/minus sign permitted but not required.
    #: H   Hexadecimal character required. A-F, a-f, 0-9.
    #: h   Hexadecimal character permitted but not required.
    #: B   Binary character required. 0-1.
    #: b   Binary character permitted but not required.
    #: >   All following alphabetic characters are uppercased.
    #: <   All following alphabetic characters are lowercased.
    #: !   Switch off case conversion.
    #: \   Use \ to escape the special characters listed above to use them as separators.
    #:
    #: The mask consists of a string of mask characters and separators, optionally
    #: followed by a semicolon and the character used for blanks
    #: Eg: 9 digit phone number: (999) 999-9999;_
    mask = d_(Unicode())

    #: The validator to use for this field. If the validator provides
    #: a client side validator, then text will only be submitted if it
    #: passes that validator.
    validator = d_(Typed(Validator))

    #: The list of actions which should cause the client to submit its
    #: text to the server for validation and update. The currently
    #: supported values are 'lost_focus', 'return_pressed', and 'auto_sync'.
    #: The 'auto_sync' mode will attempt to validate and synchronize the
    #: text when the user stops typing.
    submit_triggers = d_(List(
        Enum('lost_focus', 'return_pressed', 'auto_sync'),
        ['lost_focus', 'return_pressed']
    ))

    #: The grayed-out text to display if the field is empty and the
    #: widget doesn't have focus. Defaults to the empty string.
    placeholder = d_(Unicode())

    #: How to display the text in the field. Valid values are 'normal'
    #: which displays the text as normal, 'password' which displays the
    #: text with an obscured character, and 'silent' which displays no
    #: text at all but still allows input.
    echo_mode = d_(Enum('normal', 'password', 'silent'))

    #: The maximum length of the field in characters. The default value
    #: is Zero and indicates there is no maximum length.
    max_length = d_(Int(0))

    #: Whether or not the field is read only. Defaults to False.
    read_only = d_(Bool(False))

    #: Alignment for the text inside the field. Defaults to 'left'.
    text_align = d_(Enum('left', 'right', 'center'))

    #: How strongly a component hugs it's contents' width. Fields ignore
    #: the width hug by default, so they expand freely in width.
    hug_width = set_default('ignore')

    #: A reference to the ProxyField object.
    proxy = Typed(ProxyField)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('text', 'mask', 'submit_triggers', 'placeholder', 'echo_mode',
        'max_length', 'read_only', 'text_align')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass implementation is sufficient.
        super(Field, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
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
