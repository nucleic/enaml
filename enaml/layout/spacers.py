#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Range

import kiwisolver as kiwi

from .strength_member import StrengthMember


class Spacer(Atom):
    """ A base class for creating constraint spacers.

    """
    #: The amount of space to apply for this spacer, in pixels.
    size = Range(low=0)

    #: The optional strength to apply to the spacer constraints.
    strength = StrengthMember()

    def __init__(self, size, strength=None):
        """ Initialize a Spacer.

        Parameters
        ----------
        size : int
            The basic size of the spacer, in pixels >= 0.

        strength : strength-like, optional
            A strength to apply to the generated spacer constraints.

        """
        self.size = size
        self.strength = strength

    def __or__(self, strength):
        """ Override the strength of the generated constraints.

        Parameters
        ----------
        strength : strength-like
            The strength to apply to the generated constraints.

        Returns
        -------
        result : self
            The current spacer instance.

        """
        self.strength = strength
        return self

    def when(self, switch):
        """ A simple switch method to toggle a spacer.

        Parameters
        ----------
        switch : bool
            Whether or not the spacer should be active.

        Returns
        -------
        result : self or None
            The current instance if the switch is True, None otherwise.

        """
        return self if switch else None

    def create_constraints(self, first, second):
        """ Generate the spacer constraints for the given anchors.

        Parameters
        ----------
        first : LinearSymbolic
            A linear symbolic representing the first constraint anchor.

        second : LinearSymbolic
            A linear symbolic representing the second constraint anchor.

        Returns
        -------
        result : list
            The list of constraints for the spacer.

        """
        cns = self.constraints(first, second)
        strength = self.strength
        if strength is not None:
            cns = [cn | strength for cn in cns]
        return cns

    def constraints(self, first, second):
        """ Generate the spacer constraints for the given anchors.

        This abstract method which must be implemented by subclasses.

        Parameters
        ----------
        first : LinearSymbolic
            A linear symbolic representing the first constraint anchor.

        second : LinearSymbolic
            A linear symbolic representing the second constraint anchor.

        Returns
        -------
        result : list
            The list of constraints for the spacer.

        """
        raise NotImplementedError


class EqSpacer(Spacer):
    """ A spacer which represents a fixed amount of space.

    """
    def constraints(self, first, second):
        """ A constraint of the form: (second - first) == size

        """
        return [(second - first) == self.size]


class LeSpacer(Spacer):
    """ A spacer which represents a flexible space with a maximum value.

    """
    def constraints(self, first, second):
        """ A constraint of the form: (second - first) <= size

        A second constraint is applied to prevent negative space:
        (second - first) >= 0

        """
        return [(second - first) <= self.size, (second - first) >= 0]


class GeSpacer(Spacer):
    """ A spacer which represents a flexible space with a minimum value.

    """
    def constraints(self, first, second):
        """ A constraint of the form: (second - first) >= size

        """
        return [(second - first) >= self.size]


class FlexSpacer(Spacer):
    """ A spacer with a hard minimum and a preference for that minimum.

    """
    #: The strength for the minimum space constraint.
    min_strength = StrengthMember(kiwi.strength.required)

    #: The strength for the equality space constraint.
    eq_strength = StrengthMember(kiwi.strength.medium * 1.25)

    def __init__(self, size, min_strength=None, eq_strength=None):
        """ Initialize a FlexSpacer.

        Parameters
        ----------
        size : int
            The basic size of the spacer, in pixels >= 0.

        min_strength : strength-like, optional
            The strength to apply to the minimum spacer size. The
            default is kiwi.strength.required.

        eq_strength : strength-like, optional
            The strength to apply to preferred spacer size. The
            default is 1.25 * kiwi.strength.medium.

        """
        self.size = size
        if min_strength is not None:
            self.min_strength = min_strength
        if eq_strength is not None:
            self.eq_strength = eq_strength

    def constraints(self, first, second):
        """ Generate the constraints for the spacer.

        """
        min_cn = ((second - first) >= self.size) | self.min_strength
        eq_cn = ((second - first) == self.size) | self.eq_strength
        return [min_cn, eq_cn]


class LayoutSpacer(Spacer):
    """ A factory-like Spacer with convenient symbolic methods.

    """
    def __call__(self, *args, **kwargs):
        """ Create a new LayoutSpacer from the given arguments.

        """
        return type(self)(*args, **kwargs)

    def __or__(self, strength):
        """ Create a new LayoutSpacer with the given strength.

        """
        return type(self)(self.size, strength)

    def __eq__(self, size):
        """ Create an EqSpacer with the given size.

        """
        return EqSpacer(size, self.strength)

    def __le__(self, size):
        """ Create an LeSpacer with the given size.

        """
        return LeSpacer(size, self.strength)

    def __ge__(self, size):
        """ Create a GeSpacer withe the given size.

        """
        return GeSpacer(size, self.strength)

    def flex(self, **kwargs):
        """ Create a FlexSpacer with the given configuration.

        """
        return FlexSpacer(self.size, **kwargs)

    def constraints(self, first, second):
        """ Create the constraints for >= spacer constraint.

        """
        return GeSpacer(self.size, self.strength).constraints(first, second)
