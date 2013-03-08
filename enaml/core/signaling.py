#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import warnings


warnings.warn(
    'Importing from enaml.core.signaling is deprectated. '
    'Use enaml.signaling instead.', DeprecationWarning
)

# Backwards compatibility imports
from enaml.signaling import Signal, BoundSignal as InstanceSignal

