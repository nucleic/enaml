..-----------------------------------------------------------------------------
.. Copyright (c) 2013, Nucleic Development Team.
..
.. Distributed under the terms of the Modified BSD License.
..
.. The full license is in the file COPYING.txt, distributed with this software.
..-----------------------------------------------------------------------------
Scintilla Theme How-To
======================
This file describes how to create a syntax highlighting theme for the
Enaml Scintilla editor widget.

Enaml supports Scintilla themes defined as simple json files.

The toplevel item in the theme file is an object with keys which match
one of the available langauge syntax definitions::

    {
        "cpp": {

        },
        "python": {

        },
        "ruby": {

        },
    }

The value for a given langauge key is an object which contain the styling
data for that language. The keys of style object any of the syntax tokens
available for the given language::

    {
        "python": {
            "default": {

            },
            "comment": {

            },
            "number": {

            }
        }
    }

The value for a given language token is an object which defines the styling
to apply to that text which matches the token. The following keys are
allowed in a token styling object (and all are optional):

color
    The color to apply to the text. This is a string which conforms to
    the CSS color specification.

paper
    The color to apply to the "paper" background under the text. This is
    a string which conforms to the CSS color specification.

font
    The font to apply to the text. This is a string which conforms to
    the CSS shorthand font specification. Relative units and line height
    are not supported.

A rule for a Python number token might then look like:

    {
        "python": {
            "number": {
                "color": "#FFEE22",
                "paper": "lightskyblue",
                "font": "12pt Arial"
            }
        }
    }

The toplevel object supports a special key name "settings". The value of
this key is an object which provides settings and other defaults for the
editor. The following keys are supported:

color
    The default text color to use in the absence of a more specific rule.

paper
    The default paper color to use in the absence of a more specific rule.

font
    The default text font to use in the absence of a more specific rule.

caret
    The foreground color of the cursor caret.


Syntax Tokens
=============
Each syntax provides its own set of tokens which match the various structural
parts of the language. The number and granularity of these tokens depends on
the given syntax. The sections below enumerate the available tokens for each
syntax available in the widget. Each syntax supports a common token:

default
    The default style to apply in the absense of any matching token or
    for any token which does not have a complete style definition.

Python
------
The following tokens are available for the "python" syntax:

- class_name
- comment
- comment_block
- decorator
- double_quoted_string
- function_method_name
- highlighted_identifier
- identifier
- keyword
- number
- operator
- unclosed_string
- single_quoted_string
- triple_double_quoted_string
- triple_single_quoted_string
