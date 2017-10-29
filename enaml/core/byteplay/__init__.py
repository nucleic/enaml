#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from ...compat import IS_PY3, USE_WORDCODE

if USE_WORDCODE:
    from .wbyteplay import *
elif not IS_PY3:
    from .byteplay2 import *
else:
    from .byteplay3 import *
