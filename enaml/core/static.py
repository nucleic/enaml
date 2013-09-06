#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
class Static(object):
    """ A descriptor which holds the value of a static attribute.

    """
    __slots__ = ('_name', '_value')

    def __init__(self, name, value):
        """ Initialize a Static descriptor.

        Parameters
        ----------
        name : str
            The name of the static attribute.

        value : object
            The value of the static attribute.

        """
        self._name = name
        self._value = value

    def __get__(self, obj, cls):
        return self._value

    def __set__(self, obj, value):
        raise TypeError("static attribute '%s' is read-only" % self._name)

    def __delete__(self, obj):
        raise TypeError("static attribute '%s' is read-only" % self._name)
