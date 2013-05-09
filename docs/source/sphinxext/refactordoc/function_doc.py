# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
#  file: function_doc.py
#  License: LICENSE.TXT
#  Author: Ioannis Tziakos
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from base_doc import BaseDoc
from line_functions import get_indent, add_indent
from fields import ArgumentField, ListItemWithTypeField, ListItemField


class FunctionDoc(BaseDoc):
    """Docstring refactoring for functions"""

    def __init__(self, lines, headers=None, verbose=False):

        if headers is None:
            headers = {'Returns': 'returns', 'Arguments': 'arguments',
                       'Parameters': 'arguments', 'Raises': 'raises',
                       'Yields': 'returns', 'Notes':'notes'}

        super(FunctionDoc, self).__init__(lines, headers, verbose)
        return

    def _refactor_returns(self, header):
        """Refactor the return section to sphinx friendly format.

        """
        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        fields = self.extract_fields(indent, field_type=ListItemWithTypeField)
        lines = [indent + ':returns:']
        prefix = '' if len(fields) == 1 else '- '
        for field in fields:
            lines += field.to_rst(len(indent) + 4, prefix)
        self.insert_lines(lines, index)
        self.index += len(lines)
        return

    def _refactor_raises(self, header):
        """Refactor the raises section to sphinx friendly format"""
        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        fields = self.extract_fields(indent, field_type=ListItemField)
        lines = [indent + ':raises:']
        prefix = '' if len(fields) == 1 else '- '
        for field in fields:
            lines += field.to_rst(len(indent) + 4, prefix)
        self.insert_lines(lines, index)
        self.index += len(lines)
        return

    def _refactor_arguments(self, header):
        """Refactor the argument section to sphinx friendly format
        """
        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        fields = self.extract_fields(indent, field_type=ArgumentField)
        lines = []
        for field in fields:
            lines += field.to_rst(len(indent))
        self.insert_lines(lines, index)
        self.index += len(lines)
        return

    def _refactor_notes(self, header):
        """Refactor the argument section to sphinx friendly format.

        """
        if self.verbose:
            print 'Refactoring Notes'

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

