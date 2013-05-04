# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
#  file: class_doc.py
#  License: LICENSE.TXT
#  Author: Ioannis Tziakos
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from base_doc import BaseDoc
from line_functions import get_indent, replace_at, add_indent
from fields import (max_header_length, max_desc_length,
                    max_name_length, MethodField, AttributeField)


class ClassDoc(BaseDoc):
    """Docstring refactoring for classes"""

    def __init__(self, lines, headers=None, verbose=False):

        if headers is None:
            headers = {'Attributes': 'attributes', 'Methods': 'methods',
                       'See Also': 'header', 'Abstract Methods': 'methods',
                       'Notes':'notes'}

        super(ClassDoc, self).__init__(lines, headers, verbose)
        return

    def _refactor_attributes(self, header):
        """Refactor the attributes section to sphinx friendly format"""

        if self.verbose:
            print '{0} Section'.format(header)

        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        fields = self.extract_fields(indent, AttributeField)

        descriptions = []
        for field in fields:
            descriptions += field.to_rst(len(indent))
        self.insert_lines(descriptions[:-1], index)
        self.index += len(descriptions)
        return

    def _refactor_methods(self, header):
        """Refactor the methods section to sphinx friendly format.

        """
        if self.verbose:
            print '{0} section'.format(header)

        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        method_fields = self.extract_fields(indent, MethodField)

        lines = []
        if len(method_fields) > 0 :
            name_length = max_name_length(method_fields)
            method_length = max_header_length(method_fields)
            desc_length = max_desc_length(method_fields)

            first_column = len(indent)
            second_column = first_column + method_length + name_length + 13
            first_column_str = '=' * (method_length + name_length + 12)
            second_column_str = '=' * desc_length

            border = '{0}{1} {2}'.format(indent,
                                              first_column_str,
                                              second_column_str)
            length = len(border)
            empty = length * ' '
            headings = empty[:]
            headings = replace_at('Methods', headings, first_column)
            headings = replace_at('Description', headings, second_column)
            lines.append(border)
            lines.append(headings)
            lines.append(border)
            for field in method_fields:
                lines += field.to_rst(length, first_column, second_column)
            lines.append(border)

        lines = [line.rstrip() for line in lines]
        self.insert_lines(lines, index)
        self.index += len(lines)
        return

    def _refactor_notes(self, header):
        """Refactor the note section to use the rst ``.. note`` directive.

        """
        descriptions = []
        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        paragraph = self.get_next_paragraph()
        descriptions.append(indent + '.. note::')
        descriptions += add_indent(paragraph)
        self.insert_lines(descriptions, index)
        self.index += len(descriptions)
        return descriptions
