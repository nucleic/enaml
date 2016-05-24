#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta


from future.utils import with_metaclass
import kiwisolver as kiwi


class LinearSymbolic(with_metaclass(ABCMeta, object)):
    """ An abstract base class for testing linear symbolic interfaces.

    """


LinearSymbolic.register(kiwi.Variable)
LinearSymbolic.register(kiwi.Term)
LinearSymbolic.register(kiwi.Expression)
