#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from . import QT_API
if QT_API != 'pyqt':
    raise ImportError('the Qt TextEditor is only available when using PyQt')

from atom.api import Typed

from enaml.widgets.text_editor import ProxyTextEditor

from PyQt4 import Qsci

from .QtGui import QFont

from .q_resource_helpers import get_cached_qfont
from .qt_control import QtControl


LEXERS = {
    '': lambda: None,
    'bash': Qsci.QsciLexerBash,
    'batch': Qsci.QsciLexerBatch,
    'cmake': Qsci.QsciLexerCMake,
    'cpp': Qsci.QsciLexerCPP,
    'css': Qsci.QsciLexerCSS,
    'csharp': Qsci.QsciLexerCSharp,
    'd': Qsci.QsciLexerD,
    'diff': Qsci.QsciLexerDiff,
    'fortran': Qsci.QsciLexerFortran,
    'fortran77': Qsci.QsciLexerFortran77,
    'html': Qsci.QsciLexerHTML,
    'idl': Qsci.QsciLexerIDL,
    'java': Qsci.QsciLexerJava,
    'javascript': Qsci.QsciLexerJavaScript,
    'lua': Qsci.QsciLexerLua,
    'makefile': Qsci.QsciLexerMakefile,
    'matlab': Qsci.QsciLexerMatlab,
    'octave': Qsci.QsciLexerOctave,
    'pov': Qsci.QsciLexerPOV,
    'pascal': Qsci.QsciLexerPascal,
    'perl': Qsci.QsciLexerPerl,
    'postscript': Qsci.QsciLexerPostScript,
    'python': Qsci.QsciLexerPython,
    'ruby': Qsci.QsciLexerRuby,
    'sql': Qsci.QsciLexerSQL,
    'spice': Qsci.QsciLexerSpice,
    'tcl': Qsci.QsciLexerTCL,
    'tex': Qsci.QsciLexerTeX,
    'vhdl': Qsci.QsciLexerVHDL,
    'verilog': Qsci.QsciLexerVerilog,
    'xml': Qsci.QsciLexerXML,
    'yaml': Qsci.QsciLexerYAML,
}


class QtTextEditor(QtControl, ProxyTextEditor):
    """ A Qt implementation of an Enaml ProxyTextEditor.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(Qsci.QsciScintilla)

    lexer = Typed(Qsci.QsciLexer)

    font = Typed(QFont)

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
        super(QtTextEditor, self).init_widget()
        d = self.declaration
        self.set_document(d.document)
        self.set_syntax(d.syntax)
        self.widget.textChanged.connect(self.on_text_changed)
        self.widget.setIndentationWidth(4)
        self.widget.setIndentationsUseTabs(False)
        self.widget.setTabWidth(4)
        self.widget.setTabIndents(True)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_text_changed(self):
        d = self.declaration
        if d is not None:
            d.text_changed()

    def destroy(self):
        # setting parent to None and dropping the reference causes
        # PyQt to segfault on shutdown. deleteLater seems to work.
        self.widget.setDocument(Qsci.QsciDocument())
        self.widget.deleteLater()
        del self.widget

    #--------------------------------------------------------------------------
    # Helper Methods
    #--------------------------------------------------------------------------
    def refresh_lexer_font(self):
        if self.lexer is not None:
            self.lexer.setFont(self.font)

    #--------------------------------------------------------------------------
    # ProxyTextEditor API
    #--------------------------------------------------------------------------
    def set_document(self, document):
        """ Set the document on the underlying widget.

        """
        qdoc = document._tkdata
        if not isinstance(qdoc, Qsci.QsciDocument):
            qdoc = document._tkdata = Qsci.QsciDocument()
        self.widget.setDocument(qdoc)

    def set_syntax(self, syntax):
        """ Set the syntax defintion on the underlying widget.

        """
        lexer = LEXERS[syntax]()
        self.lexer = lexer
        self.widget.setLexer(lexer)
        self.refresh_lexer_font()

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
    def set_font(self, font):
        if font is not None:
            qfont = get_cached_qfont(font)
        else:
            qfont = QFont()
        self.widget.setFont(qfont)
        self.font = qfont
        self.refresh_lexer_font()
