#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Enum, Typed, List, ForwardTyped, observe

from enaml.core.declarative import d_
from enaml.layout.constrainable import ConstrainableMixin

from .widget import Widget, ProxyWidget


#: An atom enum which defines the allowable constraints strengths.
#: Clones will be made by selecting a new default via 'select'.
PolicyEnum = Enum('ignore', 'weak', 'medium', 'strong', 'required')


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
    #: The list of user-specified constraints or constraint-generating
    #: objects for this component.
    constraints = d_(List())

    #: How strongly a component hugs it's width hint. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. The
    #: default is 'strong'. This can be overridden on a per-control
    #: basis to specify a logical default for the given control. This
    #: is equivalent to the following constraint:
    #:
    #:     (width == hint) | hug_width
    hug_width = d_(PolicyEnum('strong'))

    #: How strongly a component hugs it's height hint. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. The
    #: default is 'strong'. This can be overridden on a per-control
    #: basis to specify a logical default for the given control. This
    #: is equivalent to the following constraint:
    #:
    #:     (height == hint) | hug_height
    hug_height = d_(PolicyEnum('strong'))

    #: How strongly a component resists clipping its width hint. Valid
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'.
    #: The default is 'strong'. This can be overridden on a per-control
    #: basis to specify a logical default for the given control. This
    #: is equivalent to the following constraint:
    #:
    #:     (width >= hint) | resist_width
    resist_width = d_(PolicyEnum('strong'))

    #: How strongly a component resists clipping its height hint. Valid
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'.
    #: The default is 'strong'. This can be overridden on a per-control
    #: basis to specify a logical default for the given control. This
    #: is equivalent to the following constraint:
    #:
    #:     (height >= hint) | resist_height
    resist_height = d_(PolicyEnum('strong'))

    #: How strongly a component resists expanding its width hint. Valid
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'.
    #: The default is 'ignore'. This can be overridden on a per-control
    #: basis to specify a logical default for the given control. This
    #: is equivalent to the following constraint:
    #:
    #:     (width <= hint) | limit_width
    limit_width = d_(PolicyEnum('ignore'))

    #: How strongly a component resists expanding its height hint. Valid
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'.
    #: The default is 'strong'. This can be overridden on a per-control
    #: basis to specify a logical default for the given control. This
    #: is equivalent to the following constraint:
    #:
    #:     (height <= hint) | limit_height
    limit_height = d_(PolicyEnum('ignore'))

    #: A reference to the ProxyConstraintsWidget object.
    proxy = Typed(ProxyConstraintsWidget)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(
        'constraints', 'hug_width', 'hug_height', 'resist_width',
        'resist_height', 'limit_width', 'limit_height')
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
