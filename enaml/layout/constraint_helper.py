#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom

from .strength_member import StrengthMember


class ConstraintHelper(Atom):
    """ A base class for defining constraint helper objects.

    """
    #: An optional strength to apply to the generated constraints.
    strength = StrengthMember()

    def __or__(self, strength):
        """ Override the strength of the generated constraints.

        Parameters
        ----------
        strength : strength-like
            The strength to apply to the generated constraints.

        Returns
        -------
        result : self
            The current helper instance.

        """
        self.strength = strength
        return self

    def when(self, switch):
        """ A simple switch method to toggle a helper.

        Parameters
        ----------
        switch : bool
            Whether or not the helper should be active.

        Returns
        -------
        result : self or None
            The current instance if the switch is True, None otherwise.

        """
        return self if switch else None

    def create_constraints(self, component):
        """ Called to generate the constraints for the component.

        Parameters
        ----------
        component : Constrainable or None
            The constrainable object which represents the conceptual
            owner of the generated constraints. This will typically
            be a Container or some other constrainable object which
            represents the boundaries of the generated constraints.
            None will be passed when no outer component is available.

        Returns
        -------
        result : list
            The list of Constraint objects for the given component.

        """
        cns = self.constraints(component)
        strength = self.strength
        if strength is not None:
            cns = [cn | strength for cn in cns]
        return cns

    def constraints(self, component):
        """ Generate the constraints for the given component.

        This abstract method which must be implemented by subclasses.

        Parameters
        ----------
        component : Constrainable or None
            The constrainable object which represents the conceptual
            owner of the generated constraints. This will typically
            be a Container or some other constrainable object which
            represents the boundaries of the generated constraints.
            None will be passed when no outer component is available.

        Returns
        -------
        result : list
            The list of Constraint objects for the given component.

        """
        raise NotImplementedError
