#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
class NodeVisitor(object):
    """ A base class for implementing node visitors.

    Subclasses should implement visitor methods using the naming scheme
    'visit_<name>' where `<name>` is the type name of a given node.

    """
    def __call__(self, node):
        """ The main entry point of the visitor class.

        This method should be called to execute the visitor. It will
        call the setup and teardown methods before and after invoking
        the visit method on the node.

        Parameters
        ----------
        node : object
            The toplevel node of interest.

        Returns
        -------
        result : object
            The return value from the result() method.

        """
        self.setup(node)
        self.visit(node)
        result = self.result(node)
        self.teardown(node)
        return result

    def setup(self, node):
        """ Perform any necessary setup before running the visitor.

        This method is invoked before the visitor is executed over
        a particular node. The default implementation does nothing.

        Parameters
        ----------
        node : object
            The node passed to the visitor.

        """
        pass

    def result(self, node):
        """ Get the results for the visitor.

        This method is invoked after the visitor is executed over a
        particular node and the result() method has been called. The
        default implementation returns None.

        Parameters
        ----------
        node : object
            The node passed to the visitor.

        Returns
        -------
        result : object
            The results of the visitor.

        """
        return None

    def teardown(self, node):
        """ Perform any necessary cleanup when the visitor is finished.

        This method is invoked after the visitor is executed over a
        particular node and the result() method has been called. The
        default implementation does nothing.

        Parameters
        ----------
        node : object
            The node passed to visitor.

        """
        pass

    def visit(self, node):
        """ The main visitor dispatch method.

        Parameters
        ----------
        node : object
            A node from the tree.

        """
        for cls in type(node).mro():
            visitor_name = 'visit_' + cls.__name__
            visitor = getattr(self, visitor_name, None)
            if visitor is not None:
                visitor(node)
                return
        self.default_visit(node)

    def default_visit(self, node):
        """ The default node visitor method.

        This method is invoked when no named visitor method is found
        for a given node. This default behavior raises an exception for
        the missing handler. Subclasses may reimplement this method for
        custom default behavior.

        """
        msg = "no visitor found for node of type `%s`"
        raise TypeError(msg % type(node).__name__)
