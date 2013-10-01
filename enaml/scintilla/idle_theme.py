#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .mono_font import MONO_FONT


# TODO add many more syntaxes to this theme.
#: A Scintilla highlight theme based on the Python IDLE environment.
IDLE_THEME = {
    "settings": {
        "caret": "#000000",
        "color": "#000000",
        "paper": "#FFFFFF",
        "font": MONO_FONT
    },
    "python": {
        "class_name": {
            "color": "#21439C"
        },
        "comment": {
            "color": "#919191"
        },
        "comment_block": {
            "color": "#919191"
        },
        "decorator": {
            "color": "#DAD085"
        },
        "double_quoted_string": {
            "color": "#00A33F"
        },
        "function_method_name": {
            "color": "#21439C"
        },
        "highlighted_identifier": {
            "color": "#A535AE"
        },
        "keyword": {
            "color": "#FF5600"
        },
        "operator": {
            "color": "#FF5600"
        },
        "unclosed_string": {
            "color": "#00A33F",
            "paper": "#EECCCC"
        },
        "single_quoted_string": {
            "color": "#00A33F"
        },
        "triple_double_quoted_string": {
            "color": "#00A33F"
        },
        "triple_single_quoted_string": {
            "color": "#00A33F"
        }
    }
}


IDLE_THEME["enaml"] = IDLE_THEME["python"]
