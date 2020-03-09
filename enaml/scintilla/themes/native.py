#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

NATIVE_THEME = {
    "python": {
        "comment": {
            "color": "#999999",
            "font-style": "italic"
        },
        "single_quoted_string": {
            "color": "#ed9d13"
        },
        "class_name": {
            "color": "#447fcf",
            "text-decoration": "underline"
        },
        "function_method_name": {
            "color": "#447fcf"
        },
        "operator": {
            "color": "#d0d0d0"
        },
        "double_quoted_string": {
            "color": "#ed9d13"
        },
        "triple_double_quoted_string": {
            "color": "#ed9d13"
        },
        "decorator": {
            "color": "#ffa500"
        },
        "comment_block": {
            "color": "#999999",
            "font-style": "italic"
        },
        "keyword": {
            "color": "#6ab825",
            "font-weight": "bold"
        },
        "triple_single_quoted_string": {
            "color": "#ed9d13"
        },
        "unclosed_string": {
            "color": "#a61717",
            "paper": "#e3d2d2"
        },
        "highlighted_identifier": {
            "paper": "#404040"
        }
    },
    "settings": {
        "caret": "#d0d0d0",
        "color": "#d0d0d0",
        "paper": "#202020",
        "name": "native"
    }
}

NATIVE_THEME['enaml'] = NATIVE_THEME['python']
