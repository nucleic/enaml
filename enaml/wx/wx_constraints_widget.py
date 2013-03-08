#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from casuarius import ConstraintVariable

from .wx_widget import WxWidget


class LayoutBox(object):
    """ A class which encapsulates a layout box using casuarius
    constraint variables.

    The constraint variables are created on an as-needed basis, this
    allows Enaml widgets to define new constraints and build layouts
    with them, without having to specifically update this client
    code.

    """
    def __init__(self, name, owner):
        """ Initialize a LayoutBox.

        Parameters
        ----------
        name : str
            A name to use in the label for the constraint variables in
            this layout box.

        owner : str
            The owner id to use in the label for the constraint variables
            in this layout box.

        """
        self._name = name
        self._owner = owner
        self._primitives = {}

    def primitive(self, name):
        """ Returns a primitive casuarius constraint variable for the
        given name.

        Parameters
        ----------
        name : str
            The name of the constraint variable to return.

        """
        primitives = self._primitives
        if name in primitives:
            res = primitives[name]
        else:
            label = '{0}|{1}|{2}'.format(self._name, self._owner, name)
            res = primitives[name] = ConstraintVariable(label)
        return res


class WxConstraintsWidget(WxWidget):
    """ A Wx implementation of an Enaml ConstraintsWidget.

    """
    #: The hug strengths for the widget's size hint.
    _hug = ('strong', 'strong')

    #: The resist strengths for the widget's size hint.
    _resist = ('strong', 'strong')

    #: The list of hard constraints which must be applied to the widget.
    #: These constraints are computed lazily and only once since they
    #: are assumed to never change.
    _hard_cns = []

    #: The list of size hint constraints to apply to the widget. These
    #: constraints are computed once and then cached. If the size hint
    #: of a widget changes at run time, then `size_hint_updated` should
    #: be called to trigger an appropriate relayout of the widget.
    _size_hint_cns = []

    #: The list of constraint dictionaries defined by the user on
    #: the server side Enaml widget.
    _user_cns = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, tree):
        """ Create and initialize the control.

        """
        super(WxConstraintsWidget, self).create(tree)
        layout = tree['layout']
        self.layout_box = LayoutBox(type(self).__name__, self.object_id())
        self._hug = layout['hug']
        self._resist = layout['resist']
        self._user_cns = layout['constraints']

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_relayout(self, content):
        """ Handle the 'relayout' action from the Enaml widget.

        """
        # XXX The WxContainer needs to get in on the action to grab the
        # share_layout flag.
        self._hug = content['hug']
        self._resist_clip = content['resist']
        self._user_cns = content['constraints']
        self.clear_size_hint_constraints()
        self.relayout()

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def relayout(self):
        """ Peform a relayout for this constraints widget.

        The default behavior of this method is to proxy the call up the
        tree of ancestors until it is either handled by a subclass which
        has reimplemented this method (see WxContainer), or the ancestor
        is not an instance of WxConstraintsWidget, at which point the
        layout request is dropped.

        """
        parent = self.parent()
        if isinstance(parent, WxConstraintsWidget):
            parent.relayout()

    def replace_constraints(self, old_cns, new_cns):
        """ Replace constraints in the current layout system.

        The default behavior of this method is to proxy the call up the
        tree of ancestors until it is either handled by a subclass which
        has reimplemented this method (see WxContainer), or the ancestor
        is not an instance of WxConstraintsWidget, at which point the
        request is dropped.

        Parameters
        ----------
        old_cns : list
            The list of casuarius constraints to remove from the
            current layout system.

        new_cns : list
            The list of casuarius constraints to add to the
            current layout system.

        """
        parent = self.parent()
        if isinstance(parent, WxConstraintsWidget):
            parent.replace_constraints(old_cns, new_cns)

    def clear_constraints(self, cns):
        """ Clear the given constraints from the current layout system.

        The default behavior of this method is to proxy the call up the
        tree of ancestors until it is either handled by a subclass which
        has reimplemented this method (see WxContainer), or the ancestor
        is not an instance of WxConstraintsWidget, at which point the
        request is dropped. This method will *not* trigger a relayout.

        Parameters
        ----------
        cns : list
            The list of casuarius constraints to remove from the
            current layout system.

        """
        parent = self.parent()
        if isinstance(parent, WxConstraintsWidget):
            parent.clear_constraints(cns)

    def size_hint_constraints(self):
        """ Creates the list of size hint constraints for this widget.

        This method uses the provided size hint of the widget and the
        policies for 'hug' and 'resist_clip' to generate casuarius
        LinearConstraint objects which respect the size hinting of the
        widget.

        If the size hint of the underlying widget is not valid, then
        no constraints will be generated.

        Returns
        -------
        result : list
            A list of casuarius LinearConstraint instances.

        """
        cns = self._size_hint_cns
        if not cns:
            cns = self._size_hint_cns = []
            push = cns.append
            hint = self.widget().GetBestSize()
            if hint.IsFullySpecified():
                width_hint = hint.width
                height_hint = hint.height
                primitive = self.layout_box.primitive
                width = primitive('width')
                height = primitive('height')
                hug_width, hug_height = self._hug
                resist_width, resist_height = self._resist
                if width_hint >= 0:
                    if hug_width != 'ignore':
                        cn = (width == width_hint) | hug_width
                        push(cn)
                    if resist_width != 'ignore':
                        cn = (width >= width_hint) | resist_width
                        push(cn)
                if height_hint >= 0:
                    if hug_height != 'ignore':
                        cn = (height == height_hint) | hug_height
                        push(cn)
                    if resist_height != 'ignore':
                        cn = (height >= height_hint) | resist_height
                        push(cn)
        return cns

    def size_hint_updated(self):
        """ Notify the layout system that the size hint of this widget
        has been updated.

        """
        # Only the ancestors of a widget care about its size hint,
        # so this method attempts to replace the size hint constraints
        # for the widget starting with its parent.
        parent = self.parent()
        if isinstance(parent, WxConstraintsWidget):
            old_cns = self._size_hint_cns
            self._size_hint_cns = []
            new_cns = self.size_hint_constraints()
            parent.replace_constraints(old_cns, new_cns)
        self.update_geometry()

    def clear_size_hint_constraints(self):
        """ Clear the size hint constraints from the layout system.

        """
        # Only the ancestors of a widget care about its size hint,
        # so this method attempts to replace the size hint constraints
        # for the widget starting with its parent.
        parent = self.parent()
        if isinstance(parent, WxConstraintsWidget):
            cns = self._size_hint_cns
            self._size_hint_cns = []
            parent.clear_constraints(cns)

    def hard_constraints(self):
        """ Generate the constraints which must always be applied.

        These constraints are generated once the first time this method
        is called. The results are then cached and returned immediately
        on future calls.

        Returns
        -------
        result : list
            A list of casuarius LinearConstraint instance.

        """
        cns = self._hard_cns
        if not cns:
            primitive = self.layout_box.primitive
            left = primitive('left')
            top = primitive('top')
            width = primitive('width')
            height = primitive('height')
            cns = [left >= 0, top >= 0, width >= 0, height >= 0]
            self._hard_cns = cns
        return cns

    def user_constraints(self):
        """ Get the list of user constraints defined for this widget.

        The default implementation returns the list of constraint
        information sent by the server.

        Returns
        -------
        result : list
            The list of dictionaries which represent the user defined
            linear constraints.

        """
        return self._user_cns

    def geometry_updater(self):
        """ A method which can be called to create a function which
        will update the layout geometry of the underlying widget.

        The parameter and return values below describe the function
        that is returned by calling this method.

        Parameters
        ----------
        dx : float
            The offset of the parent widget from the computed origin
            of the layout. This amount is subtracted from the computed
            layout 'x' amount, which is expressed in the coordinates
            of the owner widget.

        dy : float
            The offset of the parent widget from the computed origin
            of the layout. This amount is subtracted from the computed
            layout 'y' amount, which is expressed in the coordinates
            of the layout owner widget.

        Returns
        -------
        result : (x, y)
            The computed layout 'x' and 'y' amount, expressed in the
            coordinates of the layout owner widget.

        """
        # The return function is a hyper optimized (for Python) closure
        # that will is called on every resize to update the geometry of
        # the widget. This is explicitly not idiomatic Python code. It
        # exists purely for the sake of efficiency and was justified
        # with profiling.
        primitive = self.layout_box.primitive
        x = primitive('left')
        y = primitive('top')
        width = primitive('width')
        height = primitive('height')
        setdims = self.widget().SetDimensions
        def update_geometry(dx, dy):
            nx = x.value
            ny = y.value
            setdims(nx - dx, ny - dy, width.value, height.value)
            return nx, ny
        # Store a reference to self on the updater, so that the layout
        # container can know the object on which the updater operates.
        update_geometry.item = self
        return update_geometry

