#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from . import QT_API
if QT_API != 'pyqt':
    msg = 'the Qt Scintilla widget is only available when using PyQt'
    raise ImportError(msg)

import logging
import sys
import weakref

from atom.api import Typed

from enaml.colors import parse_color
from enaml.fonts import parse_font
from enaml.scintilla.scintilla import ProxyScintilla

from PyQt4 import Qsci

from .QtGui import QColor, QFont

from .q_resource_helpers import QColor_from_Color, QFont_from_Font
from .qt_control import QtControl
from .scintilla_lexers import LEXERS, LEXERS_INV
from .scintilla_tokens import TOKENS


#: The module-level logger
logger = logging.getLogger(__name__)


Base = Qsci.QsciScintillaBase


if sys.platform == 'win32':
    DEFAULT_EOL = 'crlf'
elif sys.platform == 'darwin':
    DEFAULT_EOL = 'cr'
else:
    DEFAULT_EOL = 'lf'


EOL_MODE = {
    'crlf': Base.SC_EOL_CRLF,
    'cr': Base.SC_EOL_CR,
    'lf': Base.SC_EOL_LF,
}


EDGE_MODE = {
    'none': Base.EDGE_NONE,
    'line': Base.EDGE_LINE,
    'background': Base.EDGE_BACKGROUND,
}


INDENTATION_GUIDES = {
    'none': Base.SC_IV_NONE,
    'real': Base.SC_IV_REAL,
    'look_forward': Base.SC_IV_LOOKFORWARD,
    'look_both': Base.SC_IV_LOOKBOTH,
}


WHITE_SPACE = {
    'visible_always': Base.SCWS_VISIBLEALWAYS,
    'visible_after_indent': Base.SCWS_VISIBLEAFTERINDENT,
    'invisible': Base.SCWS_INVISIBLE,
}


def _make_color(color_str):
    """ A function which converts a color string into a QColor.

    """
    color = parse_color(color_str)
    if color is not None:
        return QColor_from_Color(color)
    return QColor()


def _make_font(font_str):
    """ A function which converts a font string into a QColor.

    """
    font = parse_font(font_str)
    if font is not None:
        return QFont_from_Font(font)
    return QFont()


