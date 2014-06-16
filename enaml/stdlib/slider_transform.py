#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" Enaml Standard Library - Slider Transforms

This module contains declarative classes which can be used as children
of a `Slider` to transform the integer range of the slider into an
alternative data space.

"""
from atom.api import Value, Bool, Float, Range

from enaml.core.declarative import Declarative, d_


class SliderTransform(Declarative):
    """ A base class for creating declarative slider transforms.

    A SliderTransform must be subclassed to be useful. The abstract api
    defined below must be implemented by the subclass.

    When using a transform with a slider, the transform takes complete
    ownership of the slider range. No effort is made to observe outside
    changes to the slider range, so all changes should be made on the
    transform.

    """
    #: The data-space minimum for the transform. This may be redefined
    #: by a subclass to enforce stronger typing.
    minimum = d_(Value())

    #: The data-space maximum for the transform. This may be redefined
    #: by a subclass to enforce stronger typing.
    maximum = d_(Value())

    #: The data-space value for the transform. This may be redefined
    #: by a subclass to enforce stronger typing.
    value = d_(Value())

    #: A boolean flag used to prevent loopback cycles.
    _guard = Bool(False)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def initialize(self):
        """ A reimplemented initialization handler.

        The parent slider values are initialized during the transform
        initialization pass.

        """
        super(SliderTransform, self).initialize()
        self._apply_transform()

    def parent_changed(self, old, new):
        """ Handle the parent changed event for the transform.

        """
        super(SliderTransform, self).parent_changed(old, new)
        if old is not None:
            old.unobserve('value', self._on_slider_value_changed)
        if new is not None:
            new.observe('value', self._on_slider_value_changed)

    def _apply_transform(self, minimum=True, maximum=True, value=True):
        """ Apply the current transform to the parent slider.

        Parameters
        ----------
        minimum : bool, optional
            Whether or not to update the slider minimum. The default
            is False.

        maximum : bool, optional
            Whether or not to update the slider maximum. The default
            is False.

        value : bool, optional
            Whether or not to update the slider value. The default
            is False.

        """
        parent = self.parent
        if parent is not None:
            if minimum:
                parent.minimum = self.get_minimum()
            if maximum:
                parent.maximum = self.get_maximum()
            if value:
                parent.value = self.get_value()

    def _on_slider_value_changed(self, change):
        """ Update the transformed value when slider changes.

        """
        if change['type'] == 'update':
            self._guard = True
            try:
                self.set_value(change['value'])
            finally:
                self._guard = False

    def _observe_minimum(self, change):
        """ Update the slider minimum on transform minimum change.

        """
        if change['type'] == 'update':
            self._apply_transform(maximum=False, value=False)

    def _observe_maximum(self, change):
        """ Update the slider maximum on transform maximum change.

        """
        if change['type'] == 'update':
            self._apply_transform(minimum=False, value=False)

    def _observe_value(self, change):
        """ Update the slider value on transform value change.

        """
        if change['type'] == 'update' and not self._guard:
            self._apply_transform(minimum=False, maximum=False)

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def get_minimum(self):
        """ Get the minimum value of the transform as an int.

        Returns
        -------
        result : int
            The minimum value of the transform converted to an int.

        """
        raise NotImplementedError

    def get_maximum(self):
        """ Get the maximum value of the transform as an int.

        Returns
        -------
        result : int
            The maximum value of the transform converted to an int.

        """
        raise NotImplementedError

    def get_value(self):
        """ Get the value of the transform as an int.

        Returns
        -------
        result : int
            The value of the transform converted to an int.

        """
        raise NotImplementedError

    def set_value(self, value):
        """ Set the value of the transform from an int.

        Parameters
        ----------
        value : int
            The integer value of the slider.

        """
        raise NotImplementedError


class FloatTransform(SliderTransform):
    """ A concreted SliderTransform for floating point values.

    """
    #: A redeclared parent class member which enforces float values.
    minimum = d_(Float(0.0))

    #: A redeclared parent class member which enforces float values.
    maximum = d_(Float(1.0))

    #: A redeclared parent class member which enforces float values.
    value = d_(Float(0.0))

    #: The number of stops to use between the minimum and maximum.
    precision = d_(Range(low=1, value=100))

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def get_minimum(self):
        """ Get the minimum value of the transform as an int.

        Returns
        -------
        result : int
            The minimum value of the transform converted to an int.

        """
        return 0

    def get_maximum(self):
        """ Get the maximum value of the transform as an int.

        Returns
        -------
        result : int
            The maximum value of the transform converted to an int.

        """
        return self.precision

    def get_value(self):
        """ Get the value of the transform as an int.

        Returns
        -------
        result : int
            The value of the transform converted to an int.

        """
        offset = self.value - self.minimum
        delta = self.maximum - self.minimum
        return int(offset * self.precision / delta)

    def set_value(self, val):
        """ Set the value of the transform from an int.

        Parameters
        ----------
        value : int
            The integer value of the slider.

        """
        delta = self.maximum - self.minimum
        self.value = (val * delta / self.precision) + self.minimum
