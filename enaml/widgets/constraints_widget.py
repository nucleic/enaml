#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    DefaultValue, Enum, Typed, List, Constant, ForwardTyped, observe
)

from casuarius import ConstraintVariable

from enaml.core.declarative import d_
from enaml.layout.ab_constrainable import ABConstrainable
from enaml.layout.layout_helpers import expand_constraints

from .widget import Widget, ProxyWidget


#: An atom enum which defines the allowable constraints strengths.
#: Clones will be made by selecting a new default via 'select'.
PolicyEnum = Enum('ignore', 'weak', 'medium', 'strong', 'required')


class ConstraintMember(Constant):
    """ A custom Member class that generates a ConstraintVariable.

    """
    __slots__ = ()

    def __init__(self):
        super(ConstraintMember, self).__init__()
        mode = DefaultValue.MemberMethod_Object
        self.set_default_value_mode(mode, "default")

    def default(self, owner):
        """ Create the constraint variable for the member.

        """
        return ConstraintVariable(self.name)


class ProxyConstraintsWidget(ProxyWidget):
    """ The abstract definition of a proxy ConstraintsWidget object.

    """
    #: A reference to the ConstraintsWidget declaration.
    declaration = ForwardTyped(lambda: ConstraintsWidget)

    def request_relayout(self):
        raise NotImplementedError


class ConstraintsWidget(Widget):
    """ A Widget subclass which adds constraint information.

    A ConstraintsWidget is augmented with symbolic constraint variables
    which define a box model on the widget. This box model is used to
    declare constraints between this widget and other components which
    participate in constraints-based layout.

    Constraints are added to a widget by assigning a list to the
    'constraints' attribute. This list may contain raw LinearConstraint
    objects (which are created by manipulating the symbolic constraint
    variables) or DeferredConstraints objects which generated these
    LinearConstraint objects on-the-fly.

    """
    #: The list of user-specified constraints or constraint-generating
    #: objects for this component.
    constraints = d_(List())

    #: A constant symbolic object that represents the left boundary of
    #: the widget.
    left = ConstraintMember()

    #: A constant symbolic object that represents the top boundary of
    #: the widget.
    top = ConstraintMember()

    #: A constant symbolic object that represents the width of the
    #: widget.
    width = ConstraintMember()

    #: A constant symbolic object that represents the height of the
    #: widget.
    height = ConstraintMember()

    #: A constant symbolic object that represents the right boundary
    #: of the component. This is computed as left + width.
    right = Constant()

    def _default_right(self):
        return self.left + self.width

    #: A constant symbolic object that represents the bottom boundary
    #: of the component. This is computed as top + height.
    bottom = Constant()

    def _default_bottom(self):
        return self.top + self.height

    #: A constant symbolic object that represents the vertical center
    #: of the width. This is computed as top + 0.5 * height.
    v_center = Constant()

    def _default_v_center(self):
        return self.top + self.height / 2.0

    #: A constant symbolic object that represents the horizontal center
    #: of the widget. This is computed as left + 0.5 * width.
    h_center = Constant()

    def _default_h_center(self):
        return self.left + self.width / 2.0

    #: How strongly a component hugs it's width hint. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. Default
    #: is 'strong'. This can be overridden on a per-control basis to
    #: specify a logical default for the given control.
    hug_width = d_(PolicyEnum('strong'))

    #: How strongly a component hugs it's height hint. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. Default
    #: is 'strong'. This can be overridden on a per-control basis to
    #: specify a logical default for the given control.
    hug_height = d_(PolicyEnum('strong'))

    #: How strongly a component resists clipping its contents. Valid
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'.
    #: The default is 'strong' for width.
    resist_width = d_(PolicyEnum('strong'))

    #: How strongly a component resists clipping its contents. Valid
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'.
    #: The default is 'strong' for height.
    resist_height = d_(PolicyEnum('strong'))

    #: A reference to the ProxyConstraintsWidget object.
    proxy = Typed(ProxyConstraintsWidget)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('constraints', 'hug_width', 'hug_height', 'resist_width',
        'resist_height'))
    def _layout_invalidated(self, change):
        """ An observer which will relayout the proxy widget.

        """
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


ABConstrainable.register(ConstraintsWidget)
