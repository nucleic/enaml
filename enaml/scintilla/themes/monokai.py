#------------------------------------------------------------------------------
# Copyright (c) 2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------

MONOKAI_THEME = {
    "python": {
        "comment": {
            "color": "#75715e"
        },
        "single_quoted_string": {
            "color": "#e6db74"
        },
        "class_name": {
            "color": "#a6e22e"
        },
        "function_method_name": {
            "color": "#a6e22e"
        },
        "operator": {
            "color": "#f92672"
        },
        "double_quoted_string": {
            "color": "#e6db74"
        },
        "triple_double_quoted_string": {
            "color": "#e6db74"
        },
        "decorator": {
            "color": "#a6e22e"
        },
        "comment_block": {
            "color": "#75715e"
        },
        "keyword": {
            "color": "#66d9ef"
        },
        "triple_single_quoted_string": {
            "color": "#e6db74"
        },
        "unclosed_string": {
            "color": "#960050",
            "paper": "#1e0010"
        },
        "highlighted_identifier": {
            "paper": "#49483e"
        }
    },
    "settings": {
        "caret": "#f8f8f2",
        "color": "#f8f8f2",
        "paper": "#272822",
        "name": "monokai"
    }
}

MONOKAI_THEME['enaml'] = MONOKAI_THEME['python']
