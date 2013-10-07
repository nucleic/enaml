#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups
from pygments.lexers.agile import PythonLexer

from pygments.token import Text, Keyword, Name, Punctuation, Operator


ENAMLDEF_START = (
    r'^(enamldef)([ \t]+)([a-zA-Z_][a-zA-Z0-9_]*)([ \t]*)(\()',
    bygroups(Keyword, Text, Name.Class, Text, Punctuation),
    'enamldef_base',
)


ENAMLDEF_BASE = (
    r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*)',
    bygroups(Text, Text, Text),
    'enamldef_end',
)


ENAMLDEF_END = (
    r'(\))([ \t]*)(:)([ \t]*\n)',
    bygroups(Punctuation, Text, Punctuation, Text),
    '#pop:2',
)


ENAMLDEF_END_ID = (
    r'(\))([ \t]*)(:)([ \t]*)([a-zA-Z_][a-zA-Z0-9_]*)([ \t]*)(:)([ \t]*\n)',
    bygroups(Punctuation, Text, Punctuation, Text, Name.Entity, Text,
        Punctuation, Text),
    '#pop:2',
)


TEMPLATE_START = (
    r'^(template)([ \t]+)([a-zA-Z_][a-zA-Z0-9_]*)([ \t]*)(\()',
    bygroups(Keyword, Text, Name.Function, Text, Punctuation),
    'template_end',
)


TEMPLATE_END = (
    r'(.*?)(\))([ \t]*)(:)([ \t]*\n)',
    bygroups(Text, Punctuation, Text, Punctuation, Text),
    '#pop',
)


TEMPLATEINST_START = (
    r'^([ \t]+)([a-zA-Z_][a-zA-Z0-9_]*)([ \t]*)(\()',
    bygroups(Text, Name.Tag, Text, Punctuation),
    'templateinst_end',
)


TEMPLATEINST_END = (
    r'(.*?)(\))([ \t]*)(:)([ \t]*\n)',
    bygroups(Text, Punctuation, Text, Punctuation, Text),
    '#pop',
)


TEMPLATEINST_END_ID = (
    r'(.*?)(\))([ \t]*)(:)([ \t]*)(?=\*?[a-zA-Z_])',
    bygroups(Text, Punctuation, Text, Punctuation, Text),
    'templateinst_id',
)


TEMPLATEINST_ID_1 = (
    r'(\*)([a-zA-Z_][a-zA-Z0-9_]*)',
    bygroups(Punctuation, Name.Entity),
)


TEMPLATEINST_ID_2 = (
    r'[a-zA-Z_][a-zA-Z0-9_]*', Name.Entity
)


TEMPLATEINST_ID_3 = (
    r',', Punctuation
)


TEMPLATEINST_ID_4 = (
    r'\s*', Text
)


TEMPLATEINST_ID_END = (
    r'(:)([ \t]*\n)',
    bygroups(Punctuation, Text),
    '#pop:2',
)


CHILDDEF_START = (
    r'^([ \t]+)([a-zA-Z_][a-zA-Z0-9_]*)([ \t]*)(:)(?=[ \t]*[a-zA-Z_\n])',
    bygroups(Text, Name.Tag, Text, Punctuation),
    'childdef_end',
)


CHILDDEF_END = (
    r'[ \t]*\n', Text, '#pop',
)


CHILDDEF_END_ID = (
    r'([ \t]*)([a-zA-Z_][a-zA-Z0-9_]*)([ \t]*)(:)([ \t]*\n)',
    bygroups(Text, Name.Entity, Text, Punctuation, Text),
    '#pop',
)


ENAML_TOKENS = PythonLexer.tokens.copy()
ENAML_TOKENS['root'] = [
    ENAMLDEF_START,
    TEMPLATE_START,
    TEMPLATEINST_START,
    CHILDDEF_START,
    (r'(alias|attr|const|event)\b', Keyword),
    (r':=', Operator),
] + ENAML_TOKENS['root']


ENAML_TOKENS['enamldef_base'] = [
    ENAMLDEF_BASE,
]


ENAML_TOKENS['enamldef_end'] = [
    ENAMLDEF_END_ID,
    ENAMLDEF_END,
]


ENAML_TOKENS['template_end'] = [
    TEMPLATE_END,
]


ENAML_TOKENS['templateinst_end'] = [
    TEMPLATEINST_END_ID,
    TEMPLATEINST_END,
]


ENAML_TOKENS['templateinst_id'] = [
    TEMPLATEINST_ID_END,
    TEMPLATEINST_ID_1,
    TEMPLATEINST_ID_2,
    TEMPLATEINST_ID_3,
    TEMPLATEINST_ID_4,
]


ENAML_TOKENS['childdef_end'] = [
    CHILDDEF_END_ID,
    CHILDDEF_END,
]


class EnamlLexer(RegexLexer):
    """ For `Enaml <http://www.github.com/nucleic/enaml>`_ source code.

    """
    name = 'Enaml'
    aliases = ['enaml']
    filenames = ['*.enaml']
    mimetypes = ['text/x-enaml', 'application/x-enaml']
    tokens = ENAML_TOKENS
