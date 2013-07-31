Scintilla Theme Specification
=============================
This file describes how to create a syntax highlighting theme for the
Enaml Scintilla widget.

Enaml supports Scintilla themes defined as simple Python dictionaries. The
format of the dictionary is amenable to being stored as a JSON file.

The keys of the theme dictionary are strings which refer to a syntax. e.g.,

```python
{
    "cpp": {

    },
    "python": {

    },
    "ruby": {

    },
}
```

The value for a given syntax key is a dictionary which contains the styling
data for the tokens of that syntax. The keys of the dict are the token names
specific to the syntax. e.g.,

```python
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
```

The value for a syntax token is a dictionary which defines the styling
to apply to the text which matches that token. The following keys are
allowed in a token style dictionary.

- **color** - The color to apply to the text. This is a string which conforms
  to the CSS color specification.

- **paper** - The color to apply to the "paper" background under the text.
  This is a string which conforms to the CSS color specification.

- **font** - The font to apply to the text. This is a string which conforms to
  the CSS shorthand font specification. Relative units and line height are not
  supported.

Hence, a complete rule for a Python number token might look like:

```python
{
    "python": {
        "number": {
            "color": "#FFEE22",
            "paper": "lightskyblue",
            "font": "12pt Arial"
        }
    }
}
```

The theme dictionary supports a special key named **settings**. The value
of this key is a dictionary which provides settings and other style defaults
for the editor. The following keys are supported:

- **color** - The default text color to use in the absence of a more specific
  rule.

- **paper** - The default paper color to use in the absence of a more specific
  rule.

- **font** - The default text font to use in the absence of a more specific
  rule.

- **caret** - The foreground color of the cursor caret.

An example of the IDLE theme for the **python** syntax:

```python
{
    "settings": {
        "caret": "#000000",
        "color": "#000000",
        "paper": "#FFFFFF",
        "font": "12pt Consolas"
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
```

Syntax Tokens
-------------
Each syntax provides its own set of tokens which match the various structural
parts of a language. The number and granularity of these tokens depends on
the given syntax. The sections below enumerate the available tokens for each
of the available syntax definitions along with the string name for the syntax.
Each syntax has at least one token in common:

- **default** - The default style to apply in the absence of any matching
  token or for any token which does not have a complete style definition.


Bash - "bash"
-------------
- **backticks**
- **comment**
- **default**
- **double_quoted_string**
- **error**
- **here_document_delimiter**
- **identifier**
- **keyword**
- **number**
- **operator**
- **parameter_expansion**
- **scalar**
- **single_quoted_here_document**
- **single_quoted_string**


Batch - "batch"
---------------
- **comment**
- **default**
- **external_command**
- **hide_command_char**
- **keyword**
- **label**
- **operator**
- **variable**


CMake - "cmake"
---------------
- **block_foreach**
- **block_if**
- **block_macro**
- **block_while**
- **comment**
- **default**
- **function**
- **keyword_set3**
- **label**
- **number**
- **string**
- **string_left_quote**
- **string_right_quote**
- **string_variable**
- **variable**


C++ - "cpp"
-----------
- **comment**
- **comment_doc**
- **comment_doc_keyword**:
- **comment_doc_keyword_error**
- **comment_line**
- **comment_line_doc**
- **default**
- **double_quoted_string**
- **global_class**
- **hash_quoted_string**
- **identifier**
- **inactive_comment**
- **inactive_comment_doc**
- **inactive_comment_doc_keyword**
- **inactive_comment_doc_keyword_error**
- **inactive_comment_line**
- **inactive_comment_line_doc**
- **inactive_default**
- **inactive_double_quoted_string**
- **inactive_global_class**
- **inactive_hash_quoted_string**
- **inactive_identifier**
- **inactive_keyword**
- **inactive_keyword_set2**
- **inactive_number**
- **inactive_operator**
- **inactive_pre_processor**
- **inactive_pre_processor_comment**
- **inactive_raw_string**
- **inactive_regex**
- **inactive_single_quoted_string**
- **inactive_triple_quoted_verbatim_string**
- **inactive_unclosed_string**
- **inactive_uuid**
- **inactive_verbatim_string**
- **keyword**
- **keyword_set2**
- **number**
- **operator**
- **pre_processor**
- **pre_processor_comment**
- **raw_string**
- **regex**
- **single_quoted_string**
- **triple_quoted_verbatim_string**
- **unclosed_string**
- **uuid**
- **verbatim_string**


