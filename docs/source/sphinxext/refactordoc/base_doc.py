# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
#  file: base_doc.py
#  License: LICENSE.TXT
#  Author: Ioannis Tziakos
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import re

from fields import Field
from line_functions import is_empty, get_indent, fix_backspace

#------------------------------------------------------------------------------
#  Classes
#------------------------------------------------------------------------------

class BaseDoc(object):
    """Base abstract docstring refactoring class.

    The class' main purpose is to parse the dosctring and find the
    sections that need to be refactored. It also provides a number of
    methods to help with the refactoring. Subclasses should provide
    the methods responsible for refactoring the sections.

    Attributes
    ----------
    docstring : list
        A list of strings (lines) that holds docstrings

    index : int
        The current zero-based line number of the docstring that is
        proccessed.

    verbose : bool
        When set the class prints a lot of info about the proccess
        during runtime.

    headers : dict
        The sections that the class refactors. Each entry in the
        dictionary should have as key the name of the section in the
        form that it appears in the docstrings. The value should be
        the postfix of the method, in the subclasses, that is
        responsible for refactoring (e.g. {'Methods': 'method'}).

    """

    def __init__(self, lines, headers = None, verbose=False):
        """ Initialize the class

        The method setups the class attributes and starts parsing the
        docstring to find and refactor the sections.

        Arguments
        ---------
        lines : list of strings
            The docstring to refactor

        headers : dict
            The sections for which the class has custom refactor methods.
            Each entry in the dictionary should have as key the name of
            the section in the form that it appears in the docstrings.
            The value should be the postfix of the method, in the
            subclasses, that is responsible for refactoring (e.g.
            {'Methods': 'method'}).

        verbose : bool
            When set the class logs info about the proccess
            during runtime.

        """
        try:
            self._docstring = lines.splitlines()
        except AttributeError:
            self._docstring = lines
        self.verbose = verbose
        self.headers = {} if headers is None else headers
        self.index = 0
        self.parse()

    def parse(self):
        """ Parse the docstring.

        The docstring is parsed for sections. If a section is found then
        the corresponding refactoring method is called.

        """
        self.index = 0
        self.seek_to_next_non_empty_line()
        while not self.eol:
            header = self.is_section()
            if header:
                self.remove_if_empty(self.index + 2)  # Remove space after header
                self._refactor(header)
            else:
                self.index += 1
                self.seek_to_next_non_empty_line()

    def _refactor(self, header):
        """Call the heading refactor method.

        The name of the refctoring method is constructed using the form
        _refactor_<header>. Where <header> is the value corresponding to
        ``self.headers[header]``. If there is no custom method for the
        section then the self._refactor_header() is called with the
        found header name as input.

        """
        refactor_postfix = self.headers.get(header, 'header')
        method_name = ''.join(('_refactor_', refactor_postfix))
        method = getattr(self, method_name)
        method(header)

    def _refactor_header(self, header):
        """ Refactor the header section using the rubric directive.

        The method has been tested and supports refactoring single word
        headers, two word headers and headers that include a backslash
        ''\''.

        Arguments
        ---------
        header : string
            The header string to use with the rubric directive.

        """
        index = self.index
        indent = get_indent(self.peek())
        self.remove_lines(index, 2)
        descriptions = []
        header = fix_backspace(header)
        descriptions += [indent + '.. rubric:: {0}'.format(header), '']
        self.insert_lines(descriptions, index)
        self.index += len(descriptions)
        return descriptions


    def extract_fields(self, indent='', field_type=None):
        """Extract the fields from the docstring

        Parse the fields in the description of a section into tuples of
        name, type and description in a list of strings. The parsed lines
        are also removed from original list.

        Arguments
        ---------
        indent : str, optional
            the indent argument is used to make sure that only the lines
            with the same indent are considered when checking for a
            field header line. The value is used to define the field
            checking function.

        field_check : function
            Optional function to use for checking if the next line is a
            field. The signature of the function is ``foo(line)`` and it
            should return ``True`` if the line contains a valid field
            The default function is checking for fields of the following
            formats::

                <name> : <type>

            or::

                <name> :

            Where the name has to be one word.

        Returns
        -------
        parameters : list of tuples
            list of parsed parameter tuples as returned from the
            :meth:`~BaseDocstring.parse_field` method.

        """
        field_type = Field if (field_type is None) else field_type
        is_field = field_type.is_field
        fields = []
        while (not self.eol) and (is_field(self.peek(), indent) or
                                  is_field(self.peek(1), indent)):
            self.remove_if_empty(self.index)
            field_block = self.get_next_block()
            field = field_type.parse(field_block)
            fields.append(field)
        return fields

    def get_next_block(self):
        """ Get the next field block from the docstring.

        The method reads the next block in the docstring. The first line
        assumed to be the field header and the following lines to belong to
        the description::

            <header line>
                <descrition>

        The end of the field is designated by a line with the same indent
        as the field header or two empty lines are found in sequence. Thus,
        there are two valid field layouts:

        1. No lines between fields::

            <field1>
                <description1>
            <fieldd2>
                <description2>

        2. One line between fields::

            <field1>
                <description1>

            <field2>
                <description2>

        """
        start = self.index
        field_header = self.read()
        indent = get_indent(field_header) + ' '
        field = [field_header]
        while (not self.eol):
            peek_0 = self.peek()
            peek_1 = self.peek(1)
            if (is_empty(peek_0) and (not peek_1.startswith(indent))) \
                or \
                ((not is_empty(peek_0)) and (not peek_0.startswith(indent))):
                break
            else:
                line = self.read()
                field.append(line.rstrip())

        self.remove_lines(start, len(field))
        self.index = start
        return field

    def is_section(self):
        """Check if the line defines a section.

        """
        if self.eol:
            return False

        header = self.peek()
        line2 = self.peek(1)
        if self.verbose:
            print 'current line is: {0} at index {1}'.format(header, self.index)

        # check for underline type format
        underline = re.match(r'\s*\S+\s*\Z', line2)
        if underline is None:
            return False
        # is the nextline an rst underline?
        striped_header = header.rstrip()
        expected_underline1 = re.sub(r'[A-Za-z\\]|\b\s', '-', striped_header)
        expected_underline2 = re.sub(r'[A-Za-z\\]|\b\s', '=', striped_header)
        if ((underline.group().rstrip() == expected_underline1) or
            (underline.group().rstrip() == expected_underline2)):
            return header.strip()
        else:
            return False

    def insert_lines(self, lines, index):
        """ Insert refactored lines

        Arguments
        ---------
        new_lines : list
            The list of lines to insert

        index : int
            Index to start the insertion
        """
        docstring = self.docstring
        for line in reversed(lines):
            docstring.insert(index, line)

    def seek_to_next_non_empty_line(self):
        """ Goto the next non_empty line

        """
        docstring = self.docstring
        for line in docstring[self.index:]:
            if not is_empty(line):
                break
            self.index += 1


    def get_next_paragraph(self):
        """ Get the next paragraph designated by an empty line.

        """
        docstring = self.docstring
        lines = []
        start = self.index
        while (not self.eol) and (not is_empty(self.peek())):
            line = self.read()
            lines.append(line)
        del docstring[start:self.index]
        return lines

    def read(self):
        """ Return the next line and advance the index.

        """
        index = self.index
        line = self._docstring[index]
        self.index += 1
        return line

    def remove_lines(self, index, count=1):
        """ Removes the lines for the docstring

        """
        docstring = self.docstring
        del docstring[index:(index + count)]

    def remove_if_empty(self, index=None):
        """ Remove the line from the docstring if it is empty.

        """
        if is_empty(self.docstring[index]):
            self.remove_lines(index)

    def peek(self, ahead=0):
        """ Peek ahead a number of lines

        The function retrieves the line that is ahead of the current
        index. If the index is at the end of the list then it returns an
        empty string.

        Arguments
        ---------
        ahead : int
            The number of lines to look ahead.


        """
        position = self.index + ahead
        try:
            line = self.docstring[position]
        except IndexError:
            line = ''
        return line

    @property
    def eol(self):
        return self.index >= len(self.docstring)

    @property
    def docstring(self):
        """ Get the docstring lines.

        """
        return self._docstring

