#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------

MURPHY_THEME = {
    "python": {
        "comment": {
            "color": "#666666"
        },
        "single_quoted_string": {
            "color": "#000000"
        },
        "class_name": {
            "color": "#ee99ee"
        },
        "function_method_name": {
            "color": "#55eedd"
        },
        "operator": {
            "color": "#333333"
        },
        "double_quoted_string": {
            "color": "#000000"
        },
        "triple_double_quoted_string": {
            "color": "#000000"
        },
        "decorator": {
            "color": "#555555"
        },
        "comment_block": {
            "color": "#666666"
        },
        "keyword": {
            "color": "#228899"
        },
        "triple_single_quoted_string": {
            "color": "#000000"
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
