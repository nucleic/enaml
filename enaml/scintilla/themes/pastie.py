#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

PASTIE_THEME = {
    "python": {
        "comment": {
            "color": "#888888"
        },
        "single_quoted_string": {
            "color": "#dd2200",
            "paper": "#fff0f0"
        },
        "class_name": {
            "color": "#bb0066",
            "font-weight": "bold"
        },
        "function_method_name": {
            "color": "#0066bb",
            "font-weight": "bold"
        },
        "operator": {
            "paper": "#ffffff"
        },
        "double_quoted_string": {
            "color": "#dd2200",
            "paper": "#fff0f0"
        },
        "triple_double_quoted_string": {
            "color": "#dd2200",
            "paper": "#fff0f0"
        },
        "decorator": {
            "color": "#555555"
        },
        "comment_block": {
            "color": "#888888"
        },
        "keyword": {
            "color": "#008800",
            "font-weight": "bold"
        },
        "triple_single_quoted_string": {
            "color": "#dd2200",
            "paper": "#fff0f0"
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
        "name": "pastie"
    }
}

PASTIE_THEME['enaml'] = PASTIE_THEME['python']
