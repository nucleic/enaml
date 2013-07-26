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

from PyQt4 import Qsci


class PythonLexer(Qsci.QsciLexerPython):
    """ A custom Python lexer which highlights extra identifiers.

    """
    py_kwds = "self"  # add all builtins to this list

    def __init__(self, *args):
        super(PythonLexer, self).__init__(*args)
        # This setting is a relatively recent lexer addition.
        setter = getattr(self, 'setHighlightSubidentifiers', None)
        if setter is not None:
            setter(False)

    def keywords(self, kwset):
        if kwset == 2:
            return self.py_kwds
        return super(PythonLexer, self).keywords(kwset)


class EnamlLexer(PythonLexer):
    """ A custom Python lexer which adds Enaml keywords.

    """
    enaml_kwds = " enamldef attr event"

    def keywords(self, kwset):
        kwds = super(EnamlLexer, self).keywords(kwset)
        if kwset == 1:
            kwds += self.enaml_kwds
        return kwds


#: A static mapping of theme language name to lexer class.
LEXERS = {
    'bash': Qsci.QsciLexerBash,
    'batch': Qsci.QsciLexerBatch,
    'cmake': Qsci.QsciLexerCMake,
    'cpp': Qsci.QsciLexerCPP,
    'csharp': Qsci.QsciLexerCSharp,
    'css': Qsci.QsciLexerCSS,
    'd': Qsci.QsciLexerD,
    'diff': Qsci.QsciLexerDiff,
    'enaml': EnamlLexer,
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
    'pascal': Qsci.QsciLexerPascal,
    'perl': Qsci.QsciLexerPerl,
    'postscript': Qsci.QsciLexerPostScript,
    'pov': Qsci.QsciLexerPOV,
    'properties': Qsci.QsciLexerProperties,
    'python': Qsci.QsciLexerPython,
    'ruby': Qsci.QsciLexerRuby,
    'spice': Qsci.QsciLexerSpice,
    'sql': Qsci.QsciLexerSQL,
    'tcl': Qsci.QsciLexerTCL,
    'tex': Qsci.QsciLexerTeX,
    'verilog': Qsci.QsciLexerVerilog,
    'vhdl': Qsci.QsciLexerVHDL,
    'xml': Qsci.QsciLexerXML,
    'yaml': Qsci.QsciLexerYAML,
}


#: A static mapping of lexer class to theme language name.
LEXERS_INV = {}
for key, value in LEXERS.iteritems():
    LEXERS_INV[value] = key
