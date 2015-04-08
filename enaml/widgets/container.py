#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Coerced, ForwardTyped, Typed, observe, set_default

from enaml.core.declarative import d_, d_func
from enaml.layout.constrainable import ContentsConstrainableMixin
from enaml.layout.geometry import Box
from enaml.layout.layout_helpers import vbox

from .constraints_widget import ConstraintsWidget
from .frame import Frame, ProxyFrame


class ProxyContainer(ProxyFrame):
    """ The abstract definition of a proxy Container object.

    """
    #: A reference to the Container declaration.
    declaration = ForwardTyped(lambda: Container)


class Container(Frame, ContentsConstrainableMixin):
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

    #: A box object which holds the padding for this component. The
    #: padding is the amount of space between the outer boundary box
    #: and the content box. The default padding is 10 pixels a side.
    #: Certain subclasses, such as GroupBox, may provide additional
    #: margin than what is specified by the padding.
    padding = d_(Coerced(Box, (10, 10, 10, 10)))

    #: A Container does not generate constraints for its size hint by
    #: default. The minimum and maximum size constraints are sufficient
    #: to supply size limits and make for the most natural interaction
    #: between nested containers.
    resist_width = set_default('ignore')
    resist_height = set_default('ignore')
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

    def visible_widgets(self):
        """ Get the visible child ConstraintsWidgets on the container.

        """
        return [w for w in self.widgets() if w.visible]

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event on the container.

        This event handler will request a relayout if the added child
        is an instance of 'ConstraintsWidget'.

        """
        # Request the relayout first so that the widget's updates are
        # disabled before the child is actually added.
        if isinstance(child, ConstraintsWidget):
            self.request_relayout()
        super(Container, self).child_added(child)

    def child_moved(self, child):
        """ Handle the child moved event on the container.

        This event handler will request a relayout if the moved child
        is an instance of 'ConstraintsWidget'.

        """
        # Request the relayout first so that the widget's updates are
        # disabled before the child is actually moved.
        if isinstance(child, ConstraintsWidget):
            self.request_relayout()
        super(Container, self).child_moved(child)

    def child_removed(self, child):
        """ Handle the child removed event on the container.

        This event handler will request a relayout if the removed child
        is an instance of 'ConstraintsWidget'.

        """
        # Request the relayout first so that the widget's updates are
        # disabled before the child is actually removed.
        if isinstance(child, ConstraintsWidget):
            self.request_relayout()
        super(Container, self).child_removed(child)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('share_layout', 'padding')
    def _layout_invalidated(self, change):
        """ A private observer which invalidates the layout.

        """
        # The superclass handler is sufficient.
        super(Container, self)._layout_invalidated(change)

    #--------------------------------------------------------------------------
    # Layout Constraints
    #--------------------------------------------------------------------------
    @d_func
    def layout_constraints(self):
        """ The constraints generation for a Container.

        This method supplies default vbox constraints to the visible
        children of the container unless the user has given explicit
        'constraints'.

        This method may also be overridden from Enaml syntax.

        """
        if self.constraints:
            return self.constraints
        return [vbox(*self.visible_widgets())]
