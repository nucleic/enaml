#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------


def repolish(widget):
    """ Repolish a widget when the stylesheet dependencies change.

    Parameters
    ----------
    widget : QWidget
        The widget to repolish.

    """
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
