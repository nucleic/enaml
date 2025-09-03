#------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped

from .bounded_date import BoundedDate, ProxyBoundedDate


class ProxyCalendar(ProxyBoundedDate):
    """ The abstract definition of a proxy Calendar object.

    """
    #: A reference to the Calendar declaration.
    declaration = ForwardTyped(lambda: Calendar)


class Calendar(BoundedDate):
    """ A bounded date control which edits a Python datetime.date using
    a widget which resembles a calendar.

    """
    #: A reference to the ProxyCalendar object.
    proxy = Typed(ProxyCalendar)
