#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

VIM_THEME = {
    "python": {
        "comment": {
            "color": "#000080"
        },
        "single_quoted_string": {
            "color": "#cd0000"
        },
        "class_name": {
            "color": "#00cdcd"
        },
        "function_method_name": {
            "color": "#cccccc"
        },
        "operator": {
            "color": "#3399cc"
        },
        "double_quoted_string": {
            "color": "#cd0000"
        },
        "triple_double_quoted_string": {
            "color": "#cd0000"
        },
        "decorator": {
            "color": "#cccccc"
        },
        "comment_block": {
            "color": "#000080"
        },
        "keyword": {
            "color": "#cdcd00"
        },
        "triple_single_quoted_string": {
            "color": "#cd0000"
        },
        "unclosed_string": {
            "color": "#cccccc",
            "border": "1px solid #FF0000"
        },
        "highlighted_identifier": {
            "paper": "#222222"
        }
    },
    "settings": {
        "caret": "#cccccc",
        "color": "#cccccc",
        "paper": "#000000",
        "name": "vim"
    }
}

VIM_THEME['enaml'] = VIM_THEME['python']
