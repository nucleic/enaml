#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
class OperatorContext(dict):
    """ The Enaml operator context which provides the binding operators
    for Enaml components and a means by which developers can author
    custom operators.

    The OperatorContext is a dict subclass which is used by the Enaml
    runtime to lookup the operator functions required to bind an
    expression to an attribute of a component.

    """
    _stack_ = []

    _default_context_ = None

    @staticmethod
    def active_context():
        """ A staticmethod that returns the currently active operator
        context, or the default context if there is not active context.

        """
        stack = OperatorContext._stack_
        if not stack:
            ctxt = OperatorContext.default_context()
        else:
            ctxt = stack[-1]
        return ctxt

    @staticmethod
    def default_context():
        """ A staticmethod that returns the default operator context,
        creating one if necessary.

        """
        ctxt = OperatorContext._default_context_
        if ctxt is None:
            from enaml import default_operator_context
            ctxt = default_operator_context()
            OperatorContext._default_context_ = ctxt
        return ctxt

    def __enter__(self):
        """ A context manager method that pushes this context onto the
        active context stack.

        """
        OperatorContext._stack_.append(self)

    def __exit__(self, exc_type, exc_value, traceback):
        """ A context manager method that pops this context from the
        active context stack.

        """
        OperatorContext._stack_.pop()

