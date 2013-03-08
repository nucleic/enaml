#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .editor.qt_ace_editor_view import QtAceEditorView
from .qt_control import QtControl


class QtTextEditor(QtControl):
    """ A Qt4 implementation of an Enaml TextEditor.

    """
    def create(self):
        """ Create the underlying widget.

        """
        self.widget = QtAceEditorView(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(QtTextEditor, self).initialize(attrs)
        self.attrs = attrs
        self.widget.loadFinished.connect(self.on_load)

    def on_load(self):
        """ The attributes have to be set after the webview
        has finished loading, so this function is delayed

        """
        self.set_text(self.attrs['text'])
        self.set_theme(self.attrs['theme'])
        self.set_mode(self.attrs['mode'])
        self.set_auto_pair(self.attrs['auto_pair'])
        self.set_font_size(self.attrs['font_size'])
        self.show_margin_line(self.attrs['margin_line'])
        self.set_margin_line_column(self.attrs['margin_line_column'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_text(self, payload):
        """ Handle the 'set-text' action from the Enaml widget.

        """
        self.set_text(payload['text'])

    def on_message_set_theme(self, payload):
        """ Handle the 'set-theme' action from the Enaml widget.

        """
        self.set_theme(payload['theme'])

    def on_message_set_mode(self, payload):
        """ Handle the 'set-mode' action from the Enaml widget.

        """
        self.set_mode(payload['mode'])

    def on_message_set_auto_pair(self, payload):
        """ Handle the 'set-auto_pair' action from the Enaml widget.

        """
        self.set_auto_pair(payload['auto_pair'])

    def on_message_set_font_size(self, payload):
        """ Handle the 'set-font_size' action from the Enaml widget.

        """
        self.set_font_size(payload['font_size'])

    def on_message_show_margin_line(self, payload):
        """ Handle the 'show-margin_line' action from the Enaml widget.

        """
        self.show_margin_line(payload['margin_line'])

    def on_message_set_margin_line_column(self, payload):
        """ Handle the 'set-margin_line_column' action from the Enaml widget.

        """
        self.set_margin_line_column(payload['margin_line_column'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        self.widget.editor().set_text(text)

    def set_theme(self, theme):
        """ Set the theme of the underlying editor.

        """
        self.widget.editor().set_theme(theme)

    def set_mode(self, mode):
        """ Set the mode of the underlying editor.

        """
        self.widget.editor().set_mode(mode)

    def set_auto_pair(self, auto_pair):
        """ Set whether or not to pair parentheses, braces, etc in the editor

        """
        self.widget.editor().set_auto_pair(auto_pair)

    def set_font_size(self, font_size):
        """ Set the font size of the editor

        """
        self.widget.editor().set_font_size(font_size)

    def show_margin_line(self, margin_line):
        """ Set whether or not to display the margin line in the editor

        """
        self.widget.editor().show_margin_line(margin_line)

    def set_margin_line_column(self, margin_line_col):
        """ Set the column number for the margin line

        """
        self.widget.editor().set_margin_line_column(margin_line_col)
