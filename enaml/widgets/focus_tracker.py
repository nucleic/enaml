#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import ForwardTyped, Typed

from enaml.core.declarative import d_

from .toolkit_object import ToolkitObject, ProxyToolkitObject
from .widget import Widget


class ProxyFocusTracker(ProxyToolkitObject):
    """ The abstract definition of a proxy FocusTracker object.

    """
    #: A reference to the FocusTracker declaration.
    declaration = ForwardTyped(lambda: FocusTracker)


class FocusTracker(ToolkitObject):
    """ An object which tracks the global application focus widget.

    """
    #: The application widget with the current input focus. This will
    #: be None if no widget in the application has focus, or if the
    #: focused widget does not directly correspond to an Enaml widget.
    focused_widget = d_(Typed(Widget), writable=False)

    #: A reference to the ProxyFocusTracker object.
    proxy = Typed(ProxyFocusTracker)
