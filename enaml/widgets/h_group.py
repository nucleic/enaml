#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Int, Typed, observe

from enaml.core.declarative import d_
from enaml.layout.layout_helpers import align, hbox
from enaml.layout.spacers import Spacer

from .container import Container


class HGroup(Container):
    """ A Container subclass which groups child widgets horizontally.

    User constraints are applied *in addition* to the horizontal group
    constraints. Widgets are aligned along their vertical center.

    """
    #: The horizontal spacing to place between widgets.
    spacing = d_(Int(10))

    #: The optional spacer to add as the first layout item.
    leading_spacer = d_(Typed(Spacer))

    #: The optional spacer to add as the last layout item.
    trailing_spacer = d_(Typed(Spacer))

    #: Whether to align the widths of the widgets.
    align_widths = d_(Bool(True))

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('spacing', 'leading_spacer', 'trailing_spacer', 'align_widths')
    def _layout_invalidated(self, change):
        """ A private observer which invalidates the layout.

        """
        # The superclass handler is sufficient.
        super(HGroup, self)._layout_invalidated(change)

    #--------------------------------------------------------------------------
    # Layout Constraints
    #--------------------------------------------------------------------------
    def layout_constraints(self):
        """ The constraints generation for a HGroup.

        This method supplies horizontal group constraints for the
        children of the container in addition to any user-supplied
        constraints.

        This method cannot be overridden from Enaml syntax.

        """
        widgets = self.visible_widgets()
        items = [self.leading_spacer] + widgets + [self.trailing_spacer]
        cns = self.constraints[:]
        cns.append(hbox(*items, spacing=self.spacing))
        cns.append(align('v_center', *widgets))
        if self.align_widths:
            cns.append(align('width', *widgets))
        return cns
