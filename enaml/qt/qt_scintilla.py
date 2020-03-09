#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from . import QT_API, PYSIDE_API, PYSIDE2_API, PYQT4_API, PYQT5_API
if QT_API in PYSIDE_API or QT_API in PYSIDE2_API:
    msg = 'the Qt Scintilla widget is only available when using PyQt'
    raise ImportError(msg)

import logging
import sys
import weakref

from atom.api import Typed

from enaml.colors import parse_color
from enaml.fonts import parse_font
from enaml.scintilla.scintilla import ProxyScintilla

if QT_API in PYQT4_API:
    from PyQt4 import Qsci
elif QT_API in PYQT5_API:
    from PyQt5 import Qsci
else:
    import QScintilla as Qsci

from .QtGui import QColor, QFont

from .q_resource_helpers import (QColor_from_Color, QFont_from_Font,
                                 get_cached_qimage)
from .qt_control import QtControl
from .scintilla_lexers import LEXERS, LEXERS_INV
from .scintilla_tokens import TOKENS


#: The module-level logger
logger = logging.getLogger(__name__)


Base = Qsci.QsciScintillaBase
QsciScintilla = Qsci.QsciScintilla


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

AUTOCOMPLETION_USE_SINGLE = {
    'never': QsciScintilla.AcusNever,
    'explicit': QsciScintilla.AcusExplicit,
    'always': QsciScintilla.AcusAlways,
}

AUTOCOMPLETION_SOURCE = {
    'none': QsciScintilla.AcsNone,
    'all': QsciScintilla.AcsAll,
    'document': QsciScintilla.AcsDocument,
    'apis': QsciScintilla.AcsAPIs,
}

INDICATOR_STYLE = {
    'plain': QsciScintilla.PlainIndicator,
    'squiggle': QsciScintilla.SquiggleIndicator,
    'tt': QsciScintilla.TTIndicator,
    'diagonal': QsciScintilla.DiagonalIndicator,
    'strike': QsciScintilla.StrikeIndicator,
    'hidden': QsciScintilla.HiddenIndicator,
    'box': QsciScintilla.BoxIndicator,
    'round_box': QsciScintilla.RoundBoxIndicator,
    'straight_box': QsciScintilla.StraightBoxIndicator,
    'full_box': QsciScintilla.FullBoxIndicator,
    'dashes': QsciScintilla.DashesIndicator,
    'dots': QsciScintilla.DotsIndicator,
    'squiggle_low': QsciScintilla.SquiggleLowIndicator,
    'dot_box': QsciScintilla.DotBoxIndicator,
    'thick_composition': QsciScintilla.ThickCompositionIndicator,
    'thin_composition': QsciScintilla.ThinCompositionIndicator,
    'text_color': QsciScintilla.TextColorIndicator,
    'triangle': QsciScintilla.TriangleIndicator,
    'triangle_character': QsciScintilla.TriangleCharacterIndicator,
}

