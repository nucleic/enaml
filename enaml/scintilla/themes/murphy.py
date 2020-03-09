#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

MURPHY_THEME = {
    "python": {
        "comment": {
            "color": "#666666",
            "font-style": "italic"
        },
        "single_quoted_string": {
            "paper": "#e0e0ff"
        },
        "class_name": {
            "color": "#ee99ee",
            "font-weight": "bold"
        },
        "function_method_name": {
            "color": "#55eedd",
            "font-weight": "bold"
        },
        "operator": {
            "color": "#333333"
        },
        "double_quoted_string": {
            "paper": "#e0e0ff"
        },
        "triple_double_quoted_string": {
            "paper": "#e0e0ff"
        },
        "decorator": {
            "color": "#555555",
            "font-weight": "bold"
        },
        "comment_block": {
            "color": "#666666",
            "font-style": "italic"
        },
        "keyword": {
            "color": "#228899",
            "font-weight": "bold"
        },
        "triple_single_quoted_string": {
            "paper": "#e0e0ff"
        },
        "unclosed_string": {
            "color": "#FF0000",
            "paper": "#FFAAAA"
        },
        "highlighted_identifier": {
            "paper": "#ffffcc"
        }
    },
    "settings": {
        "caret": "#000000",
        "color": "#000000",
        "paper": "#ffffff",
        "name": "murphy"
    }
}

MURPHY_THEME['enaml'] = MURPHY_THEME['python']
