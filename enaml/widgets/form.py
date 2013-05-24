#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import set_default

from enaml.layout.layout_helpers import align, vertical, horizontal, spacer

from .constraints_widget import ConstraintMember
from .container import Container


class Form(Container):
    """ A Container subclass that arranges its children in two columns.

    The left column is typically Labels (but this is not a requirement).
    The right are the actual widgets for data entry. The children should
    be in alternating label/widget order. If there are an odd number
    of children, the last child will span both columns.

    The Form provides an extra constraint variable, 'midline', which
    is used as the alignment anchor for the columns.

    """
    #: The ConstraintVariable giving the midline along which the labels
    #: and widgets are aligned.
    midline = ConstraintMember()

    #: A form hugs its height strongly by default. Forms are typcially
    #: used to display vertical arrangements of widgets, with forms
    #: often being stacked on top of each other. For this case, hugging
    #: the height is desired.
    hug_height = set_default('strong')

    def layout_constraints(self):
        """ Get the layout constraints for a Form.

        A Form supplies default constraints which will arrange the
        children in a two column layout. User defined 'constraints'
        will be added on top of the generated form constraints.

        """
        # FIXME: do something sensible when children are not visible.
        children = self.widgets()
        labels = children[::2]
        widgets = children[1::2]
        n_labels = len(labels)
        n_widgets = len(widgets)
        if n_labels != n_widgets:
            if n_labels > n_widgets:
                odd_child = labels.pop()
            else:
                odd_child = widgets.pop()
        else:
            odd_child = None

        # Boundary flex spacer
        b_flx = spacer(0).flex()

        # Inter-widget flex spacer
        w_flx = spacer(10).flex()

        # Generate the row constraints and make the column stacks
        midline = self.midline
        top = self.contents_top
        left = self.contents_left
        right = self.contents_right
        constraints = self.constraints[:]
        column1 = [top, b_flx]
        column2 = [top, b_flx]
        push = constraints.append
        push_col1 = column1.append
        push_col2 = column2.append
        for label, widget in zip(labels, widgets):
            push((widget.left == midline) | 'strong')
            push(align('v_center', label, widget) | 'strong')
            push(horizontal(left, b_flx, label, w_flx, widget, b_flx, right))
            push_col1(label)
            push_col1(w_flx)
            push_col2(widget)
            push_col2(w_flx)

        # Handle the odd child and create the column constraints
        if odd_child is not None:
            push_col1(odd_child)
            push_col2(odd_child)
            push(horizontal(left, b_flx, odd_child, b_flx, right))
        else:
            column1.pop()
            column2.pop()
        bottom = self.contents_bottom
        push_col1(b_flx)
        push_col1(bottom)
        push_col2(b_flx)
        push_col2(bottom)
        push(vertical(*column1))
        push(vertical(*column2))

        return constraints
