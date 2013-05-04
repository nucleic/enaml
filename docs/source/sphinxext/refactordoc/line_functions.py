# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
#  file: line_functions.py
#  License: LICENSE.TXT
#  Author: Ioannis Tziakos
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
#!/usr/bin/env python
import re

#------------------------------------------------------------------------------
#  Precompiled regexes
#------------------------------------------------------------------------------
indent_regex = re.compile(r'\s+')

#------------------------------------------------------------------------------
#  Functions to manage indention
#------------------------------------------------------------------------------

def add_indent(lines, indent=4):
    """ Add spaces to indent a list of lines.

    Arguments
    ---------
    lines : list
        The list of strings to indent.

    indent : int
        The number of spaces to add.

    Returns
    -------
    lines : list
        The indented strings (lines).

    .. note:: Empty strings are not changed

    """
    indent_str = ' ' * indent
    output = []
    for line in lines:
        if is_empty(line):
            output.append(line)
        else:
            output.append(indent_str + line)
    return output

def remove_indent(lines):
    """ Remove all indentation from the lines.

    """
    return [line.lstrip() for line in lines]

def get_indent(line):
    """ Return the indent portion of the line.

    """
    indent = indent_regex.match(line)
    if indent is None:
        return ''
    else:
        return indent.group()

#------------------------------------------------------------------------------
#  Functions to detect line type
#------------------------------------------------------------------------------

def is_empty(line):
    return not line.strip()

#------------------------------------------------------------------------------
#  Functions to adjust strings
#------------------------------------------------------------------------------

def fix_star(word):
    return word.replace('*','\*')

def fix_backspace(word):
    return word.replace('\\', '\\\\')

def replace_at(word, line, index):
    """ Replace the text in-line.

    The text in line is replaced (not inserted) with the word. The
    replacement starts at the provided index. The result is cliped to
    the input length

    Arguments
    ---------
    word : str
        The text to copy into the line.

    line : str
        The line where the copy takes place.

    index : int
        The index to start coping.

    Returns
    -------
    result : str
        line of text with the text replaced.

    """
    word_length = len(word)
    result = line[:index] + word + line[(index + word_length):]
    return result[:len(line)]