class QtScintilla(QtControl, ProxyScintilla):
    """ A Qt implementation of an Enaml ProxyScintilla.

    """
    #: A weak cache which maps uuid -> QsciDocument.
    qsci_doc_cache = weakref.WeakValueDictionary()

    #: A reference to the widget created by the proxy.
    widget = Typed(Qsci.QsciScintilla)

    #: A strong reference to the QsciDocument handle.
    qsci_doc = Typed(Qsci.QsciDocument)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying label widget.

        """
        self.widget = Qsci.QsciScintilla(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtScintilla, self).init_widget()
        d = self.declaration
        self.set_document(d.document)
        self.set_syntax(d.syntax, refresh_style=False)
        self.set_settings(d.settings)
        self.set_zoom(d.zoom)
        self.refresh_style()
        self.widget.textChanged.connect(self.on_text_changed)

    def destroy(self):
        """ A reimplemented destructor.

        This destructor decrefs its document handle before calling the
        superclass destructor. This prevents a segfault in PyQt.

        """
        # Clear the strong reference to the document. It must be freed
        # *before* the last widget using it is freed or PyQt segfaults.
        del self.qsci_doc
        super(QtScintilla, self).destroy()

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_text_changed(self):
        """ Handle the 'textChanged' signal on the widget.

        """
        d = self.declaration
        if d is not None:
            d.text_changed()

    #--------------------------------------------------------------------------
    # Helper Methods
    #--------------------------------------------------------------------------
    def refresh_style(self):
        """ Refresh the theme styling for the widget.

        This method will style the widget and the lexer using the
        current theme that was provided by the declaration object.

        """
        colorcache = {}
        fontcache = {}

        def get_color(color_str):
            if color_str in colorcache:
                return colorcache[color_str]
            color = colorcache[color_str] = _make_color(color_str)
            return color

        def get_font(font_str):
            if font_str in fontcache:
                return fontcache[font_str]
            font = fontcache[font_str] = _make_font(font_str)
            return font

        def pull_color(dct, key, default):
            color = dct.get(key)
            if color is None:
                return default
            return get_color(color)

        def pull_font(dct, key, default):
            font = dct.get(key)
            if font is None:
                return default
            return get_font(font)

        # Setup the various defaults.
        caret_color = QColor(0, 0, 0)
        default_color = QColor(0, 0, 0)
        default_paper = QColor(255, 255, 255)
        default_font = QFont()

        # Update the defaults from the theme's root 'settings' object.
        theme = self.declaration.theme
        settings = theme.get('settings')
        if settings is not None:
            caret_color = pull_color(settings, 'caret', caret_color)
            default_color = pull_color(settings, 'color', default_color)
            default_paper = pull_color(settings, 'paper', default_paper)
            default_font = pull_font(settings, 'font', default_font)

        # Apply the default styling for the widget.
        widget = self.widget
        widget.setCaretForegroundColor(caret_color)
        widget.setColor(default_color)
        widget.setPaper(default_paper)
        widget.setFont(default_font)

        # Ensure the lexer and syntax tokens exist before continuing.
        lexer = widget.lexer()
        if lexer is None:
            return
        syntax = LEXERS_INV.get(type(lexer))
        if syntax is None:
            return

        # Resolve the default parameters and apply them for all lexer
        # styles. More specifc rules will override these defaults.
        syntax_rules = theme.get(syntax, {})
        syntax_tokens = TOKENS.get(syntax, {})
        syntax_default = syntax_rules.get('default', {})
        default_color = pull_color(syntax_default, 'color', default_color)
        default_paper = pull_color(syntax_default, 'paper', default_paper)
        default_font = pull_font(syntax_default, 'font', default_font)
        lexer.setColor(default_color)
        lexer.setPaper(default_paper)
        lexer.setFont(default_font)

        # Override the defaults with more specific syntax rules.
        for token, rule in syntax_rules.iteritems():
            if token == 'default':
                continue
            qtoken = getattr(lexer, syntax_tokens.get(token, ''), None)
            if qtoken is not None:
                color = pull_color(rule, 'color', default_color)
                paper = pull_color(rule, 'paper', default_paper)
                font = pull_font(rule, 'font', default_font)
                lexer.setColor(color, qtoken)
                lexer.setPaper(paper, qtoken)
                lexer.setFont(font, qtoken)
            else:
                msg = "unknown token '%s' given for the '%s' syntax"
                logger.warn(msg % (token, syntax))

    #--------------------------------------------------------------------------
    # ProxyScintilla API
    #--------------------------------------------------------------------------
    def set_document(self, document):
        """ Set the document on the underlying widget.

        """
        qdoc = self.qsci_doc_cache.get(document.uuid)
        if qdoc is None:
            qdoc = self.qsci_doc_cache[document.uuid] = Qsci.QsciDocument()
        self.qsci_doc = qdoc  # take a strong ref since PyQt doesn't
        self.widget.setDocument(qdoc)

    def set_syntax(self, syntax, refresh_style=True):
        """ Set the syntax on the underlying widget.

        """
        # The old lexer will remain as a child unless deleted.
        old = self.widget.lexer()
        if old is not None:
            old.deleteLater()
        lexer_cls = LEXERS.get(syntax) or (lambda w: None)
        self.widget.setLexer(lexer_cls(self.widget))
        if refresh_style:
            self.refresh_style()

    def set_theme(self, theme):
        """ Set the styling theme for the widget.

        """
        self.refresh_style()

    def set_settings(self, settings):
        """ Set the settings for the widget.

        """
        w = self.widget
        send = w.SendScintilla
        get = settings.get

        def pull(kind, name, default):
            value = get(name, default)
            if not isinstance(value, kind):
                msg = 'invalid value "%s" for "%s" setting'
                logger.warn(msg % (value, name))
                value = default
            return value

        pull_int = lambda name, default: pull(int, name, default)
        pull_bool = lambda name, default: pull(bool, name, default)
        pull_str = lambda name, default: pull(str, name, default)

        def pull_enum(options, name, default):
            value = pull_str(name, default)
            if value in options:
                return options[value]
            message = 'invalid value "%s" for "%s" setting'
            logger.warn(message % (value, name))
            return options[default]

        def pull_color(name, default):
            color = pull_str(name, default)
            return _make_color(color)

        # Line Endings
        send(w.SCI_SETEOLMODE, pull_enum(EOL_MODE, 'eol_mode', DEFAULT_EOL))
        send(w.SCI_SETVIEWEOL, pull_bool('view_eol', False))

        # Long Lines
        send(w.SCI_SETEDGEMODE, pull_enum(EDGE_MODE, 'edge_mode', 'none'))
        send(w.SCI_SETEDGECOLUMN, pull_int('edge_column', 79))
        send(w.SCI_SETEDGECOLOUR, pull_color('edge_color', ''))

        # Tabs and Indentation
        send(w.SCI_SETTABWIDTH, pull_int('tab_width', 8))
        send(w.SCI_SETUSETABS, pull_bool('use_tabs', True))
        send(w.SCI_SETINDENT, pull_int('indent', 0))
        send(w.SCI_SETTABINDENTS, pull_bool('tab_indents', False))
        send(w.SCI_SETBACKSPACEUNINDENTS,
            pull_bool('backspace_unindents', False))
        send(w.SCI_SETINDENTATIONGUIDES,
            pull_enum(INDENTATION_GUIDES, 'indentation_guides', 'none'))

        # White Space
        send(w.SCI_SETVIEWWS, pull_enum(WHITE_SPACE, 'view_ws', 'invisible'))
        send(w.SCI_SETWHITESPACESIZE, pull_int('white_space_size', 1))
        send(w.SCI_SETEXTRAASCENT, pull_int('extra_ascent', 0))
        send(w.SCI_SETEXTRADESCENT, pull_int('extra_descent', 0))

    def set_zoom(self, zoom):
        """ Set the zoom factor on the widget.

        """
        self.widget.zoomTo(zoom)

    def get_text(self):
        """ Get the text in the document.

        """
        return self.widget.text()

    def set_text(self, text):
        """ Set the text in the document.

        """
        self.widget.setText(text)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def set_foreground(self, foreground):
        """ Set the foreground color of the widget.

        This reimplementation ignores the foreground setting. The
        foreground color is set by the theme.

        """
        pass

    def set_background(self, background):
        """ Set the background color of the widget.

        This reimplementation ignores the background setting. The
        background color is set by the theme.

        """
        pass

    def set_font(self, font):
        """ Set the font of the widget.

        This reimplementation ignores the font setting. The font is
        set by the theme.

        """
        pass
