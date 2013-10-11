#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
class ObjectDict(dict):
    """ A dict subclass which allows access by named attribute.

    """
    __slots__ = ()

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        msg = "'%s' object has no attribute '%s'"
        raise AttributeError(msg % (type(self).__name__, attr))
