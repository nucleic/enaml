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
from line_functions import get_indent, replace_at, add_indent, fix_backspace
from fields import AttributeField


class EnamlDeclDoc(BaseDoc):
    """Docstring refactoring for classes"""

    def __init__(self, lines, headers=None, verbose=False):

        if headers is None:
            headers = {'Input Attributes': 'attributes',
                       'Synchronized Attributes': 'attributes',
                       'Output Attributes': 'attributes',
                       'Public Attributes': 'attributes'}

        super(EnamlDeclDoc, self).__init__(lines, headers, verbose)
        return

    def _refactor_attributes(self, header):
        """Refactor the attributes section to sphinx friendly format"""

        if self.verbose:
            print '{0} Section'.format(header)

        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        fields = self.extract_fields(indent, AttributeField)
        header = fix_backspace(header)
        lines = [indent + ':{0}:'.format(header), '']
        for field in fields:
            lines += field.to_rst(len(indent) + 4)
        self.insert_lines(lines[:-1], index)
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
