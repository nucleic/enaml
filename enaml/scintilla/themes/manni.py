#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

MANNI_THEME = {
    "python": {
        "comment": {
            "color": "#0099FF",
            "font-style": "italic"
        },
        "single_quoted_string": {
            "color": "#CC3300"
        },
        "class_name": {
            "color": "#00AA88",
            "font-weight": "bold"
        },
        "function_method_name": {
            "color": "#CC00FF"
        },
        "operator": {
            "color": "#555555"
        },
        "double_quoted_string": {
            "color": "#CC3300"
        },
        "triple_double_quoted_string": {
            "color": "#CC3300"
        },
        "decorator": {
            "color": "#9999FF"
        },
        "comment_block": {
            "color": "#0099FF",
            "font-style": "italic"
        },
        "keyword": {
            "color": "#006699",
            "font-weight": "bold"
        },
        "triple_single_quoted_string": {
            "color": "#CC3300"
        },
        "unclosed_string": {
            "color": "#AA0000",
            "paper": "#FFAAAA"
        },
        "highlighted_identifier": {
            "paper": "#ffffcc"
        }
    },
    "settings": {
        "caret": "#000000",
        "color": "#000000",
        "paper": "#f0f3f3",
        "name": "manni"
    }
}

MANNI_THEME['enaml'] = MANNI_THEME['python']
