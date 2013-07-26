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

from atom.api import Atom, Int, Str, Typed

from enaml.widgets.scintilla import ProxyScintilla

from PyQt4 import Qsci

from .QtGui import QColor, QFont

from .qt_control import QtControl
from .scintilla_lexers import LEXERS, LEXERS_INV
from .scintilla_tokens import TOKENS


class QtSciDoc(Atom):
    """ A helper class which manages references to a QsciDocument.

    """
    # There are some subtle lifetime issues when dealing with instances
    # of QsciDocument. If a given document is garbage collected after
    # the last widget to reference it is destroyed, PyQt will segfault.
    # This class tracks a "refcount" of the document and allows it to
    # be garbage collected before the last widget is destroyed.

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

    #: The name of the currently applied syntax.
    syntax = Str()

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
        self.set_syntax(d.syntax)
        self.set_theme(d.theme)
        self.set_zoom(d.zoom)
        self.widget.textChanged.connect(self.on_text_changed)
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
        d = self.declaration
        if d is not None:
            d.text_changed()

    def _refresh_theme(self):
        default_color = QColor(0, 0, 0)
        default_paper = QColor(255, 255, 255)
        default_font = QFont()
        caret_color = QColor(0, 0, 0)

        theme = self.theme
        settings = theme.get('settings')
        if settings is not None:
            default_color = settings.get('color', default_color)
            default_paper = settings.get('paper', default_paper)
            default_font = settings.get('font', default_font)
            caret_color = settings.get('caret', caret_color)

        widget = self.widget
        widget.setCaretForegroundColor(caret_color)

        lexer = widget.lexer()
        if lexer is not None:
            syntax = LEXERS_INV[type(lexer)]
            syntax_theme = theme.get(syntax, {})
            defaults = syntax_theme.get('default', {})
            default_color = defaults.get('color', default_color)
            default_paper = defaults.get('paper', default_paper)
            default_font = defaults.get('font', default_font)
            lexer.setColor(default_color)
            lexer.setPaper(default_paper)
            lexer.setFont(default_font)
            for token, style in syntax_theme.iteritems():
                qtoken = getattr(lexer, TOKENS.get(token, ''), None)
                if qtoken is not None:
                    color = style.get('color', default_color)
                    paper = style.get('paper', default_paper)
                    font = style.get('font', default_font)
                    lexer.setColor(color, qtoken)
                    lexer.setPaper(paper, qtoken)
                    lexer.setFont(font, qtoken)
                else:
                    print 'fail token', token

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

    def set_syntax(self, syntax):
        """ Set the syntax defintion on the underlying widget.

        """
        current = self.widget.lexer()
        if current is not None:
            # The current lexer still lives as a child of the widget
            # and must be deleted, or it will hang around forever.
            current.deleteLater()
        if not syntax:
            self.widget.setLexer(None)
        else:
            lexer = LEXERS[syntax](self.widget)
            self.widget.setLexer(lexer)
            lexer.refreshProperties()
        self.syntax = syntax
        self._refresh_theme()

    def set_theme(self, theme):
        """ Set the syntax highlighting theme for the widget.

        """
        if theme:
            self.theme = parse_theme(theme)
        else:
            self.theme = {}
        self._refresh_theme()

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
