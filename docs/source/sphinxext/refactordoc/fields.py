# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
#  file: fields.py
#  License: LICENSE.TXT
#  Author: Ioannis Tziakos
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import collections
import re

from line_functions import add_indent, is_empty, remove_indent, replace_at


class Field(collections.namedtuple('Field', ('name','signature','desc'))):
    """ A docstring field.

    The class is based on the nametuple class and represents the logic
    to check, parse and refactor a docstring field.

    Attributes
    ----------
    name : str
        The name if the field, usssualy the name of a parameter of atrribute.

    signature : str
        The signature of the field. Commonly is the class type of an argument
        or the signature of a function.

    desc : str
        The description of the field. Given the type of the field this is a
        single paragraph or a block of rst source.

    """

    @classmethod
    def is_field(cls, line, indent=''):
        """ Check if the line is a field header.
        """
        regex = indent + r'\*?\*?\w+\s:(\s+|$)'
        match = re.match(regex, line)
        return match

    @classmethod
    def parse(cls, lines):
        """Parse a field definition for a set of lines.

        The field is assumed to be in one of the following formats::

            <name> : <type>
                <description>

        or::

            <name> :
                <description>

        or::

            <name>
                <description>

        Arguments
        ---------
        lines :
            docstring lines of the field without any empty lines before or
            after.

        Returns
        -------
        field :
            Field or subclass of Field

        """
        header = lines[0].strip()
        if ' :' in header:
            arg_name, arg_type = re.split('\s\:\s?', header, maxsplit=1)
        else:
            arg_name, arg_type = header, ''
        if len(lines) > 1:
            lines = [line.rstrip() for line in lines]
            return cls(arg_name.strip(), arg_type.strip(), lines[1:])
        else:
            return cls(arg_name.strip(), arg_type.strip(), [''])


    def to_rst(self, indent=4):
        """ Outputs field in rst as an itme in a definition list.

        Arguments
        ---------
        indent : int
            The indent to use for the decription block.


        Returns
        -------
        lines : list
            A list of string lines of formated rst.

        Example
        -------

        >>> Field('Ioannis', 'Ιωάννης', 'Is the greek guy.')
        >>> print Field.to_rst()
        Ioannis (Ιωάννης)
            Is the greek guy.

        """
        lines = []
        header = '{0} ({1})'.format(self.name, self.signature)
        lines.append(header)
        lines += add_indent(self.desc, indent)
        return lines

class AttributeField(Field):
    """ Field for the argument function docstrings """

    def to_rst(self, indent=4):
        """ Outputs field in rst using the ``:param:`` role.

        Arguments
        ---------
        indent : int
            The indent to use for the decription block.

        Example
        -------

        >>> Field('indent', 'int', 'The indent to use for the decription block.')
        >>> print Field.to_rst()
        :param indent: The indent to use for the description block
        :type indent: int

        """
        lines = []
        _type = self.signature
        annotation = '{0}    :annotation: = {1}'
        type_str = '' if is_empty(_type) else annotation.format(indent * ' ', _type)
        directive = '{0}.. attribute:: {1}'
        lines += [directive.format(indent * ' ', self.name), type_str]
        if type_str != '':
            lines.append('')
        lines += self.desc
        lines.append('')
        return lines


class ArgumentField(Field):
    """ Field for the argument function docstrings """

    def to_rst(self, indent=4):
        """ Outputs field in rst using the ``:param:`` role.

        Arguments
        ---------
        indent : int
            The indent to use for the decription block.

        Example
        -------

        >>> Field('indent', 'int', 'The indent to use for the decription block.')
        >>> print Field.to_rst()
        :param indent: The indent to use for the description block
        :type indent: int

        """
        lines = []
        name = self.name.replace('*','\*')  # Fix cases like *args and **kwargs
        indent_str = ' ' * indent
        param_str = '{0}:param {1}: {2}'.format(indent_str, name, self.desc[0].strip())
        type_str = '{0}:type {1}: {2}'.format(indent_str, name, self.signature)
        lines.append(param_str)
        lines += self.desc[1:]
        if len(self.signature) > 0:
            lines.append(type_str)
        return lines

class ListItemField(Field):
    """ Field that in rst is formated as an item in the list ignoring any
    field.type information.

    """

    def to_rst(self, indent=4, prefix=''):
        """ Outputs field in rst using as items in an list.

        Arguments
        ---------
        indent : int
            The indent to use for the decription block.

        prefix : str
            The prefix to use. For example if the item is part of a numbered
            list then ``prefix='# '``.

        Example
        -------


        Note
        ----
        The field descrption is reformated into a line.

        """
        indent_str = ' ' * indent
        rst_pattern = '{0}{1}**{2}**{3}' if is_empty(self.desc[0]) else \
                       '{0}{1}**{2}** -- {3}'
        description = '' if is_empty(self.desc[0]) else \
                      ' '.join(remove_indent(self.desc))
        return [rst_pattern.format(indent_str, prefix, self.name, description)]


class ListItemWithTypeField(Field):
    """ Field for the return section of the function docstrings """
    def to_rst(self, indent=4, prefix=''):
        indent_str = ' ' * indent
        _type = '' if self.signature == '' else '({0})'.format(self.signature)
        rst_pattern = '{0}{1}**{2}** {3}{4}' if is_empty(self.desc[0]) else \
                       '{0}{1}**{2}** {3} -- {4}'
        description = '' if is_empty(self.desc[0]) else \
                    ' '.join(remove_indent(self.desc))
        return [rst_pattern.format(indent_str, prefix, self.name, _type, description)]


class FunctionField(Field):
    """ A field that represents a function """

    @classmethod
    def is_field(cls, line, indent=''):
        regex = indent + r'\w+\(.*\)\s*'
        match = re.match(regex, line)
        return match

    def to_rst(self, length, first_column, second_column):
                split_result = re.split('\((.*)\)', self.name)
                method_name = split_result[0]
                method_text = ':meth:`{0} <{1}>`'.format(self.name, method_name)
                summary = ' '.join([line.strip() for line in self.desc])
                line = ' ' * length
                line = replace_at(method_text, line, first_column)
                line = replace_at(summary, line, second_column)
                return [line]

MethodField = FunctionField

#------------------------------------------------------------------------------
#  Functions to work with fields
#------------------------------------------------------------------------------

def max_name_length(method_fields):
    """ Find the max length of the function name in a list of method fields.

    Arguments
    ---------
    fields : list
        The list of the parsed fields.

    """
    return max([field[0].find('(') for field in method_fields])

def max_header_length(fields):
    """ Find the max length of the header in a list of fields.

    Arguments
    ---------
    fields : list
        The list of the parsed fields.

    """
    return max([len(field[0]) for field in fields])

def max_desc_length(fields):
    """ Find the max length of the description in a list of fields.

    Arguments
    ---------
    fields : list
        The list of the parsed fields.

    """
    return max([len(' '.join([line.strip() for line in field[2]]))
                for field in fields])
