#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from casuarius import ConstraintVariable


class BoxModel(object):
    """ A class which provides a simple constraints box model.

    Primitive Variables:
        left, top, width, height

    Derived Variables:
        right, bottom, v_center, h_center

    """
    __slots__ = (
        'left', 'top', 'width', 'height', 'right', 'bottom', 'v_center',
        'h_center'
    )

    def __init__(self, owner):
        """ Initialize a BoxModel.

        Parameters
        ----------
        owner : string
            A string which uniquely identifies the owner of this box
            model.

        """
        self.left = ConstraintVariable('left')
        self.top = ConstraintVariable('top')
        self.width = ConstraintVariable('width')
        self.height = ConstraintVariable('height')
        self.right = self.left + self.width
        self.bottom = self.top + self.height
        self.v_center = self.top + self.height / 2.0
        self.h_center = self.left + self.width / 2.0


class ContentsBoxModel(BoxModel):
    """ A BoxModel subclass which adds an inner contents box.

    Primitive Variables:
        contents_[left|right|top|bottom]

    Derived Variables:
        contents_[width|height|v_center|h_center]

    """
    __slots__ = (
        'contents_left', 'contents_right', 'contents_top', 'contents_bottom',
        'contents_width', 'contents_height', 'contents_v_center',
        'contents_h_center'
    )

    def __init__(self, owner):
        """ Initialize a ContainerBoxModel.

        Parameters
        ----------
        owner : string
            A string which uniquely identifies the owner of this box
            model.

        """
        super(ContentsBoxModel, self).__init__(owner)
        self.contents_left = ConstraintVariable('contents_left')
        self.contents_right = ConstraintVariable('contents_right')
        self.contents_top = ConstraintVariable('contents_top')
        self.contents_bottom = ConstraintVariable('contents_bottom')
        self.contents_width = self.contents_right - self.contents_left
        self.contents_height = self.contents_bottom - self.contents_top
        self.contents_v_center = self.contents_top + self.contents_height / 2.0
        self.contents_h_center = self.contents_left + self.contents_width / 2.0
