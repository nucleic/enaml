#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import uuid

from atom.api import (
    Atom, Int, Constant, Enum, Event, Typed, ForwardTyped, observe, set_default
)

from enaml.core.declarative import d_
from enaml.widgets.control import Control, ProxyControl


#: The available syntaxes for the Scintilla widget.
SYNTAXES = (
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


class ScintillaDocument(Atom):
    """ An opaque class which represents a Scintilla text document.

    An instance of this class can be shared with multiple Scintilla
    widgets to enable multiple editor views on the same buffer, or
    to use multiple buffers with the same view.

    """
    #: A uuid which can be used as a handle by the toolkit backend.
    uuid = Constant(factory=lambda: uuid.uuid4().hex)


class ProxyScintilla(ProxyControl):
    """ The abstract definition of a proxy Scintilla object.

    """
    #: A reference to the Scintilla declaration.
    declaration = ForwardTyped(lambda: Scintilla)

    def set_document(self, document):
        raise NotImplementedError

    def set_syntax(self, lexer):
        raise NotImplementedError

    def set_theme(self, theme):
        raise NotImplementedError

    def set_settings(self, settings):
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
    The 'background', 'foreground', and 'font' attributes have no effect
    on this widget. All styling is supplied via the 'theme' attribute.

    """
    #: The scintilla document buffer to use in the editor. A default
    #: document will be created automatically for each editor. This
    #: value only needs to be supplied when swapping buffers or when
    #: using a single buffer in multiple editors.
    document = d_(Typed(ScintillaDocument, ()))

    #: The language syntax to apply to the document.
    syntax = d_(Enum(*SYNTAXES))

    #: The theme to apply to the widget. See the './THEMES' document
    #: for how to create a theme dict for the widget.
    theme = d_(Typed(dict, ()))

    #: The settings to apply to the widget. See the './SETTINGS'
    #: document for how to create a settings dict for the widget.
    settings = d_(Typed(dict, ()))

    #: The zoom factor for the editor. The value is internally clamped
    #: to the range -10 to 20, inclusive.
    zoom = d_(Int())

    #: An event emitted when the text is changed.
    text_changed = d_(Event(), writable=False)

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

    def _post_validate_theme(self, old, new):
        """" Post validate the theme.

        The theme is reset to an empty dictionary if set to None.

        """
        return new or {}

    def _post_validate_settings(self, old, new):
        """" Post validate the settings.

        The settings are reset to an empty dictionary if set to None.

        """
        return new or {}

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('document', 'syntax', 'theme', 'settings', 'zoom')
    def _update_proxy(self, change):
        """ An observer which sends the document change to the proxy.

        """
        # The superclass implementation is sufficient.
        super(Scintilla, self)._update_proxy(change)

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
