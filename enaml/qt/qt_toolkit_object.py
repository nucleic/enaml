#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QObject

from atom.api import Typed

from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject


class QtToolkitObject(ProxyToolkitObject):
    """ A Qt implementation of an Enaml ProxyToolkitObject.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QObject)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def init_top_down_pass(self):
        """ Initialize the proxy tree with a top-down pass.

        This method will initialize the entire tree and should only be
        called on the root object in the tree.

        """
        self.create_widget()
        self.init_widget()
        for child in self.children():
            child.init_top_down_pass()

    def init_bottom_up_pass(self):
        """ Initialize the proxy tree with a bottom-up pass.

        This method will initialize the entire tree and should only be
        called on the root object in the tree.

        """
        for child in self.children():
            child.init_bottom_up_pass()
        self.init_layout()

    def create_widget(self):
        """ Create the toolkit widget for the proxy object.

        This method is called during the top-down pass, just before the
        'init_widget()' method is called. This method should create the
        toolkit widget and assign it to the 'widget' attribute.

        """
        self.widget = QObject(self.parent_widget())

    def init_widget(self):
        """ Initialize the state of the toolkit widget.

        This method is called during the top-down pass, just after the
        'create_widget()' method is called. This method should init the
        state of the widget. The child widgets will not yet be created.

        """
        pass

    def init_layout(self):
        """ Initialize the layout of the toolkit widget.

        This method is called during the bottom-up pass. This method
        should initialize the layout of the widget. The child widgets
        will be fully initialized and layed out when this is called.

        """
        pass

    #--------------------------------------------------------------------------
    # Proxy API
    #--------------------------------------------------------------------------
    def destroy(self):
        """ A reimplemented destructor.

        This will destroy the toolkit object provided that the parent
        declaration is no already destroyed. This is so that only the
        top-most toolkit object is destroyed, saving time.

        """
        if self.widget:
            d = self.declaration.parent
            if d is None or not d.is_destroyed:
                self.widget.setParent(None)
                del self.widget
        super(QtToolkitObject, self).destroy()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def parent(self):
        """ Get the parent proxy object for this object.

        Returns
        -------
        result : QtToolkitObject or None
            The parent toolkit object of this object, or None if no
            such parent exists.

        """
        d = self.declaration.parent
        if isinstance(d, ToolkitObject):
            return d.proxy

    def children(self):
        """ Get the child objects for this object.

        Returns
        -------
        result : iterable
            An iterable of the child toolkit objects for this object.

        """
        for d in self.declaration.children:
            if isinstance(d, ToolkitObject):
                yield d.proxy

    def parent_widget(self):
        """ Get the parent toolkit widget for this object.

        Returns
        -------
        result : QObject or None
            The toolkit widget declared on the declaration parent, or
            None if there is no such parent.

        """
        d = self.parent()
        if d is not None:
            return d.widget or None

    def child_widgets(self):
        """ Get the child toolkit widgets for this object.

        Returns
        -------
        result : iterable of QObject
            The child widgets defined for this object.

        """
        for child in self.children():
            if child.widget:
                yield child.widget
