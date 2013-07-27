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

import json
import logging
import md5

from atom.api import Atom, Int, Str, Typed

from enaml.colors import parse_color
from enaml.fonts import parse_font
from enaml.widgets.scintilla import ProxyScintilla

from PyQt4 import Qsci

from .QtGui import QColor, QFont

from .q_resource_helpers import QColor_from_Color, QFont_from_Font
from .qt_control import QtControl
from .scintilla_lexers import LEXERS, LEXERS_INV
from .scintilla_tokens import TOKENS


#: The module-level logger
logger = logging.getLogger(__name__)


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


#: A static cache of parsed themes. A key in the cache is the md5 hash
#: of the json theme text. The value is the parsed theme. The number of
#: themes will be finite and relatively small. Rather than re-parsing
#: the theme for every file in every editor, they are cached and reused.
_parsed_theme_cache = {}


def parse_theme(theme):
    """ Parse a json theme file into a theme dictionary.

    If the given theme has already been parsed once, the cached parsed
    theme will be returned.

    Parameters
    ----------
    theme : str
        A json string defining the theme.

    Returns
    -------
    result : dict
        The parsed them dict. Since this may be a cached value, it
        should be considered read-only.

    """
    md5_sum = md5.new()
    md5_sum.update(theme)
    md5_hash = md5_sum.digest()
    if md5_hash in _parsed_theme_cache:
        return _parsed_theme_cache[md5_hash]

    try:
        theme_dict = json.loads(theme)
    except Exception as e:
        msg = "error occured while parsing the json theme: '%s'"
        logger.error(msg % e.message)
        return {}

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

    style_conv = [
        ('color', get_color),
        ('paper', get_color),
        ('font',  get_font),
    ]

    settings = theme_dict.get('settings')
    if settings is not None:
        if 'caret' in settings:
            settings['caret'] = get_color(settings['caret'])
        for key, func in style_conv:
            if key in settings:
                settings[key] = func(settings[key])

    for key, token_styles in theme_dict.iteritems():
        if key == 'settings':
            continue
        for style in token_styles.itervalues():
            for key, func in style_conv:
                if key in style:
                    style[key] = func(style[key])

    _parsed_theme_cache[md5_hash] = theme_dict

    return theme_dict


class QtSciDoc(Atom):
    """ A helper class which manages references to a QsciDocument.

    There are some subtle lifetime issues when dealing with instances
    of QsciDocument. If a given document is garbage collected after
    the last widget to reference it is destroyed, PyQt will segfault.
    This class tracks a "refcount" of the document and allows it to
    be garbage collected before the last widget is destroyed.

    """
    #: A static cache mapping uuid -> QtSciDoc instance.
    doc_cache = {}

    #: The actually document instance held by this handle.
    qsci_doc = Typed(Qsci.QsciDocument)

    #: The number of editors currently editing the assicated document.
    ref_count = Int()

    #: The uuid of the document as provided by Enaml.
    doc_id = Str()

    @classmethod
    def get(cls, doc_id):
        """ Get a QtSciDoc instance for the given doc_id.

        This will return a shared instance of the handle, or create a
        new handle if necessary. The caller is responsible for calling
        incref() and decref() as needed.

        """
        if doc_id in cls.doc_cache:
            return cls.doc_cache[doc_id]
        self = cls(doc_id=doc_id)
        self.qsci_doc = Qsci.QsciDocument()
        cls.doc_cache[doc_id] = self
        return self

    def incref(self):
        """ Increment the reference count of the document.

        """
        self.ref_count += 1

    def decref(self):
        """ Decrement the reference count of the document.

        If the ref count reaches zero, all strong references to the
        underlying QsciDocument will be removed, and the instance
        removed from the cache.

        """
        self.ref_count -= 1
        if self.ref_count == 0:
            self.qsci_doc = None
            self.doc_cache.pop(self.doc_id, None)


class QtScintilla(QtControl, ProxyScintilla):
    """ A Qt implementation of an Enaml ProxyScintilla.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(Qsci.QsciScintilla)

    #: Storage for the Qt document handle.
    qt_doc = Typed(QtSciDoc)

    #: The parsed theme to apply to the editor.
    theme = Typed(dict, ())

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
        self.set_lexer(d.lexer)
        self.set_theme(d.theme)
        self.set_zoom(d.zoom)
        self.widget.textChanged.connect(self.on_text_changed)

        # TODO move these to declaration settings
        self.widget.setIndentationWidth(4)
        self.widget.setIndentationsUseTabs(False)
        self.widget.setTabWidth(4)
        self.widget.setTabIndents(True)

    def destroy(self):
        """ A reimplemented destructor.

        This destructor decrefs its document handle before calling the
        superclass destructor. This prevents a segfault in PyQt.

        """
        doc = self.qt_doc
        if doc is not None:
            doc.decref()
            self.qt_doc = None
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
        # Setup the various defaults.
        caret_color = QColor(0, 0, 0)
        default_color = QColor(0, 0, 0)
        default_paper = QColor(255, 255, 255)
        default_font = QFont()

        # Update the defaults from the theme's root 'settings' object.
        theme = self.theme
        settings = theme.get('settings')
        if settings is not None:
            caret_color = settings.get('caret', caret_color)
            default_color = settings.get('color', default_color)
            default_paper = settings.get('paper', default_paper)
            default_font = settings.get('font', default_font)

        # Apply the styling for the widget.
        widget = self.widget
        widget.setCaretForegroundColor(caret_color)

        # Ensure the lexer and language def exist before continuing.
        lexer = widget.lexer()
        if lexer is None:
            return
        lang = LEXERS_INV.get(type(lexer))
        if lang is None:
            return

        # Resolve the default parameters and apply them for all lexer
        # styles. More specifc rules will override these defaults.
        lang_style = theme.get(lang, {})
        lang_tokens = TOKENS.get(lang, {})
        lang_default = lang_style.get('default', {})
        default_color = lang_default.get('color', default_color)
        default_paper = lang_default.get('paper', default_paper)
        default_font = lang_default.get('font', default_font)
        lexer.setColor(default_color)
        lexer.setPaper(default_paper)
        lexer.setFont(default_font)
        for token, style in lang_style.iteritems():
            lexer_token = getattr(lexer, lang_tokens.get(token, ''), None)
            if lexer_token is not None:
                color = style.get('color', default_color)
                paper = style.get('paper', default_paper)
                font = style.get('font', default_font)
                lexer.setColor(color, lexer_token)
                lexer.setPaper(paper, lexer_token)
                lexer.setFont(font, lexer_token)
            else:
                msg = "unknown lexer token '%s' defined for the '%s' theme"
                logger.warn(msg % (token, lang))

    #--------------------------------------------------------------------------
    # ProxyScintilla API
    #--------------------------------------------------------------------------
    def set_document(self, document):
        """ Set the document on the underlying widget.

        """
        old = self.qt_doc
        new = self.qt_doc = QtSciDoc.get(document.uuid)
        new.incref()
        if old is not None:
            old.decref()
        self.widget.setDocument(new.qsci_doc)

    def set_lexer(self, lexer):
        """ Set the lexer on the underlying widget.

        """
        # The old lexer will live forever as a child unless deleted.
        old = self.widget.lexer()
        if old is not None:
            old.deleteLater()
        lexer_cls = LEXERS.get(lexer) or (lambda w: None)
        self.widget.setLexer(lexer_cls(self.widget))
        self.refresh_style()

    def set_theme(self, theme):
        """ Set the syntax highlighting theme for the widget.

        """
        if theme is None:
            self.theme = {}
        else:
            self.theme = parse_theme(theme.load())
        self.refresh_style()

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
