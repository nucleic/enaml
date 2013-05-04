#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------


# TODO Expose hooks for source code open for db-based source systems
def _format_source_error(filename, context, lineno):
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
    filename : string
        The name of the offending file.

    context : string
        The string name of the context scope in which the error
        occured. In the sample above, the context is 'bar'.

    lineno : int
        The integer line number of the offending line.

    Returns
    -------
    result : string
        A nicely formatted string for including in an exception. If the
        file cannot be opened, the source lines will note be included.

    """
    text = 'File "%s", line %d, in %s()' % (filename, lineno, context)
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


class DeclarativeException(Exception):
    """ A Sentinel exception type for declarative exceptions.

    """
    pass


class DeclarativeNameError(NameError, DeclarativeException):
    """ A NameError subclass which nicely formats the exception.

    This class is intended for used by Declarative and its subclasses to
    report errors for failed global lookups when building out the object
    tree.

    """
    def __init__(self, name, filename, context, lineno):
        """ Initialize a DeclarativeNameError.

        Parameters
        ----------
        name : string
            The name of global symbol which was not found.

        filename : string
            The name of the file where the error occurred.

        context : string
            The context name where the error occured.

        lineno : int
            The line number where the error occurred.

        """
        super(DeclarativeNameError, self).__init__(name)
        self.name = name
        self.filename = filename
        self.context = context
        self.lineno = lineno

    def __str__(self):
        """ A nicely formatted representaion of the exception.

        """
        text = '%s\n\n' % self.name
        text += _format_source_error(self.filename, self.context, self.lineno)
        text += "\n\n%s: global name '%s' " % (type(self).__name__, self.name)
        text += "is not defined"
        return text


class DeclarativeError(DeclarativeException):
    """ A Exception subclass which nicely formats the exception.

    This class is intended for use by the Enaml compiler machinery to
    indicate general errors when working with declarative types.

    """
    def __init__(self, message, filename, context, lineno):
        """ Initialize a DeclarativeError.

        Parameters
        ----------
        message : string
            The message to associate with the error.

        filename : string
            The name of the file where the error occurred.

        context : string
            The context name where the error occured.

        lineno : int
            The line number where the error occurred.

        """
        super(DeclarativeError, self).__init__(message)
        self.message = message
        self.filename = filename
        self.context = context
        self.lineno = lineno

    def __str__(self):
        """ A nicely formatted representaion of the exception.

        """
        text = '\n\n'
        text += _format_source_error(self.filename, self.context, self.lineno)
        text += "\n\n%s: %s" % (type(self).__name__, self.message)
        return text


class OperatorLookupError(LookupError, DeclarativeException):
    """ A LookupError subclass which nicely formats the exception.

    This class is intended for use by Enaml compiler machinery to report
    failures when looking up operators.

    """
    def __init__(self, operator, filename, context, lineno):
        """ Initialize an OperatorLookupError.

        Parameters
        ----------
        operator : string
            The name of the operator which was not found.

        filename : string
            The name of the file where the error occurred.

        context : string
            The context name where the error occured.

        lineno : int
            The line number where the error occurred.

        """
        super(OperatorLookupError, self).__init__(operator)
        self.operator = operator
        self.filename = filename
        self.context = context
        self.lineno = lineno

    def __str__(self):
        """ A nicely formatted representaion of the exception.

        """
        text = '\n\n'
        text += _format_source_error(self.filename, self.context, self.lineno)
        text += "\n\nOperatorLookupError: "
        text += "failed to load operator '%s'" % self.operator
        return text