C# - "csharp"
-------------
The **csharp** syntax uses the same token set as the **cpp** syntax.


CSS - "css"
-----------
- **at_rule**
- **attribute**
- **class_selector**
- **comment**
- **css1_property**
- **css2_property**
- **css3_property**
- **default**
- **double_quoted_string**
- **extended_css_property**
- **extended_pseudo_class**
- **extended_pseudo_element**
- **id_selector**
- **important**
- **media_rule**
- **operator**
- **pseudo_class**
- **pseudo_element**
- **single_quoted_string**
- **tag**
- **unknown_property**
- **unknown_pseudo_class**
- **value**
- **variable**


D - "d"
-------
- **backquote_string**
- **character**
- **comment**
- **comment_doc**
- **comment_doc_keyword**
- **comment_doc_keyword_error**
- **comment_line**
- **comment_line_doc**
- **comment_nested**
- **default**
- **identifier**
- **keyword**
- **keyword_doc**
- **keyword_secondary**
- **keyword_set5**
- **keyword_set6**
- **keyword_set7**
- **number**
- **operator**
- **raw_string**
- **string**
- **typedefs**
- **unclosed_string**


Diff - "diff"
-------------
- **command**
- **comment**
- **default**
- **header**
- **line_added**
- **line_changed**
- **line_removed**
- **position**


Enaml - "enaml"
---------------
The **enaml** syntax uses the same token set as the **python** syntax.


Fortran - "fortran"
-------------------
The **fortran** syntax uses the same token set as the **fortran77** syntax.


Fortran77 - "fortran77"
-----------------------
- **comment**
- **continuation**
- **default**
- **dotted_operator**
- **double_quoted_string**
- **extended_function**
- **identifier**
- **intrinsic_function**
- **keyword**
- **label**
- **number**
- **operator**
- **pre_processor**
- **single_quoted_string**
- **unclosed_string**


Html - "html"
-------------
- **asp_at_start**
- **asp_java_script_comment**
- **asp_java_script_comment_doc**
- **asp_java_script_comment_line**
- **asp_java_script_default**
- **asp_java_script_double_quoted_string**
- **asp_java_script_keyword**
- **asp_java_script_number**
- **asp_java_script_regex**
- **asp_java_script_single_quoted_string**
- **asp_java_script_start**
- **asp_java_script_symbol**
- **asp_java_script_unclosed_string**
- **asp_java_script_word**
- **asp_python_class_name**
- **asp_python_comment**
- **asp_python_default**
- **asp_python_double_quoted_string**
- **asp_python_function_method_name**
- **asp_python_identifier**
- **asp_python_keyword**
- **asp_python_number**
- **asp_python_operator**
- **asp_python_single_quoted_string**
- **asp_python_start**
- **asp_python_triple_double_quoted_string**
- **asp_python_triple_single_quoted_string**
- **asp_start**
- **aspvb_script_comment**
- **aspvb_script_default**
- **aspvb_script_identifier**
- **aspvb_script_keyword**
- **aspvb_script_number**
- **aspvb_script_start**
- **aspvb_script_string**
- **aspvb_script_unclosed_string**
- **aspxc_comment**
- **attribute**
- **cdata**
- **default**
- **entity**
- **html_comment**
- **html_double_quoted_string**
- **html_number**
- **html_single_quoted_string**
- **html_value**
- **java_script_comment**
- **java_script_comment_doc**
- **java_script_comment_line**
- **java_script_default**
- **java_script_double_quoted_string**
- **java_script_keyword**
- **java_script_number**
- **java_script_regex**
- **java_script_single_quoted_string**
- **java_script_start**
- **java_script_symbol**
- **java_script_unclosed_string**
- **java_script_word**
- **other_in_tag**
- **php_comment**
- **php_comment_line**
- **php_default**
- **php_double_quoted_string**
- **php_double_quoted_variable**
- **php_keyword**
- **php_number**
- **php_operator**
- **php_single_quoted_string**
- **php_start**
- **php_variable**
- **python_class_name**
- **python_comment**
- **python_default**
- **python_double_quoted_string**
- **python_function_method_name**
- **python_identifier**
- **python_keyword**
- **python_number**
- **python_operator**
- **python_single_quoted_string**
- **python_start**
- **python_triple_double_quoted_string**
- **python_triple_single_quoted_string**
- **script**
- **sgml_block_default**
- **sgml_command**
- **sgml_comment**
- **sgml_default**
- **sgml_double_quoted_string**
- **sgml_entity**
- **sgml_error**
- **sgml_parameter**
- **sgml_parameter_comment**
- **sgml_single_quoted_string**
- **sgml_special**
- **tag**
- **unknown_attribute**
- **unknown_tag**
- **vb_script_comment**
- **vb_script_default**
- **vb_script_identifier**
- **vb_script_keyword**
- **vb_script_number**
- **vb_script_start**
- **vb_script_string**
- **vb_script_unclosed_string**
- **xml_end**
- **xml_start**
- **xml_tag_end**


