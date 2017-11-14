#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from . import QT_API, PYSIDE_API, PYSIDE2_API, PYQT4_API, PYQT5_API
if QT_API in PYSIDE_API or QT_API in PYSIDE2_API:
    msg = 'the Qt Scintilla widget is only available when using PyQt'
    raise ImportError(msg)

if QT_API in PYQT4_API:
    from PyQt4 import Qsci
elif QT_API in PYQT5_API:
    from PyQt5 import Qsci
else:
    import QScintilla as Qsci


class PythonLexer(Qsci.QsciLexerPython):
    """ A custom Python lexer which highlights extra identifiers.

    """
    py_kwds = (
        'ArithmeticError AssertionError AttributeError BaseException '
        'BufferError BytesWarning DeprecationWarning EOFErr Ellipsis '
        'EnvironmentError Exception False FloatingPointError FutureWarning '
        'GeneratorExit IOError ImportError ImportWarning IndentationError '
        'IndexError KeyError KeyboardInterrupt LookupError MemoryError '
        'NameError None NotImplemented NotImplementedError OSError '
        'OverflowError PendingDeprecationWarning ReferenceError RuntimeError '
        'RuntimeWarning StandardError StopIteration SyntaxError SyntaxWarning '
        'SystemError SystemExit TabError True TypeError UnboundLocalError '
        'UnicodeDecodeError UnicodeEncodeError UnicodeError '
        'UnicodeTranslateError UnicodeWarning UserWarning ValueError Warning '
        'WindowsError ZeroDivisionError abs all any apply bin bool '
        'buffer bytearray bytes callable chr classmethod cmp coerce compile '
        'complex delattr dict dir divmod enumerate eval execfile file filter'
        'float format frozenset getattr globals hasattr hash help hex id input'
        'int intern isinstance issubclass iter len list locals long map max '
        'memoryview min next object oct open ord pow print property range '
        'raw_input reduce reload repr reversed round set setattr slice sorted'
        'staticmethod str sum super tuple type unichr unicode vars xrange zip'
    )

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
    'python': PythonLexer,
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
for key, value in LEXERS.items():
    LEXERS_INV[value] = key
