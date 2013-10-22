# enaml.styling.parse_tab.lextab.py. This file automatically created by PLY (version 3.4). Don't edit!
_tabversion   = '3.4'
_lextokens    = {'IDENT': 1, 'HASH': 1, 'GREATER': 1, 'WS': 1, 'EQUAL': 1, 'STRING_START_SINGLE': 1, 'RPAR': 1, 'STAR': 1, 'DOUBLE_COLON': 1, 'COMMA': 1, 'STRING_CONTINUE': 1, 'NOT': 1, 'COLON': 1, 'LSQB': 1, 'STRING_END': 1, 'RSQB': 1, 'DOT': 1, 'STRING': 1}
_lexreflags   = 0
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive', 'SINGLEQ2': 'exclusive', 'SINGLEQ1': 'exclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_start_single_quoted_q1_string>\')|(?P<t_start_single_quoted_q2_string>")|(?P<t_IDENT>-?[a-zA-Z_][a-zA-Z0-9_-]*)|(?P<t_WS>[ \\t\\r\\n\\f]+)|(?P<t_NOT>:not\\()|(?P<t_GREATER>\\>)|(?P<t_STAR>\\*)|(?P<t_HASH>\\#)|(?P<t_LSQB>\\[)|(?P<t_RPAR>\\))|(?P<t_DOT>\\.)|(?P<t_RSQB>\\])|(?P<t_DOUBLE_COLON>::)|(?P<t_EQUAL>=)|(?P<t_COLON>:)|(?P<t_COMMA>,)', [None, ('t_start_single_quoted_q1_string', 'start_single_quoted_q1_string'), ('t_start_single_quoted_q2_string', 'start_single_quoted_q2_string'), (None, 'IDENT'), (None, 'WS'), (None, 'NOT'), (None, 'GREATER'), (None, 'STAR'), (None, 'HASH'), (None, 'LSQB'), (None, 'RPAR'), (None, 'DOT'), (None, 'RSQB'), (None, 'DOUBLE_COLON'), (None, 'EQUAL'), (None, 'COLON'), (None, 'COMMA')])], 'SINGLEQ2': [('(?P<t_SINGLEQ2_simple>[^"\\\\\\n]+)|(?P<t_SINGLEQ2_end>")', [None, ('t_SINGLEQ2_simple', 'simple'), ('t_SINGLEQ2_end', 'end')])], 'SINGLEQ1': [("(?P<t_SINGLEQ1_simple>[^'\\\\\\n]+)|(?P<t_SINGLEQ1_end>')", [None, ('t_SINGLEQ1_simple', 'simple'), ('t_SINGLEQ1_end', 'end')])]}
_lexstateignore = {'INITIAL': '', 'SINGLEQ2': '', 'SINGLEQ1': ''}
_lexstateerrorf = {'INITIAL': 't_error', 'SINGLEQ2': 't_SINGLEQ2_error', 'SINGLEQ1': 't_SINGLEQ1_error'}