IDL - "idl"
-----------
The **idl** syntax uses the same token set as the **cpp** syntax.


Java - "java"
-------------
The **java** syntax uses the same token set as the **cpp** syntax.


Javascript - "javascript"
-------------------------
The **javascript** syntax uses the same token set as the **cpp** syntax.


Lua - "lua"
-----------
- **basic_functions**
- **character**
- **comment**
- **coroutines_io_system_facilities**
- **default**
- **identifier**
- **keyword**
- **keyword_set5**
- **keyword_set6**
- **keyword_set7**
- **keyword_set8**
- **label**
- **line_comment**
- **literal_string**
- **number**
- **operator**
- **preprocessor**
- **string**
- **string_table_maths_functions**
- **unclosed_string**


Makefile - "makefile"
---------------------
- **comment**
- **default**
- **error**
- **operator**
- **preprocessor**
- **target**
- **variable**


Matlab - "matlab"
-----------------
- **command**
- **comment**
- **default**
- **double_quoted_string**
- **identifier**
- **keyword**
- **number**
- **operator**
- **single_quoted_string**


Octave - "octave"
-----------------
The **octave** syntax uses the same token set as the **matlab** syntax.


Pascal - "pascal"
-----------------
- **asm**
- **character**
- **comment**
- **comment_line**
- **comment_parenthesis**
- **default**
- **hex_number**
- **identifier**
- **keyword**
- **number**
- **operator**
- **pre_processor**
- **pre_processor_parenthesis**
- **single_quoted_string**
- **unclosed_string**


Perl - "perl"
-------------
- **array**
- **backtick_here_document**
- **backtick_here_document_var**
- **backticks**
- **backticks_var**
- **comment**
- **data_section**
- **default**
- **double_quoted_here_document**
- **double_quoted_here_document_var**
- **double_quoted_string**
- **double_quoted_string_var**
- **error**
- **format_body**
- **format_identifier**
- **hash**
- **here_document_delimiter**
- **identifier**
- **keyword**
- **number**
- **operator**
- **pod**
- **pod_verbatim**
- **quoted_string_q**
- **quoted_string_qq**
- **quoted_string_qq_var**
- **quoted_string_qr**
- **quoted_string_qr_var**
- **quoted_string_qw**
- **quoted_string_qx**
- **quoted_string_qx_var**
- **regex**
- **regex_var**
- **scalar**
- **single_quoted_here_document**
- **single_quoted_string**
- **subroutine_prototype**
- **substitution**
- **substitution_var**
- **symbol_table**
- **translation**


