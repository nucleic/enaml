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


#: The available lexers for syntax highlighting.
LEXERS = (
    '',
    'bash',
    'batch',
    'cmake',
    'cpp',
    'csharp',
    'css',
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
    'pascal',
    'perl',
    'postscript',
    'pov',
    'python',
    'ruby',
    'spice',
    'sql',
    'tcl',
    'tex',
    'verilog',
    'vhdl',
    'xml',
    'yaml',
)


class ThemeLoader(Atom):
    """ A base class for defining theme loader objects.

    A theme loader is responsible for providing a JSON string which
    defines a Scintilla theme to the requestor.

    """
    def load(self):
        """ Load and return the theme to apply to the document.

        This method must be implemented by subclasses.

        Returns
        -------
        result : str
            A JSON string which defines the theme.

        """
        raise NotImplementedError


class StringThemeLoader(ThemeLoader):
    """ A theme loader for themes which already exist as strings.

    """
    #: The JSON string which defines the Scintilla theme.
    theme = Str()

    def load(self):
        """ Load and return the theme string.

        This method simply returns the 'theme' string.

        """
        return self.theme


class FileThemeLoader(ThemeLoader):
    """ A theme loader for themes which live on the filesystem.

    """
    #: The full path to the theme file.
    path = Str()

    def load(self):
        """ Load and return the theme string.

        This method loads and returns the data from the file.

        """
        with open(path, 'r') as f:
            data = f.read()
        return data


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
    
    def set_document(self, document):
        raise NotImplementedError

    def set_lexer(self, lexer):
        raise NotImplementedError

    def set_theme(self, theme):
        raise NotImplementedError

    def set_zoom(self, zoom):
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
    have an effect if a lexer is not applied to the editor. If a lexer
    is being used, the styling is supplied by the 'theme'. See the file
    'scintilla_theme.rst' for information about how to write a syntax 
    highlighting theme for the widget.

    """
    #: The scintilla document buffer to use in the editor. A default
    #: document will be created automatically for each editor. This
    #: value only needs to be supplied when swapping buffers or when
    #: using a single buffer in multiple editors.
    document = d_(Typed(ScintillaDocument, ()))

    #: The language lexer to apply to the document.
    lexer = d_(Enum(*LEXERS))

    #: The syntax highlighting theme to apply to the editor. This will
    #: only have an effect when a lexer is also applied. See the file
    #: 'scintilla_theme.rst' for information on how to write a theme.
    theme = d_(Typed(ThemeLoader))

    #: The zoom factor for the editor. Values will be clamped to the
    #: range -10 to 20.
    zoom = d_(Int())

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
    @observe(('lexer', 'theme', 'zoom'))
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
