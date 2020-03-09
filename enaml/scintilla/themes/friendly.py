#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

FRIENDLY_THEME = {
    "python": {
        "comment": {
            "color": "#60a0b0",
            "font-style": "italic"
        },
        "single_quoted_string": {
            "color": "#4070a0"
        },
        "class_name": {
            "color": "#0e84b5",
            "font-weight": "bold"
        },
        "function_method_name": {
            "color": "#06287e"
        },
        "operator": {
            "color": "#666666"
        },
        "double_quoted_string": {
            "color": "#4070a0"
        },
        "triple_double_quoted_string": {
            "color": "#4070a0"
        },
        "decorator": {
            "color": "#555555",
            "font-weight": "bold"
        },
        "comment_block": {
            "color": "#60a0b0",
            "font-style": "italic"
        },
        "keyword": {
            "color": "#007020",
            "font-weight": "bold"
        },
        "triple_single_quoted_string": {
            "color": "#4070a0"
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
        "paper": "#f0f0f0",
        "name": "friendly"
    }
}

FRIENDLY_THEME['enaml'] = FRIENDLY_THEME['python']
