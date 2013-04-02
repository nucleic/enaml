#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

import wx

from atom.api import List, Typed

from enaml.widgets.constraints_widget import ProxyConstraintsWidget

from .wx_widget import WxWidget


@contextmanager
def size_hint_guard(obj):
    """ A contenxt manager for guarding the size hint of a widget.

    This manager will call `size_hint_updated` if the size hint of the
    widget changes during context execution.

    Parameters
    ----------
    obj : QtConstraintsWidget
        The constraints widget with the size hint of interest.

    """
    old_hint = obj.widget.GetBestSize()
    yield
    new_hint = obj.widget.GetBestSize()
    if old_hint != new_hint:
        obj.size_hint_updated()


class wxLayoutTimer(wx.Timer):
    """ A custom wx Timer which for collapsing layout requests.

    """
    def __init__(self, owner):
        super(wxLayoutTimer, self).__init__()
        self.owner = owner

    def Release(self):
        self.owner = None

    def Notify(self):
        self.owner.on_layout_triggered()


class WxConstraintsWidget(WxWidget, ProxyConstraintsWidget):
    """ A Wx implementation of an Enaml ProxyConstraintsWidget.

    """
    #: The list of size hint constraints to apply to the widget. These
    #: constraints are computed once and then cached. If the size hint
    #: of a widget changes at run time, then `size_hint_updated` should
    #: be called to trigger an appropriate relayout of the widget.
    size_hint_cns = List()

    #: A timer used to collapse relayout requests. The timer is created
    #: on an as needed basis and destroyed when it is no longer needed.
    layout_timer = Typed(wxLayoutTimer)

    def _default_size_hint_cns(self):
        """ Creates the list of size hint constraints for this widget.

        This method uses the provided size hint of the widget and the
        policies for 'hug' and 'resist' to generate constraints which
        respect the size hinting of the widget.

        If the size hint of the underlying widget is not valid, then
        no constraints will be generated.

        Returns
        -------
        result : list
            A list of casuarius LinearConstraint instances.

        """
        cns = []
        hint = self.widget.GetBestSize()
        if hint.IsFullySpecified():
            width_hint = hint.width
            height_hint = hint.height
            d = self.declaration
            if width_hint >= 0:
                if d.hug_width != 'ignore':
                    cns.append((d.width == width_hint) | d.hug_width)
                if d.resist_width != 'ignore':
                    cns.append((d.width >= width_hint) | d.resist_width)
            if height_hint >= 0:
                if d.hug_height != 'ignore':
                    cns.append((d.height == height_hint) | d.hug_height)
                if d.resist_height != 'ignore':
                    cns.append((d.height >= height_hint) | d.resist_height)
        return cns

    #--------------------------------------------------------------------------
    # ProxyConstraintsWidget API
    #--------------------------------------------------------------------------
    def request_relayout(self):
        """ Request a relayout of the proxy widget.

        This call will be placed on a collapsed timer. The first request
        will cause updates to be disabled on the widget. The updates will
        be reenabled after the actual relayout is performed.

        """
        if not self.layout_timer:
            self.widget.Freeze()
            self.layout_timer = wxLayoutTimer(self)
        self.layout_timer.Start(1, oneShot=True)

    def on_layout_triggered(self):
        """ Handle the timeout even from the layout trigger timer.

        This handler will drop the reference to the timer, invoke the
        'relayout' method, and reenable the updates on the widget.

        """
        self.layout_timer.Release()
        del self.layout_timer
        self.relayout()
        self.widget.Thaw()

    #--------------------------------------------------------------------------
    # Public API
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

    def size_hint_updated(self):
        """ Notify the layout system that the size hint has changed.

        This method should be called when the size hint of the widget has
        changed and the layout should be refreshed to reflect the new
        state of the widget.

        """
        # Only the ancestors of a widget care about its size hint and
        # will have added those constraints to a layout, so this method
        # attempts to replace the size hint constraints for the widget
        # starting with its parent.
        parent = self.parent()
        if isinstance(parent, WxConstraintsWidget):
            old_cns = self.size_hint_cns
            del self.size_hint_cns
            new_cns = self.size_hint_cns
            parent.replace_constraints(old_cns, new_cns)
        self.update_geometry()

    def geometry_updater(self):
        """ Create a layout function for the widget.

        This method will create a function which will update the
        layout geometry of the underlying widget. The parameter and
        return values below describe the function that is returned by
        calling this method.

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
        # that will be called on every resize to update the geometry of
        # the widget. According to cProfile, executing the body of this
        # closure is 2x faster than the call to QWidgetItem.setGeometry.
        # The previous version of this method, `update_layout_geometry`,
        # was 5x slower. This is explicitly not idiomatic Python code.
        # It exists purely for the sake of efficiency, justified with
        # profiling.
        d = self.declaration
        x = d.left
        y = d.top
        width = d.width
        height = d.height
        setdims = self.widget.SetDimensions

        def update_geometry(dx, dy):
            nx = x.value
            ny = y.value
            setdims(nx - dx, ny - dy, width.value, height.value)
            return nx, ny

        # Store a reference to self on the updater, so that the layout
        # container can know the object on which the updater operates.
        update_geometry.item = self
        return update_geometry