NUMBER_MARGIN = 0


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
    widget = Typed(QsciScintilla)

    #: A reference to the autocomplete API
    qsci_api = Typed(Qsci.QsciAPIs)

    #: A strong reference to the QsciDocument handle.
    qsci_doc = Typed(Qsci.QsciDocument)

    #: Indicator style to style ID mapping
    _indicator_styles = Typed(dict, ())

    #: Marker image to marker ID mapping
    _marker_images = Typed(dict, ())

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying label widget.

        """
        self.widget = QsciScintilla(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtScintilla, self).init_widget()
        d = self.declaration
        self.set_document(d.document)
        self.set_autocomplete(d.autocomplete)
        self.set_syntax(d.syntax, refresh_style=False)
        self.set_settings(d.settings)
        self.set_zoom(d.zoom)
        self.refresh_style()
        if d.indicators:
            self.set_indicators(d.indicators)
        if d.markers:
            self.set_markers(d.markers)
        self.widget.textChanged.connect(self.on_text_changed)
        self.widget.cursorPositionChanged.connect(
            self.on_cursor_position_changed)

    def destroy(self):
        """ A reimplemented destructor.

        This destructor decrefs its document handle before calling the
        superclass destructor. This prevents a segfault in PyQt.

        """
        # Clear the strong reference to the document. It must be freed
        # *before* the last widget using it is freed or PyQt segfaults.
        del self.qsci_doc
        if self.qsci_api:
            del self.qsci_api
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

            self.refresh_line_number_width()

    def on_cursor_position_changed(self):
        """ Handle the 'cursorPositionChanged' signal on the widget.

        """
        d = self.declaration
        if d is not None:
            d.cursor_position = self.widget.getCursorPosition()

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
        for token, rule in syntax_rules.items():
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

    def refresh_autocomplete(self):
        """ If the lexer changes, update the API options as these depend
        on the lexer.

        """
        d = self.declaration
        if d.autocomplete in ['api', 'all'] and d.autocompletions:
            self.set_autocompletions(d.autocompletions)

    def refresh_line_number_width(self):
        """ When the number of lines changes update the width accordingly.
        Always shows one more than the width of the number of lines.

        """
        w = self.widget
        # Only update it if show_line_numbers=True
        if w.marginWidth(NUMBER_MARGIN) > 0:
            w.setMarginWidth(NUMBER_MARGIN, "0"+str(max(10, w.lines())))

    def get_indicator_style_id(self, indicator):
        """ Get the indicator style id for this indicator. The key
        is simply the style and fg color.

        If the key does not exist, define a new style.

        """
        style = "{},{}".format(indicator.style, indicator.color)
        if style not in self._indicator_styles:
            w = self.widget
            style_id = w.indicatorDefine(INDICATOR_STYLE[indicator.style])
            w.setIndicatorForegroundColor(_make_color(indicator.color),
                                          style_id)
            self._indicator_styles[style] = style_id
        return self._indicator_styles[style]

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
        self.refresh_autocomplete()
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
        w.setAutoIndent(pull_bool('auto_indent', False))

        # White Space
        send(w.SCI_SETVIEWWS, pull_enum(WHITE_SPACE, 'view_ws', 'invisible'))
        send(w.SCI_SETWHITESPACESIZE, pull_int('white_space_size', 1))
        send(w.SCI_SETEXTRAASCENT, pull_int('extra_ascent', 0))
        send(w.SCI_SETEXTRADESCENT, pull_int('extra_descent', 0))

        # Autocompletion
        # See https://qscintilla.com/general-autocompletion/
        w.setAutoCompletionThreshold(pull_int('autocompletion_threshold', 3))
        w.setAutoCompletionCaseSensitivity(
            pull_bool('autocompletion_case_sensitive', False))
        w.setAutoCompletionReplaceWord(
            pull_bool('autocompletion_replace_word', False))
        w.setAutoCompletionUseSingle(
            pull_enum(AUTOCOMPLETION_USE_SINGLE,
                      'autocompletion_use_single', 'never'))
        self.set_autocompletion_images(
            settings.get('autocompletion_images', []))

        # Line numbers
        self.set_show_line_numbers(pull_bool('show_line_numbers', False))

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

    def set_autocomplete(self, mode):
        """ Set the autocompletion mode

        """
        self.widget.setAutoCompletionSource(AUTOCOMPLETION_SOURCE[mode])

    def set_autocompletions(self, options):
        """ Set the autocompletion options for when the autocompletion mode
        is in 'all' or 'apis'.

        """
        # Delete the old if one exists
        if self.qsci_api:
            # Please note that it is not possible to add or remove entries
            # once you’ve “prepared” so we have to destroy and create
            # a new provider every time.
            self.qsci_api.deleteLater()
            self.qsci_api = None

        # Add the new options
        api = self.qsci_api = Qsci.QsciAPIs(self.widget.lexer())
        for option in options:
            api.add(option)
        api.prepare()

    def set_autocompletion_images(self, images):
        """ Set the images that can be used in autocompletion results.

        """
        w = self.widget
        w.clearRegisteredImages()
        for i, image in enumerate(images):
            w.registerImage(i, get_cached_qimage(image))

    def set_show_line_numbers(self, show):
        """ Set whether line numbers are shown or not by setting
        the margin width of the LineNumber margin.

        """
        w = self.widget
        w.setMarginType(NUMBER_MARGIN, QsciScintilla.NumberMargin)
        self.widget.setMarginWidth(
            NUMBER_MARGIN, "0"+str(max(10, w.lines())) if show else "")

    def set_markers(self, markers):
        """ Set the markers on the left margin of the widget.

        If the image is not a defined marker, one will be created.

        """
        w = self.widget

        # Clear markers
        w.markerDeleteAll()

        # Add the new markers
        for m in markers:
            # Define a new marker with the given image if one has not already
            # been created.
            if m.image not in self._marker_images:
                self._marker_images[m.image] = w.markerDefine(
                    get_cached_qimage(m.image))

            # Add the marker
            w.markerAdd(m.line, self._marker_images[m.image])

    def set_indicators(self, indicators):
        """ Set the indicators of the widget.

        This lets certain text be highlighted or underlined with a given
        style to indicate something (errors) within the editor.

        """
        w = self.widget

        # Cleanup old indicators by clearing all indicators in the document
        # There's no api to do this so clear the entire document range
        # for each style to ensure a clean state.
        lines = w.lines()
        column = w.lineLength(lines)
        for style_id in self._indicator_styles.values():
            w.clearIndicatorRange(0, 0, lines, column, style_id)

        # Add new indicators
        for ind in indicators:
            l0, c0 = ind.start
            l1, c1 = ind.stop
            w.fillIndicatorRange(l0, c0, l1, c1,
                                 self.get_indicator_style_id(ind))

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
