#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from pygments.lexer import RegexLexer, include, combined, bygroups
from pygments.lexers.agile import PythonLexer

from pygments.token import(
    Text, Comment, Operator, Keyword, Name, String, Number, Punctuation
)


# TODO use state transitions to lex arguments and identifiers
ENAML_DEF = (
    (r'^(enamldef)([ \t]+)([a-zA-Z_][a-zA-Z0-9_]*)([ \t]*)'
     r'(\()(.*?)(\))([ \t]*)(:)([ \t]*\n)'),
    bygroups(Keyword, Text, Name.Class, Text,
        Punctuation, Text, Punctuation, Text, Punctuation, Text),
)


CHILD_DEF = (
    r'^([ \t]+)([a-zA-Z_][a-zA-Z0-9_]*)([ \t]*)(:)([ \t]*\n)',
    bygroups(Text, Name.Tag, Text, Punctuation, Text),
)


CHILD_DEF_ID = (
    (r'^([ \t]+)([a-zA-Z_][a-zA-Z0-9_]*)([ \t]*)(:)([ \t]*)'
     r'([a-zA-Z_][a-zA-Z0-9_]*)([ \t]*)(:)([ \t]*\n)'),
    bygroups(Text, Name.Tag, Text, Punctuation, Text,
        Name.Entity, Text, Punctuation, Text),
)


ENAML_TOKENS = PythonLexer.tokens.copy()
ENAML_TOKENS['root'] = [
    (r'\n', Text),
    (r'^(\s*)([rRuU]{,2}"""(?:.|\n)*?""")', bygroups(Text, String.Doc)),
    (r"^(\s*)([rRuU]{,2}'''(?:.|\n)*?''')", bygroups(Text, String.Doc)),
    ENAML_DEF,
    CHILD_DEF_ID,
    CHILD_DEF,
    (r'[^\S\n]+', Text),
    (r'#.*$', Comment),
    (r'[]{}:(),;[]', Punctuation),
    (r'\\\n', Text),
    (r'\\', Text),
    (r'(in|is|and|or|not)\b', Operator.Word),
    (r'!=|==|<<|>>|[-~+/*%=<>&^|.]', Operator),
    include('keywords'),
    (r'(def)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'funcname'),
    (r'(class)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'classname'),
    (r'(template)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'funcname'),
    (r'(from)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text), 'fromimport'),
    (r'(import)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text), 'import'),
    include('builtins'),
    include('backtick'),
    ('(?:[rR]|[uU][rR]|[rR][uU])"""', String, 'tdqs'),
    ("(?:[rR]|[uU][rR]|[rR][uU])'''", String, 'tsqs'),
    ('(?:[rR]|[uU][rR]|[rR][uU])"', String, 'dqs'),
    ("(?:[rR]|[uU][rR]|[rR][uU])'", String, 'sqs'),
    ('[uU]?"""', String, combined('stringescape', 'tdqs')),
    ("[uU]?'''", String, combined('stringescape', 'tsqs')),
    ('[uU]?"', String, combined('stringescape', 'dqs')),
    ("[uU]?'", String, combined('stringescape', 'sqs')),
    include('name'),
    include('numbers'),
]


ENAML_TOKENS['keywords'] = [
    (r'(alias|assert|attr|break|const|continue|del|elif|else|except|exec|'
     r'event|finally|for|global|if|lambda|pass|print|raise|'
     r'return|try|while|yield|as|with)\b', Keyword),
]


class EnamlLexer(RegexLexer):
    """ For `Enaml <http://www.github.com/nucleic/enaml>`_ source code.

    """
    name = 'Enaml'
    aliases = ['enaml']
    filenames = ['*.enaml']
    mimetypes = ['text/x-enaml', 'application/x-enaml']

    tokens = ENAML_TOKENS
