#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys


if sys.platform == 'win32':
    MONO_FONT = '12pt Consolas'
elif sys.platform == 'darwin':
    MONO_FONT = '12pt Menlo'
else:
    MONO_FONT = '12pt Courier'
