#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, Int, Unicode, Enum, List, Instance, observe, set_default
)

from enaml.core.declarative import d_
from enaml.validation.validator import Validator

from .control import Control


class Field(Control):
    """ A single line editable text widget.

    """
    #: The unicode text to display in the field.
    text = d_(Unicode())

    #: The mask to use for text input.
    #: TODO - describe and implement this mask
    mask = d_(Unicode())

    #: The validator to use for this field. If the validator provides
    #: a client side validator, then text will only be submitted if it
    #: passes that validator.
    validator = d_(Instance(Validator))

    #: The list of actions which should cause the client to submit its
    #: text to the server for validation and update. The currently
    #: supported values are 'lost_focus' and 'return_pressed'.
    submit_triggers = d_(List(
        Enum('lost_focus', 'return_pressed'), ['lost_focus', 'return_pressed']
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

    #: How strongly a component hugs it's contents' width. Fields ignore
    #: the width hug by default, so they expand freely in width.
    hug_width = set_default('ignore')

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the field.

        """
        snap = super(Field, self).snapshot()
        snap['text'] = self.text
        snap['validator'] = self._client_validator()
        snap['submit_triggers'] = self.submit_triggers
        snap['placeholder'] = self.placeholder
        snap['echo_mode'] = self.echo_mode
        snap['max_length'] = self.max_length
        snap['read_only'] = self.read_only
        return snap

    @observe(r'^(text|placeholder|echo_mode|max_length|read_only|'
             r'submit_triggers)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(Field, self).send_member_change(change)

    @observe('validator')
    def send_validator_change(self, change):
        """ Send the new validator to the client widget.

        """
        content = {'validator': self._client_validator()}
        self.send_action('set_validator', content)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _client_validator(self):
        """ A private method which returns the current client validator.

        """
        v = self.validator
        return v.client_validator() if v is not None else None

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_submit_text(self, content):
        """ Handle the 'submit_text' action from the client widget.

        """
        edit_text = content['text']
        validator = self.validator
        if validator is not None:
            text, valid = validator.validate(edit_text, self)
        else:
            text, valid = edit_text, True
        if valid:
            # If the new text differs from the original edit text,
            # we push an update to the client.
            if text != edit_text:
                content = {'text': text}
                self.send_action('set_text', content)
            self.set_guarded(text=text)
        else:
            # notify the client that server validation failed.
            content = {'text': text}
            self.send_action('invalid_text', content)

