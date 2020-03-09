#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

EMACS_THEME = {
    "python": {
        "comment": {
            "color": "#008800",
            "font-style": "italic"
        },
        "single_quoted_string": {
            "color": "#BB4444"
        },
        "class_name": {
            "color": "#0000FF"
        },
        "function_method_name": {
            "color": "#00A000"
        },
        "operator": {
            "color": "#666666"
        },
        "double_quoted_string": {
            "color": "#BB4444"
        },
        "triple_double_quoted_string": {
            "color": "#BB4444"
        },
        "decorator": {
            "color": "#AA22FF"
        },
        "comment_block": {
            "color": "#008800",
            "font-style": "italic"
        },
        "keyword": {
            "color": "#AA22FF",
            "font-weight": "bold"
        },
        "triple_single_quoted_string": {
            "color": "#BB4444"
        },
        "unclosed_string": {
            "border": "1px solid #FF0000"
        },
        "highlighted_identifier": {
            "paper": "#ffffcc"
        }
    },
    "settings": {
        "caret": "#000000",
        "color": "#000000",
        "paper": "#f8f8f8",
        "name": "emacs"
    }
}

EMACS_THEME['enaml'] = EMACS_THEME['python']
