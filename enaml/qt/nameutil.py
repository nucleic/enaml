#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from itertools import count

_counter = count()


def make_name(name):
    return name + '-%d' % _counter.next()


def clean_name(name):
    return name.rsplit('-', 1)[0]
