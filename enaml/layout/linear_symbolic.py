#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta

import kiwisolver as kiwi


class LinearSymbolic(object, metaclass=ABCMeta):
    """ An abstract base class for testing linear symbolic interfaces.

    """


LinearSymbolic.register(kiwi.Variable)
LinearSymbolic.register(kiwi.Term)
LinearSymbolic.register(kiwi.Expression)
