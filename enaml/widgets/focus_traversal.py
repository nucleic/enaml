#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped

from enaml.core.declarative import d_func

from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyFocusTraversal(ProxyToolkitObject):
    """ The abstract defintion of a proxy FocusTraversal object.

    """
    #: A reference to the FocusTraversal declaration.
    declaration = ForwardTyped(lambda: FocusTraversal)


class FocusTraversal(ToolkitObject):
    """ An object which handles advanced focus traversal logic.

    An instance of this class can be declared as the child of any
    Widget in order to gain control over the tab traversal order of
    its decendants.

    Declaring more than one FocusTraversal child on a given Widget
    or reparenting a FocusTraversal object is a programming error
    and the resulting behavior is undefined.

    """
    #: A reference to the ProxyFocusTraversal object.
    proxy = Typed(ProxyFocusTraversal)

    @d_func
    def next_focus_child(self, current):
        """ Compute the next widget which should gain focus.

        This method is invoked as a result of a Tab key press or from
        a call to the 'focus_next_child' method on a decendant of the
        owner widget. It should be reimplemented in order to provide
        custom logic for computing the next focus widget.

        Parameters
        ----------
        current : Widget or None
            The current widget with input focus, or None if no widget
            has focus or if the toolkit widget with focus does not
            correspond to an Enaml widget.

        Returns
        -------
        result : Widget or None
            The next widget which should gain focus, or None to follow
            the default toolkit behavior.

        """
        return None

    @d_func
    def previous_focus_child(self, current):
        """ Compute the previous widget which should gain focus.

        This method is invoked as a result of a Shift+Tab key press or
        from a call to the 'focus_prev_child' method on a decendant of
        the owner widget. It should be reimplemented in order to provide
        custom logic for computing the previous focus widget.

        Parameters
        ----------
        current : Widget or None
            The current widget with input focus, or None if no widget
            has focus or if the toolkit widget with focus does not
            correspond to an Enaml widget.

        Returns
        -------
        result : Widget or None
            The previous widget which should gain focus, or None to
            follow the default toolkit behavior.

        """
        return None
