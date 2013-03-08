#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Unicode


class Validator(Atom):
    """ The base class for creating widget text validators.

    This class is abstract. It's abstract api must be implemented by a
    subclass in order to be usable.

    """
    #: An optional message to associate with the validator. This message
    #: will be sent to the client widget if server side validation fails
    message = Unicode()

    def validate(self, text, component):
        """ Validates the given text.

        This is an abstract method which must be implemented by
        sublasses.

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        component : Declarative
            The declarative component currently making use of the
            validator.

        Returns
        -------
        result : (unicode, bool)
            A 2-tuple of (optionally modified) unicode text, and whether
            or not that text should be considered valid.

        """
        raise NotImplementedError

    def client_validator(self):
        """ A serializable representation of a client side validator.

        Returns
        -------
        result : dict or None
            A dict in the format specified by 'validator_format.js'
            or None if no client validator is specified. The default
            implementation of this method returns None.

        """
        return None
