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
  values are: `"real"` - guides are shown in real indentation whitespace,
  `"look_forward"` - guides are show beyond the actual indentation up to the
  next non-empty line, `"look_both"` - guides are shown up to the next non-empty
  line or previous non-empty line whichever is greater.
