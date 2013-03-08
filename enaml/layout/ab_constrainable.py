#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta


class ABConstrainable(object):
    """ An abstract base class for objects that can be laid out using
    layout helpers.

    Minimally, instances need to have `top`, `bottom`, `left`, `right`,
    `width`, `height`, `v_center` and `h_center` attributes which are
    `LinearSymbolic` instances.

    """
    __metaclass__ = ABCMeta

