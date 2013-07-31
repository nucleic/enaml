Scintilla Settings Specification
================================
This file describes how to define settings for the Enaml Scintilla widget.

Enaml supports Scintilla settings defined as simple Python dictionaries. The
format of the dictionary is amenable to being stored as a JSON file.

The keys of the theme dictionary are strings and the values will be some
form of Python primitive or builtin. The available keys and values are
described below, categorized into related topic.

An example of indentation settings for a Python session:

```python
{
    "tab_width": 4,
    "use_tabs": False,
    "indent": 4,
    "tab_indents": True,
    "backspace_unindents": True,
}
```


Line Endings
------------
- **eol_mode** (string) - The line ending convention. Valid values are:

    - **crlf** - the Windows \r\n convention

    - **cr** - the Mac \r convention

    - **lf** - the Unix \n convention.

  The default is chosen based on the current platform.

- **view_eol** (bool) - Whether to display the end of line characters. The
  default is False.


Long Lines
----------
- **edge_mode** (string) - The mode for the edge marker. Valid values are:

    - **none** - The default mode where no edge ruler is displayed.

    - **line** - A vertical line is drawn at the "edge_column".

    - **background** - The background color after "edge_column" is changed to
      this color.

- **edge_column** (int) - The column at which to display the long line marker.
  The default is 79.

- **edge_color** (string) - The color for the edge marker. This should conform
  to CSS color syntax.


Tabs and Indentation
--------------------
- **tab_width** (int) - The width of the tab character as a multiple of the
  size of a space character. The default is 8 characters.

- **use_tabs** (bool) - Wether indention should be created with a mixture of
  tabs and spaces, or purely spaces. The default is True and uses a mixture.

- **indent** (int) - The size of an indentation as a multiple of the size of
  a space character. If set to 0, the tab size is used. The default is 0.

- **tab_indents** (bool) - Whether the tab key inserts indentation instead of
  the tab character in the context of indentation whitespace. The default
  is False.

- **backspace_unindents** (bool) - Whether the backspace deletes indentation
  instead of a single character in the context of indentation whitespace.
  The default is False.

- **indentation_guides** (string) - The indentation guides to display. Valid
  values are:

    - **none** - the default mode with no indentation guides

    - **real** - guides are shown in real indentation whitespace

    - **look_forward** - guides are show beyond the actual indentation up to
      the next non-empty line

    - **look_both** - guides are shown up to the nextnon-empty line or
      previous non-empty line whichever is greater.


White Space
-----------
- **view_ws** (string) - The mode for viewing white space. Valid values are:

    - **invisible** - the default mode with invisible white space characters

    - **visible_always** - white space characters are drawn as dots and arrows

    - **visible_after_indent** - white space is displayed normal for
      indentation but shown with dots and arrows for everything else.

- **white_space_size** (int) - The size of the dots used for white space
  characters. The default is 1.

- **extra_ascent** (int) - Extra space above a line. The default is 0.

- **extra_descent** (int) - Extra space below a line. The default is 0.
