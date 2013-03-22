#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import AtomMeta


class EnamlDefMeta(AtomMeta):
    """ The type of an enamldef.

    This is a metaclass used to create types for the 'enamldef' keyword.
    The metaclass serves primarily to distinguish between types created
    by 'enamldef' and those created by traditional subclassing.

    """
    def __repr__(cls):
        """ A nice repr for a type created by the `enamldef` keyword.

        """
        return "<enamldef '%s.%s'>" % (cls.__module__, cls.__name__)

    def __call__(cls, parent=None, **kwargs):
        """ A custom instance creation routine for EnamlDef classes.

        This constructor will populate an instance before calling
        the __init__ method on the instance.

        """
        self = cls.__new__(cls)
        c = getattr(cls, '__construct__', None)
        if c is not None:
            self._populate(c, {})
            #for child in c.child_defs:
            #    print 'creating', child.typeclass
            #    instance = child.typeclass()
            #    instance.set_parent(self)

        #for descr, f_globals in cls.__descriptions__:
        #    self._populate(descr, {}, f_globals)
        self.__init__(parent, **kwargs)
        return self
