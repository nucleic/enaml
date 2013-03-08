#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .bounded_date import BoundedDate


class Calendar(BoundedDate):
    """ A bounded date control which edits a Python datetime.date using
    a widget which resembles a calendar.

    """
    # The BoundedDate interface is sufficient for a Calendar
    pass

