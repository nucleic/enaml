#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

DEFAULT_THEME = {
    "python": {
        "comment": {
            "color": "#408080",
            "font-style": "italic"
        },
        "single_quoted_string": {
            "color": "#BA2121"
        },
        "class_name": {
            "color": "#0000FF",
            "font-weight": "bold"
        },
        "function_method_name": {
            "color": "#0000FF"
        },
        "operator": {
            "color": "#666666"
        },
        "double_quoted_string": {
            "color": "#BA2121"
        },
        "triple_double_quoted_string": {
            "color": "#BA2121"
        },
        "decorator": {
            "color": "#AA22FF"
        },
        "comment_block": {
            "color": "#408080",
            "font-style": "italic"
        },
        "keyword": {
            "color": "#008000",
            "font-weight": "bold"
        },
        "triple_single_quoted_string": {
            "color": "#BA2121"
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
        "name": "default"
    }
}

DEFAULT_THEME['enaml'] = DEFAULT_THEME['python']
