#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Atom, Enum, Event, Typed, ForwardTyped, Value, observe, set_default
)

from enaml.core.declarative import d_

from .control import Control, ProxyControl


SYNTAX_DEFS = (
    '',
    'bash',
    'batch',
    'cmake',
    'cpp',
    'css',
    'csharp',
    'd',
    'diff',
    'fortran',
    'fortran77',
    'html',
    'idl',
    'java',
    'javascript',
    'lua',
    'makefile',
    'matlab',
    'octave',
    'pov',
    'pascal',
    'perl',
    'postscript',
    'python',
    'ruby',
    'sql',
    'spice',
    'tcl',
    'tex',
    'vhdl',
    'verilog',
    'xml',
    'yaml',
)


class TextDocument(Atom):
    """ An opaque class which represents a toolkit text document.

    The same instance of this class can be given to multiple TextEditor
    instances to allow simultaneous editing of the same text buffer.

    """
    #: Private storage for the toolkit document object.
    _tkdata = Value()


class ProxyTextEditor(ProxyControl):
    """ The abstract definition of a proxy TextEditor object.

    """
    #: A reference to the Label declaration.
    declaration = ForwardTyped(lambda: TextEditor)

    def set_document(self, document):
        raise NotImplementedError

    def set_syntax(self, syntax):
        raise NotImplementedError

    def get_text(self):
        raise NotImplementedError

    def set_text(self, text):
        raise NotImplementedError


class TextEditor(Control):
    """ A simple control for displaying read-only text.

    """
    #: An event emitted when the text is changed.
    text_changed = d_(Event(), writable=False)

    #: The text document to display in the text editor.
    document = d_(Typed(TextDocument, ()))

    #: The syntax definition to apply to the text editor.
    syntax = d_(Enum(*SYNTAX_DEFS))

    #: Text Editors expand freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyTextEditor object.
    proxy = Typed(ProxyTextEditor)

    #--------------------------------------------------------------------------
    # Post Validators
    #--------------------------------------------------------------------------
    def _post_validate_document(self, old, new):
        """ Post validate the text document.

        A text document cannot be None. If it is set to None, then a
        new TextDocument is created.

        """
        if new is None:
            new = TextDocument()
        return new

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('syntax'))
    def _update_proxy(self, change):
        """ An observer which sends the document change to the proxy.

        """
        # The superclass implementation is sufficient.
        super(TextEditor, self)._update_proxy(change)

    @observe('document')
    def _refresh_document(self, change):
        """ An observer which sends the document change to the proxy.

        """
        # _update_proxy doesn't handle deletion, this does.
        if self.proxy_is_active:
            self.proxy.set_document(self.document)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def get_text(self):
        """ Get the text in the current document.

        """
        if self.proxy_is_active:
            return self.proxy.get_text()
        return u''

    def set_text(self, text):
        """ Set the text in the current document.

        """
        if self.proxy_is_active:
            self.proxy.set_text(text)