Postscript - "postscript"
-------------------------
- **array_parenthesis**
- **bad_string_character**
- **base85_string**
- **comment**
- **default**
- **dictionary_parenthesis**
- **dsc_comment**
- **dsc_comment_value**
- **hex_string**
- **immediate_eval_literal**
- **keyword**
- **literal**
- **name**
- **number**
- **procedure_parenthesis**
- **text**


POV - "pov"
-----------
- **bad_directive**
- **comment**
- **comment_line**
- **default**
- **directive**
- **identifier**
- **keyword_set6**
- **keyword_set7**
- **keyword_set8**
- **number**
- **objects_csg_appearance**
- **operator**
- **predefined_functions**
- **predefined_identifiers**
- **string**
- **types_modifiers_items**
- **unclosed_string**


Properties - "properties"
-------------------------
- **assignment**
- **comment**
- **default**
- **default_value**
- **key**
- **section**


Python - "python"
-----------------
- **class_name**
- **comment**
- **comment_block**
- **decorator**
- **default**
- **double_quoted_string**
- **function_method_name**
- **highlighted_identifier**
- **identifier**
- **keyword**
- **number**
- **operator**
- **single_quoted_string**
- **triple_double_quoted_string**
- **triple_single_quoted_string**
- **unclosed_string**


Ruby - "ruby"
-------------
- **backticks**
- **class_name**
- **class_variable**
- **comment**
- **data_section**
- **default**
- **demoted_keyword**
- **double_quoted_string**
- **error**
- **function_method_name**
- **global**
- **here_document**
- **here_document_delimiter**
- **identifier**
- **instance_variable**
- **keyword**
- **module_name**
- **number**
- **operator**
- **percent_string_q**
- **percent_stringq**
- **percent_stringr**
- **percent_stringw**
- **percent_stringx**
- **pod**
- **regex**
- **single_quoted_string**
- **stderr**
- **stdin**
- **stdout**
- **symbol**


Spice - "spice"
---------------
- **command**
- **comment**
- **default**
- **delimiter**
- **function**
- **identifier**
- **number**
- **parameter**
- **value**


SQL - "sql"
-----------
- **comment**
- **comment_doc**
- **comment_doc_keyword**
- **comment_doc_keyword_error**
- **comment_line**
- **comment_line_hash**
- **default**
- **double_quoted_string**
- **identifier**
- **keyword**
- **keyword_set5**
- **keyword_set6**
- **keyword_set7**
- **keyword_set8**
- **number**
- **operator**
- **plus_comment**
- **plus_keyword**
- **plus_prompt**
- **quoted_identifier**
- **single_quoted_string**


TCL - "tcl"
-----------
- **comment**
- **comment_block**
- **comment_box**
- **comment_line**
- **default**
- **expand_keyword**
- **identifier**
- **itcl_keyword**
- **keyword_set6**
- **keyword_set7**
- **keyword_set8**
- **keyword_set9**
- **modifier**
- **number**
- **operator**
- **quoted_keyword**
- **quoted_string**
- **substitution**
- **substitution_brace**
- **tcl_keyword**
- **tk_command**
- **tk_keyword**


TEX - "tex"
-----------
- **command**
- **default**
- **group**
- **special**
- **symbol**
- **text**


Verilog - "verilog"
-------------------
- **comment**
- **comment_bang**
- **comment_line**
- **default**
- **identifier**
- **keyword**
- **keyword_set2**
- **number**
- **operator**
- **preprocessor**
- **string**
- **system_task**
- **unclosed_string**
- **user_keyword_set**


VHDL - "vhdl"
-------------
- **attribute**
- **comment**
- **comment_line**
- **default**
- **identifier**
- **keyword**
- **keyword_set7**
- **number**
- **operator**
- **standard_function**
- **standard_operator**
- **standard_package**
- **standard_type**
- **string**
- **unclosed_string**


XML - "xml"
-----------
The **xml** syntax uses the same token set as the **html** syntax.


YAML - "yaml"
-------------
- **comment**
- **default**
- **document_delimiter**
- **identifier**
- **keyword**
- **number**
- **operator**
- **reference**
- **syntax_error_marker**
- **text_block_marker**
