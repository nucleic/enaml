#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

AUTUMN_THEME = {
    "python": {
        "comment": {
            "color": "#aaaaaa",
            "font-style": "italic"
        },
        "single_quoted_string": {
            "color": "#aa5500"
        },
        "class_name": {
            "color": "#00aa00",
            "text-decoration": "underline"
        },
        "function_method_name": {
            "color": "#00aa00"
        },
        "operator": {
            "paper": "#ffffff"
        },
        "double_quoted_string": {
            "color": "#aa5500"
        },
        "triple_double_quoted_string": {
            "color": "#aa5500"
        },
        "decorator": {
            "color": "#888888"
        },
        "comment_block": {
            "color": "#aaaaaa",
            "font-style": "italic"
        },
        "keyword": {
            "color": "#0000aa"
        },
        "triple_single_quoted_string": {
            "color": "#aa5500"
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
        "name": "autumn"
    }
}

AUTUMN_THEME['enaml'] = AUTUMN_THEME['python']
