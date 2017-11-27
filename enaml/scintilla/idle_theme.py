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

AUTUMN_THEME = {
    "python": {
        "comment": {
            "color": "#aaaaaa"
        },
        "single_quoted_string": {
            "color": "#aa5500"
        },
        "class_name": {
            "color": "#00aa00"
        },
        "function_method_name": {
            "color": "#00aa00"
        },
        "operator": {
            "color": "#000000"
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
            "color": "#aaaaaa"
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

COLORFUL_THEME = {
    "python": {
        "comment": {
            "color": "#888888"
        },
        "single_quoted_string": {
            "color": "#000000"
        },
        "class_name": {
            "color": "#BB0066"
        },
        "function_method_name": {
            "color": "#0066BB"
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
            "color": "#888888"
        },
        "keyword": {
            "color": "#008800"
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
        "name": "colorful"
    }
}
COLORFUL_THEME['enaml'] = COLORFUL_THEME['python']

DEFAULT_THEME = {
    "python": {
        "comment": {
            "color": "#408080"
        },
        "single_quoted_string": {
            "color": "#BA2121"
        },
        "class_name": {
            "color": "#0000FF"
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
            "color": "#408080"
        },
        "keyword": {
            "color": "#008000"
        },
        "triple_single_quoted_string": {
            "color": "#BA2121"
        },
        "unclosed_string": {
            "color": "#000000",
            "paper": "#f8f8f8"
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

EMACS_THEME = {
    "python": {
        "comment": {
            "color": "#008800"
        },
        "single_quoted_string": {
            "color": "#BB4444"
        },
        "class_name": {
            "color": "#0000FF"
        },
        "function_method_name": {
            "color": "#00A000"
        },
        "operator": {
            "color": "#666666"
        },
        "double_quoted_string": {
            "color": "#BB4444"
        },
        "triple_double_quoted_string": {
            "color": "#BB4444"
        },
        "decorator": {
            "color": "#AA22FF"
        },
        "comment_block": {
            "color": "#008800"
        },
        "keyword": {
            "color": "#AA22FF"
        },
        "triple_single_quoted_string": {
            "color": "#BB4444"
        },
        "unclosed_string": {
            "color": "#000000",
            "paper": "#f8f8f8"
        },
        "highlighted_identifier": {
            "paper": "#ffffcc"
        }
    },
    "settings": {
        "caret": "#000000",
        "color": "#000000",
        "paper": "#f8f8f8",
        "name": "emacs"
    }
}
EMACS_THEME['enaml'] = EMACS_THEME['python']

FRIENDLY_THEME = {
    "python": {
        "comment": {
            "color": "#60a0b0"
        },
        "single_quoted_string": {
            "color": "#4070a0"
        },
        "class_name": {
            "color": "#0e84b5"
        },
        "function_method_name": {
            "color": "#06287e"
        },
        "operator": {
            "color": "#666666"
        },
        "double_quoted_string": {
            "color": "#4070a0"
        },
        "triple_double_quoted_string": {
            "color": "#4070a0"
        },
        "decorator": {
            "color": "#555555"
        },
        "comment_block": {
            "color": "#60a0b0"
        },
        "keyword": {
            "color": "#007020"
        },
        "triple_single_quoted_string": {
            "color": "#4070a0"
        },
        "unclosed_string": {
            "color": "#000000",
            "paper": "#f0f0f0"
        },
        "highlighted_identifier": {
            "paper": "#ffffcc"
        }
    },
    "settings": {
        "caret": "#000000",
        "color": "#000000",
        "paper": "#f0f0f0",
        "name": "friendly"
    }
}
FRIENDLY_THEME['enaml'] = FRIENDLY_THEME['python']

FRUITY_THEME = {
    "python": {
        "comment": {
            "color": "#008800"
        },
        "single_quoted_string": {
            "color": "#0086d2"
        },
        "class_name": {
            "color": "#ffffff"
        },
        "function_method_name": {
            "color": "#ff0086"
        },
        "operator": {
            "color": "#ffffff"
        },
        "double_quoted_string": {
            "color": "#0086d2"
        },
        "triple_double_quoted_string": {
            "color": "#0086d2"
        },
        "decorator": {
            "color": "#ffffff"
        },
        "comment_block": {
            "color": "#008800"
        },
        "keyword": {
            "color": "#fb660a"
        },
        "triple_single_quoted_string": {
            "color": "#0086d2"
        },
        "unclosed_string": {
            "color": "#ffffff",
            "paper": "#111111"
        },
        "highlighted_identifier": {
            "paper": "#333333"
        }
    },
    "settings": {
        "caret": "#ffffff",
        "color": "#ffffff",
        "paper": "#111111",
        "name": "fruity"
    }
}
FRUITY_THEME['enaml'] = FRUITY_THEME['python']

MANNI_THEME = {
    "python": {
        "comment": {
            "color": "#0099FF"
        },
        "single_quoted_string": {
            "color": "#CC3300"
        },
        "class_name": {
            "color": "#00AA88"
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
            "color": "#0099FF"
        },
        "keyword": {
            "color": "#006699"
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

NATIVE_THEME = {
    "python": {
        "comment": {
            "color": "#999999"
        },
        "single_quoted_string": {
            "color": "#ed9d13"
        },
        "class_name": {
            "color": "#447fcf"
        },
        "function_method_name": {
            "color": "#447fcf"
        },
        "operator": {
            "color": "#d0d0d0"
        },
        "double_quoted_string": {
            "color": "#ed9d13"
        },
        "triple_double_quoted_string": {
            "color": "#ed9d13"
        },
        "decorator": {
            "color": "#ffa500"
        },
        "comment_block": {
            "color": "#999999"
        },
        "keyword": {
            "color": "#6ab825"
        },
        "triple_single_quoted_string": {
            "color": "#ed9d13"
        },
        "unclosed_string": {
            "color": "#a61717",
            "paper": "#e3d2d2"
        },
        "highlighted_identifier": {
            "paper": "#404040"
        }
    },
    "settings": {
        "caret": "#d0d0d0",
        "color": "#d0d0d0",
        "paper": "#202020",
        "name": "native"
    }
}
NATIVE_THEME['enaml'] = NATIVE_THEME['python']

PASTIE_THEME = {
    "python": {
        "comment": {
            "color": "#888888"
        },
        "single_quoted_string": {
            "color": "#dd2200"
        },
        "class_name": {
            "color": "#bb0066"
        },
        "function_method_name": {
            "color": "#0066bb"
        },
        "operator": {
            "color": "#000000"
        },
        "double_quoted_string": {
            "color": "#dd2200"
        },
        "triple_double_quoted_string": {
            "color": "#dd2200"
        },
        "decorator": {
            "color": "#555555"
        },
        "comment_block": {
            "color": "#888888"
        },
        "keyword": {
            "color": "#008800"
        },
        "triple_single_quoted_string": {
            "color": "#dd2200"
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

PERLDOC_THEME = {
    "python": {
        "comment": {
            "color": "#228B22"
        },
        "single_quoted_string": {
            "color": "#CD5555"
        },
        "class_name": {
            "color": "#008b45"
        },
        "function_method_name": {
            "color": "#008b45"
        },
        "operator": {
            "color": "#000000"
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
            "color": "#8B008B"
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

TANGO_THEME = {
    "python": {
        "comment": {
            "color": "#8f5902"
        },
        "single_quoted_string": {
            "color": "#4e9a06"
        },
        "class_name": {
            "color": "#000000"
        },
        "function_method_name": {
            "color": "#000000"
        },
        "operator": {
            "color": "#ce5c00"
        },
        "double_quoted_string": {
            "color": "#4e9a06"
        },
        "triple_double_quoted_string": {
            "color": "#4e9a06"
        },
        "decorator": {
            "color": "#5c35cc"
        },
        "comment_block": {
            "color": "#8f5902"
        },
        "keyword": {
            "color": "#204a87"
        },
        "triple_single_quoted_string": {
            "color": "#4e9a06"
        },
        "unclosed_string": {
            "color": "#a40000",
            "paper": "#f8f8f8"
        },
        "highlighted_identifier": {
            "paper": "#ffffcc"
        }
    },
    "settings": {
        "caret": "#000000",
        "color": "#000000",
        "paper": "#f8f8f8",
        "name": "tango"
    }
}
TANGO_THEME['enaml'] = TANGO_THEME['python']

TRAC_THEME = {
    "python": {
        "comment": {
            "color": "#999988"
        },
        "single_quoted_string": {
            "color": "#bb8844"
        },
        "class_name": {
            "color": "#445588"
        },
        "function_method_name": {
            "color": "#990000"
        },
        "operator": {
            "color": "#000000"
        },
        "double_quoted_string": {
            "color": "#bb8844"
        },
        "triple_double_quoted_string": {
            "color": "#bb8844"
        },
        "decorator": {
            "color": "#000000"
        },
        "comment_block": {
            "color": "#999988"
        },
        "keyword": {
            "color": "#000000"
        },
        "triple_single_quoted_string": {
            "color": "#bb8844"
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
        "name": "trac"
    }
}
TRAC_THEME['enaml'] = TRAC_THEME['python']

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
            "paper": "#000000"
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

THEMES = {
    'autumn': AUTUMN_THEME,
    'colorful': COLORFUL_THEME,
    'default': DEFAULT_THEME,
    'emacs': EMACS_THEME,
    'friendly': FRIENDLY_THEME,
    'fruity': FRUITY_THEME,
    'idle': IDLE_THEME,
    'manni': MANNI_THEME,
    'monokai': MONOKAI_THEME,
    'murphy': MURPHY_THEME,
    'native': NATIVE_THEME,
    'pastie': PASTIE_THEME,
    'perldoc': PERLDOC_THEME,
    'tango': TANGO_THEME,
    'trac': TRAC_THEME,
    'vim': VIM_THEME,
}
