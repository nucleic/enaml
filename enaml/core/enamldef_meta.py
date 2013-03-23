#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import AtomMeta


class EnamlDefMeta(AtomMeta):
    """ The metaclass which creates types for the 'enamldef' keyword.

    """
    def __repr__(cls):
        """ A nice repr for a type created by the `enamldef` keyword.

        """
        return "<enamldef '%s.%s'>" % (cls.__module__, cls.__name__)

    def __call__(cls, parent=None, **kwargs):
        """ A custom instance creation routine for EnamlDef classes.

        """
        self = cls.__new__(cls)
        for node in cls.__constructs__:
            self._construct(node, {})
        self.__init__(parent, **kwargs)
        return self
