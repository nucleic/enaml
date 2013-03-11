#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
def _format_source_error(filename, lineno, block):
    """ A helper function which generates an error string.

    This function handles the work of reading the lines of the file
    which bracket the error, and formatting a string which points to
    the offending line. The output is similar to:

    File "foo.py", line 42, in bar()
           41 def bar():
    ---->  42     a = a + 1
           43     return a

    Parameters
    ----------
    filename : str
        The full path to the offending file.

    lineno : int
        The line number of the offending like.

    block : str
        The name of the block scope in which the error occured. In the
        sample above, the block scope is 'bar'.

    Returns
    -------
    result : str
        A nicely formatted string for including in an exception. If the
        file cannot be opened, the source lines will note be included.

    """
    text = 'File "%s", line %d, in %s()' % (filename, lineno, block)
    start_lineno = max(0, lineno - 1)
    end_lineno = start_lineno + 2
    lines = []
    try:
        with open(filename, 'r') as f:
            for idx, line in enumerate(f, 1):
                if idx >= start_lineno and idx <= end_lineno:
                    lines.append((idx, line))
                elif idx > end_lineno:
                    break
    except IOError:
        pass
    if len(lines) > 0:
        digits = str(len(str(end_lineno)))
        line_templ = '\n----> %' + digits + 'd %s'
        other_templ = '\n      %' + digits + 'd %s'
        for lno, line in lines:
            line = line.rstrip()
            if lno == lineno:
                text += line_templ % (lno, line)
            else:
                text += other_templ % (lno, line)
    return text


class DeclarativeNameError(NameError):
    """ A NameError subclass which nicely formats the exception.

    This class is intended for used by Declarative and its subclasses to
    report errors for failed global lookups when building out the object
    tree.

    """
    def __init__(self, name, filename, lineno, block):
        """ Initialize a DeclarativeNameError.

        Parameters
        ----------
        name : str
            The name of global symbol which was not found.

        filename : str
            The filename where the lookup failed.

        lineno : int
            The line number of the error.

        block : str
            The name of the lexical block in which the lookup failed.

        """
        super(DeclarativeNameError, self).__init__(name)
        self.name = name
        self.filename = filename
        self.lineno = lineno
        self.block = block

    def __str__(self):
        """ A nicely formatted representaion of the exception.

        """
        text = '%s\n\n' % self.name
        text += _format_source_error(self.filename, self.lineno, self.block)
        text += "\n\nNameError: global name '%s' is not defined" % self.name
        return text


class OperatorLookupError(LookupError):
    """ A LookupError subclass which nicely formats the exception.

    This class is intended for use by Declarative and its subclasses to
    report errors for failed operator lookups when building the object
    tree.

    """
    op_map = {
        '__operator_Equal__': '=',
        '__operator_LessLess__': '<<',
        '__operator_ColonColon__': '::',
        '__operator_ColonEqual__': ':=',
        '__operator_GreaterGreater__': '>>',
    }

    def __init__(self, operator, filename, lineno, block):
        """ Initialize an OperatorLookupError.

        Parameters
        ----------
        operator : str
            The name of the operator which was not found.

        filename : str
            The filename where the lookup failed.

        lineno : int
            The line number of the error.

        block : str
            The name of the lexical block in which the lookup failed.

        """
        super(OperatorLookupError, self).__init__(operator)
        self.operator = operator
        self.filename = filename
        self.lineno = lineno
        self.block = block

    def __str__(self):
        """ A nicely formatted representaion of the exception.

        """
        op = self.operator
        text = '%s\n\n' % op
        text += _format_source_error(self.filename, self.lineno, self.block)
        optext = "'%s'" % op
        if op in self.op_map:
            optext += " ( %s )" % self.op_map[op]
        text += "\n\nOperatorLookupError: failed to load operator %s" % optext
        return text


class InvalidOverrideError(TypeError):
    """ A TypeError subclass which nicely formats the exception.

    This class is intended for use by the Enaml compiler machinery to
    indicate that overriding the given member is not allowed.

    """
    def __init__(self, suffix, filename, lineno, block):
        """ Initialize an InvalidOverrideError.

        Parameters
        ----------
        suffix : str
            The suffix to append to the end of the error message.

        filename : str
            The filename where the lookup failed.

        lineno : int
            The line number of the error.

        block : str
            The name of the lexical block in which the lookup failed.

        """
        super(InvalidOverrideError, self).__init__(suffix)
        self.suffix = suffix
        self.filename = filename
        self.lineno = lineno
        self.block = block

    def __str__(self):
        """ A nicely formatted representaion of the exception.

        """
        text = '\n\n'
        text += _format_source_error(self.filename, self.lineno, self.block)
        text += "\n\nInvalidOverrideError: cannot override %s" % self.suffix
        return text
