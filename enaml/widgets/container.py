#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, Constant, Coerced, ForwardTyped, Typed, observe, set_default
)

from enaml.core.declarative import d_
from enaml.layout.geometry import Box
from enaml.layout.layout_helpers import vbox

from .constraints_widget import ConstraintsWidget, ConstraintMember
from .frame import Frame, ProxyFrame


class ProxyContainer(ProxyFrame):
    """ The abstract definition of a proxy Container object.

    """
    #: A reference to the Container declaration.
    declaration = ForwardTyped(lambda: Container)


class Container(Frame):
    """ A Frame subclass which provides child layout functionality.

    The Container is the canonical component used to arrange child
    widgets using constraints-based layout. The developer can supply
    a list of constraints on the container which specify how to layout
    it's child widgets.

    There are widgets whose boundaries constraints may not cross. Some
    examples of these would be a ScrollArea or a Notebook. See the
    documentation of a given widget as to whether or not constraints
    may cross its boundaries.

    """
    #: A boolean which indicates whether or not to allow the layout
    #: ownership of this container to be transferred to an ancestor.
    #: This is False by default, which means that every container
    #: get its own layout solver. This improves speed and reduces
    #: memory use (by keeping a solver's internal tableaux small)
    #: but at the cost of not being able to share constraints
    #: across Container boundaries. This flag must be explicitly
    #: marked as True to enable sharing.
    share_layout = d_(Bool(False))

    #: A constant symbolic object that represents the internal left
    #: boundary of the content area of the container.
    contents_left = ConstraintMember()

    #: A constant symbolic object that represents the internal right
    #: boundary of the content area of the container.
    contents_right = ConstraintMember()

    #: A constant symbolic object that represents the internal top
    #: boundary of the content area of the container.
    contents_top = ConstraintMember()

    #: A constant symbolic object that represents the internal bottom
    #: boundary of the content area of the container.
    contents_bottom = ConstraintMember()

    #: A constant symbolic object that represents the internal width of
    #: the content area of the container.
    contents_width = Constant()

    def _default_contents_width(self):
        return self.contents_right - self.contents_left

    #: A constant symbolic object that represents the internal height of
    #: the content area of the container.
    contents_height = Constant()

    def _default_contents_height(self):
        return self.contents_bottom - self.contents_top

    #: A constant symbolic object that represents the internal center
    #: along the vertical direction the content area of the container.
    contents_v_center = Constant()

    def _default_contents_v_center(self):
        return self.contents_top + self.contents_height / 2.0

    #: A constant symbolic object that represents the internal center
    #: along the horizontal direction of the content area of the container.
    contents_h_center = Constant()

    def _default_contents_h_center(self):
        return self.contents_left + self.contents_width / 2.0

    #: A box object which holds the padding for this component. The
    #: padding is the amount of space between the outer boundary box
    #: and the content box. The default padding is (10, 10, 10, 10).
    #: Certain subclasses, such as GroupBox, may provide additional
    #: margin than what is specified by the padding.
    padding = d_(Coerced(Box, (10, 10, 10, 10)))

    #: Containers freely exapnd in width and height. The size hint
    #: constraints for a Container are used when the container is
    #: not sharing its layout. In these cases, expansion of the
    #: container is typically desired.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyContainer object.
    proxy = Typed(ProxyContainer)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def widgets(self):
        """ Get the child ConstraintsWidgets defined on the container.

        """
        return [c for c in self.children if isinstance(c, ConstraintsWidget)]

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event on the container.

        This event handler will request a relayout if the added child
        is an instance of 'ConstraintsWidget'.

        """
        super(Container, self).child_added(child)
        if isinstance(child, ConstraintsWidget):
            self.request_relayout()

    def child_removed(self, child):
        """ Handle the child removed event on the container.

        This event handler will request a relayout if the removed child
        is an instance of 'ConstraintsWidget'.

        """
        super(Container, self).child_removed(child)
        if isinstance(child, ConstraintsWidget):
            self.request_relayout()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('share_layout', 'padding'))
    def _layout_invalidated(self, change):
        """ A private observer which invalidates the layout.

        """
        # The superclass handler is sufficient.
        super(Container, self)._layout_invalidated(change)

    #--------------------------------------------------------------------------
    # Layout Constraints
    #--------------------------------------------------------------------------
    def layout_constraints(self):
        """ The constraints generation for a Container.

        This method supplies default vbox constraints to the children of
        the container unless the user has given explicit 'constraints'.

        """
        cns = self.constraints[:]
        if not cns:
            cns.append(vbox(*self.widgets()))
        return cns
