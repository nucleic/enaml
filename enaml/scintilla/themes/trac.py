#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

TRAC_THEME = {
    "python": {
        "comment": {
            "color": "#999988",
            "font-style": "italic"
        },
        "single_quoted_string": {
            "color": "#bb8844"
        },
        "class_name": {
            "color": "#445588",
            "font-weight": "bold"
        },
        "function_method_name": {
            "color": "#990000",
            "font-weight": "bold"
        },
        "operator": {
            "font-weight": "bold"
        },
        "double_quoted_string": {
            "color": "#bb8844"
        },
        "triple_double_quoted_string": {
            "color": "#bb8844"
        },
        "decorator": {
            "paper": "#ffffff"
        },
        "comment_block": {
            "color": "#999988",
            "font-style": "italic"
        },
        "keyword": {
            "font-weight": "bold"
        },
        "triple_single_quoted_string": {
            "color": "#bb8844"
        },
        "unclosed_string": {
            "color": "#a61717",
            "paper": "#e3d2d2"
        },
        "highlighted_identifier": {
            "paper": "#ffffcc"
        }
    },
    "settings": {
        "caret": "#000000",
        "color": "#000000",
        "paper": "#ffffff",
        "name": "trac"
    }
}

TRAC_THEME['enaml'] = TRAC_THEME['python']
