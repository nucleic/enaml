#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

TANGO_THEME = {
    "python": {
        "comment": {
            "color": "#8f5902",
            "font-style": "italic"
        },
        "single_quoted_string": {
            "color": "#4e9a06"
        },
        "class_name": {
            "color": "#000000"
        },
        "function_method_name": {
            "color": "#000000"
        },
        "operator": {
            "color": "#ce5c00",
            "font-weight": "bold"
        },
        "double_quoted_string": {
            "color": "#4e9a06"
        },
        "triple_double_quoted_string": {
            "color": "#4e9a06"
        },
        "decorator": {
            "color": "#5c35cc",
            "font-weight": "bold"
        },
        "comment_block": {
            "color": "#8f5902",
            "font-style": "italic"
        },
        "keyword": {
            "color": "#204a87",
            "font-weight": "bold"
        },
        "triple_single_quoted_string": {
            "color": "#4e9a06"
        },
        "unclosed_string": {
            "color": "#a40000",
            "border": "1px solid #ef2929"
        },
        "highlighted_identifier": {
            "paper": "#ffffcc"
        }
    },
    "settings": {
        "caret": "#000000",
        "color": "#000000",
        "paper": "#f8f8f8",
        "name": "tango"
    }
}

TANGO_THEME['enaml'] = TANGO_THEME['python']
