#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed, ForwardTyped

from enaml.application import Application
from enaml.core.declarative import Declarative


class ProxyToolkitObject(Atom):
    """ The base class of all proxy toolkit objects.

    A ProxyToolkitObject is repsonsible for the communication between
    the Declarative declaration of the object and then implementation
    object which actually performs the behavior.

    """
    #: A reference to the ToolkitObject declaration.
    declaration = ForwardTyped(lambda: ToolkitObject)

    def destroy(self):
        """ Destroy the proxy and any of its resources.

        This method is called by the declaration when it is destroyed.
        It should be reimplemented by subclasses when more control
        is required.

        """
        del self.declaration


class ToolkitObject(Declarative):
    """ The base class of all toolkit objects in Enaml.

    """
    #: A reference to the ProxyToolkitObject
    proxy = Typed(ProxyToolkitObject)

    def __init__(self, parent=None, **kwargs):
        """ Initialize a ToolkitObject.

        """
        super(ToolkitObject, self).__init__(parent, **kwargs)
        app = Application.instance()
        if app is not None:
            self.proxy = app.create_proxy(self)
        else:
            msg = 'the Application must be created before creating any '
            msg += 'instances of ToolkitObject'
            raise RuntimeError(msg)

    def destroy(self):
        """ A reimplemented destructor.

        This destructor invokes the 'destroy' method on the proxy
        toolkit object.

        """
        super(ToolkitObject, self).destroy()
        self.proxy.destroy()

    def _update_proxy(self, change):
        """ Update the proxy widget when the Widget data changes.

        This method only updates the proxy when an attribute is updated;
        not when it is created or deleted. It is useful for subclasses
        as a base observer handler

        """
        if change['type'] == 'updated':
            handler = getattr(self.proxy, 'set_' + change['name'], None)
            if handler is not None:
                handler(change['newvalue'])
