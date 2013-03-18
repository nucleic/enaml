#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
def _format_source_error(location):
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
    location : dict
        A dict of location information with the following keys:

        'filename'
            The full string path to the offending file.

        'lineno'
            The integer line number of the offending line.

        'block'
            The string name of the block scope in which the error
            occured. In the sample above, the block scope is 'bar'.

    Returns
    -------
    result : str
        A nicely formatted string for including in an exception. If the
        file cannot be opened, the source lines will note be included.

    """
    filename = location['filename']
    lineno = location['lineno']
    block = location['block']
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
    def __init__(self, name, location):
        """ Initialize a DeclarativeNameError.

        Parameters
        ----------
        name : str
            The name of global symbol which was not found.

        location : dict
            The location dict with 'filename', 'lineno', and 'block'
            keys indicating the source location of the failure.

        """
        super(DeclarativeNameError, self).__init__(name)
        self.name = name
        self.location = location

    def __str__(self):
        """ A nicely formatted representaion of the exception.

        """
        text = '%s\n\n' % self.name
        text += _format_source_error(self.location)
        text += "\n\n%s: global name '%s' " % (type(self).__name__, self.name)
        text += "is not defined"
        return text


class DeclarativeError(Exception):
    """ A Exception subclass which nicely formats the exception.

    This class is intended for use by the Enaml compiler machinery to
    indicate general errors when working with declarative types.

    """
    def __init__(self, message, location):
        """ Initialize an DeclarativeError.

        Parameters
        ----------
        message : str
            The message to display for the exception.

        location : dict
            The location dict with 'filename', 'lineno', and 'block'
            keys indicating the source location of the failure.

        """
        super(DeclarativeError, self).__init__(message)
        self.message = message
        self.location = location

    def __str__(self):
        """ A nicely formatted representaion of the exception.

        """
        text = '\n\n'
        text += _format_source_error(self.location)
        text += "\n\n%s: %s" % (type(self).__name__, self.message)
        return text


class OperatorLookupError(LookupError):
    """ A LookupError subclass which nicely formats the exception.

    This class is intended for use by Enaml compiler machinery to report
    failures when looking up operators.

    """
    def __init__(self, operator, location):
        """ Initialize an OperatorLookupError.

        Parameters
        ----------
        operator : str
            The name of the operator which was not found.

        location : dict
            The location dict with 'filename', 'lineno', and 'block'
            keys indicating the source location of the failure.

        """
        super(OperatorLookupError, self).__init__(operator)
        self.operator = operator
        self.location = location

    def __str__(self):
        """ A nicely formatted representaion of the exception.

        """
        text = '\n\n'
        text += _format_source_error(self.location)
        text += "\n\nOperatorLookupError: "
        text += "failed to load operator '%s'" % self.operator
        return text
