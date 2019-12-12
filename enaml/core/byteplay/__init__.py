#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from ...compat import USE_WORDCODE

if USE_WORDCODE:
    from .wbyteplay import *
else:
    from .byteplay3 import *
