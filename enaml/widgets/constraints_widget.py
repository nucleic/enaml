#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import List, ForwardTyped, Typed, observe

from enaml.core.declarative import d_
from enaml.layout.constrainable import ConstrainableMixin, PolicyEnum

from .widget import Widget, ProxyWidget


class ProxyConstraintsWidget(ProxyWidget):
    """ The abstract definition of a proxy ConstraintsWidget object.

    """
    #: A reference to the ConstraintsWidget declaration.
    declaration = ForwardTyped(lambda: ConstraintsWidget)

    def request_relayout(self):
        raise NotImplementedError


class ConstraintsWidget(Widget, ConstrainableMixin):
    """ A Widget subclass which adds constraint information.

    A ConstraintsWidget is augmented with symbolic constraint variables
    which define a box model on the widget. This box model is used to
    declare constraints between this widget and other components which
    participate in constraints-based layout.

    Constraints are added to a widget by assigning a list to the
    'constraints' attribute. This list may contain raw Constraint
    objects, which are created by manipulating the symbolic constraint
    variables, or ConstraintHelper objects which generate Constraint
    objects on request.

    """
    #: The list of user-specified constraints or ConstraintHelpers.
    constraints = d_(List())

    # Redefine the policy enums as declarative members. The docs on
    # the ConstrainableMixin class provide their full explanation.
    hug_width = d_(PolicyEnum('strong'))
    hug_height = d_(PolicyEnum('strong'))
    resist_width = d_(PolicyEnum('strong'))
    resist_height = d_(PolicyEnum('strong'))
    limit_width = d_(PolicyEnum('ignore'))
    limit_height = d_(PolicyEnum('ignore'))

    #: A reference to the ProxyConstraintsWidget object.
    proxy = Typed(ProxyConstraintsWidget)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(
        'constraints', 'hug_width', 'hug_height', 'resist_width',
        'resist_height', 'limit_width', 'limit_height', 'visible')
    def _layout_invalidated(self, change):
        """ An observer which will relayout the proxy widget.

        """
        if change['type'] == 'update':
            self.request_relayout()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def request_relayout(self):
        """ Request a relayout from the proxy widget.

        This will invoke the 'request_relayout' method on an active
        proxy. The proxy should collapse the requests as necessary.

        """
        if self.proxy_is_active:
            self.proxy.request_relayout()

    def when(self, switch):
        """ A method which returns `self` or None based on the truthness
        of the argument.

        This can be useful to easily turn off the effects of an object
        in constraints-based layout.

        Parameters
        ----------
        switch : bool
            A boolean which indicates whether this instance or None
            should be returned.

        Returns
        -------
        result : self or None
            If 'switch' is boolean True, self is returned. Otherwise,
            None is returned.

        """
        if switch:
            return self

    def layout_constraints(self):
        """ Get the constraints to use for this component's layout.

        This method may be overridden by subclasses as needed to create
        custom constraints. It will be called when the relayout request
        has been made by the layout engine. The default implementation
        will return the list of 'constraints' defined by the user.

        """
        return self.constraints
