#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .declarative_meta import DeclarativeMeta


def __enamldef_newobj__(cls, *args):
    """ An enamldef pickler function.

    This function is not part of the public Enaml api.

    """
    instance = cls.__new__(cls, *args)
    cls.__node__(instance)
    return instance


def __reduce_ex__(self, proto):
    """ An implementation of the reduce protocol.

    This method creates a reduction tuple for enamldef instances. It
    is not part of the public Enaml api.

    """
    args = (type(self),) + self.__getnewargs__()
    return (__enamldef_newobj__, args, self.__getstate__())


class EnamlDefMeta(DeclarativeMeta):
    """ The metaclass which creates types for the 'enamldef' keyword.

    """
    #: Class level storage for the compiler node. This is populated by
    #: the compiler when the enamldef class is created. It should not
    #: be modified by user code.
    __node__ = None

    def __new__(meta, name, bases, dct):
        """ Create a new enamldef subclass.

        This method overrides the default Atom pickle reducer with one
        which invokes the Enaml compiler node during unpickling.

        """
        cls = DeclarativeMeta.__new__(meta, name, bases, dct)
        if cls.__reduce_ex__ is not __reduce_ex__:
            cls.__reduce_ex__ = __reduce_ex__
        return cls

    def __repr__(cls):
        """ A nice repr for a type created by the `enamldef` keyword.

        """
        return "<enamldef '%s.%s'>" % (cls.__module__, cls.__name__)

    def __call__(cls, parent=None, **kwargs):
        """ Create a new instance of the enamldef class.

        This method will create the new instance, then populate that
        instance with children defined in the enamldef. Once those
        children are added, the __init__ method of the instance will
        be invoked with the provided arguments.

        Parameters
        ----------
        parent : Object or None
            The parent object of the new instance.

        **kwargs
            Additional keyword arguments to pass to the constructor.

        """
        instance = cls.__new__(cls)
        cls.__node__(instance)
        instance.__init__(parent, **kwargs)
        return instance
