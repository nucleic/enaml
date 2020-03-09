#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

PERLDOC_THEME = {
    "python": {
        "comment": {
            "color": "#228B22"
        },
        "single_quoted_string": {
            "color": "#CD5555"
        },
        "class_name": {
            "color": "#008b45",
            "font-weight": "bold"
        },
        "function_method_name": {
            "color": "#008b45"
        },
        "operator": {
            "paper": "#eeeedd"
        },
        "double_quoted_string": {
            "color": "#CD5555"
        },
        "triple_double_quoted_string": {
            "color": "#CD5555"
        },
        "decorator": {
            "color": "#707a7c"
        },
        "comment_block": {
            "color": "#228B22"
        },
        "keyword": {
            "color": "#8B008B",
            "font-weight": "bold"
        },
        "triple_single_quoted_string": {
            "color": "#CD5555"
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
        "paper": "#eeeedd",
        "name": "perldoc"
    }
}

PERLDOC_THEME['enaml'] = PERLDOC_THEME['python']
