#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .declarative import DeclarativeMeta


class EnamlDefMeta(DeclarativeMeta):
    """ The metaclass which creates types for the 'enamldef' keyword.

    """
    #: Class level storage for the compiler node. This is populated by
    #: the compiler when the enamldef class is created. It should not
    #: be modified by user code.
    __node__ = None

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
