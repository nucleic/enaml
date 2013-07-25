#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import uuid

from atom.api import (
    Atom, Int, Constant, Enum, Event, Typed, ForwardTyped, Str, observe,
    set_default
)

from enaml.core.declarative import d_

from .control import Control, ProxyControl


#: The syntax definitions available for syntax highlighting.
SYNTAX = (
    '',
    'bash',
    'batch',
    'cmake',
    'cpp',
    'css',
    'csharp',
    'd',
    'diff',
    'enaml',
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


class ScintillaDocument(Atom):
    """ An opaque class which represents a Scintilla text document.

    An instance of this class can be shared with multiple Scintilla
    widgets to enable multiple editing views on the same buffer.

    """
    #: A uuid which can be used as a handle by toolkit backends.
    uuid = Constant(factory=lambda: uuid.uuid4().hex)


class ProxyScintilla(ProxyControl):
    """ The abstract definition of a proxy Scintilla object.

    """
    #: A reference to the Label declaration.
    declaration = ForwardTyped(lambda: Scintilla)

    def set_syntax(self, syntax):
        raise NotImplementedError

    def set_theme(self, theme):
        raise NotImplementedError

    def set_zoom(self, zoom):
        raise NotImplementedError

    def set_document(self, document):
        raise NotImplementedError

    def get_text(self):
        raise NotImplementedError

    def set_text(self, text):
        raise NotImplementedError


class Scintilla(Control):
    """ A Scintilla text editing control.

    Notes
    -----
    The 'background', 'foreground', and 'font' attributes will only
    have an effect if a syntax definition is not in use. If a syntax
    definition is in use, the styling is supplied by the 'theme'. See
    the 'scintilla_theme.rst' file for information about how to write
    a syntax highlighting theme.

    """
    #: The syntax definition to apply to the text editor.
    syntax = d_(Enum(*SYNTAX))

    #: The syntax highlighting them to apply to the editor. This will
    #: only have an effect when a syntax definition is in use. See the
    #: 'scintilla_theme.rst' file for information about how to write a
    #: syntax highlighting theme.
    theme = d_(Str())

    #: The zoom factor for the editor. Values outside the range of
    #: -10 to 20 will be clipped to that range.
    zoom = d_(Int())

    #: The scintilla document buffer to use in the editor. A default
    #: document will be created automatically for each editor. This
    #: value only needs to be supplied when swapping buffers or when
    #: using a single buffer in multiple editors.
    document = d_(Typed(ScintillaDocument, ()))

    #: An event emitted when the text is changed.
    text_changed = d_(Event(), writable=False)

    #: An event emitted when the selection is changed.
    selection_changed = d_(Event(), writable=False)

    #: Text Editors expand freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyScintilla object.
    proxy = Typed(ProxyScintilla)

    #--------------------------------------------------------------------------
    # Post Validators
    #--------------------------------------------------------------------------
    def _post_validate_document(self, old, new):
        """ Post validate the text document.

        A new document is created when the existing document is set to
        None. This ensures that the proxy object never receives a null
        document and helps keep the state synchronized.

        """
        return new or ScintillaDocument()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('syntax', 'theme', 'zoom'))
    def _update_proxy(self, change):
        """ An observer which sends the document change to the proxy.

        """
        # The superclass implementation is sufficient.
        super(Scintilla, self)._update_proxy(change)

    @observe('document')
    def _refresh_document(self, change):
        """ An observer which sends the document change to the proxy.

        """
        # _update_proxy doesn't handle 'delete' changes; this does.
        if self.proxy_is_active:
            self.proxy.set_document(self.document)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def get_text(self):
        """ Get the text in the current document.

        Returns
        -------
        result : unicode
            The text in the current document.

        """
        if self.proxy_is_active:
            return self.proxy.get_text()
        return u''

    def set_text(self, text):
        """ Set the text in the current document.

        Parameters
        ----------
        text : unicode
            The text to apply to the current document.

        """
        if self.proxy_is_active:
            self.proxy.set_text(text)
