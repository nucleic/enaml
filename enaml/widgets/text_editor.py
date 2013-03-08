#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Unicode, Bool, Int, observe, set_default

from enaml.core.declarative import d_

from .control import Control


class TextEditor(Control):
    """ A simple control for displaying read-only text.

    """
    #: The text for the text editor
    text = d_(Unicode(""))

    #: The editing mode for the editor
    mode = d_(Unicode("ace/mode/text"))

    #: The theme for the editor
    theme = d_(Unicode("ace/theme/textmate"))

    #: Auto pairs parentheses, braces, etc
    auto_pair = d_(Bool(True))

    #: The editor's font size
    font_size = d_(Int(12))

    #: Display the margin line
    margin_line = d_(Bool(True))

    #: The column number for the margin line
    margin_line_column = d_(Int(80))

    #: A text editor expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dict for the control.

        """
        snap = super(TextEditor, self).snapshot()
        snap['text'] = self.text
        snap['mode'] = self.mode
        snap['theme'] = self.theme
        snap['auto_pair'] = self.auto_pair
        snap['font_size'] = self.font_size
        snap['margin_line'] = self.margin_line
        snap['margin_line_column'] = self.margin_line_column
        return snap

    @observe(r'^(text|mode|theme|auto_pair|font_size|margin_line|'
             r'margin_line_column)$', regex=True)
    def send_member_change(self, change):
        """ An observe which sends the state change to the client.

        """
        # The superclass implementation is sufficient.
        super(TextEditor, self).send_member_change(change)

