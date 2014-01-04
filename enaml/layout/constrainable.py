#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta

from atom.api import Atom, Constant, DefaultValue

import kiwisolver as kiwi


class Constrainable(object):
    """ An abstract base class for defining constrainable objects.

    Implementations must provide `top`, `bottom`, `left`, `right`,
    `width`, `height`, `v_center` and `h_center` attributes which
    are instances of 'LinearSymbolic'.

    """
    __metaclass__ = ABCMeta


class ContentsConstrainable(Constrainable):
    """ An abstract base class for contents constrainable objects.

    A contents constrainable object has additional linear symbolic
    attributes with the prefix 'contents_' for all of the symbolic
    attributes defined by Constrainable.

    """
    pass


class ConstraintMember(Constant):
    """ A custom Member class that generates a kiwi Variable.

    """
    __slots__ = ()

    def __init__(self):
        super(ConstraintMember, self).__init__()
        mode = DefaultValue.MemberMethod_Object
        self.set_default_value_mode(mode, 'default')

    def default(self, owner):
        """ Create the constraint variable for the member.

        """
        return kiwi.Variable(self.name)


class ConstrainableMixin(Atom):
    """ An atom mixin class which defines constraint members.

    This class implements the Constrainable interface.

    """
    #: The symbolic left boundary of the constrainable.
    left = ConstraintMember()

    #: The symbolic top boundary of the constrainable.
    top = ConstraintMember()

    #: The symbolic width of the constrainable.
    width = ConstraintMember()

    #: The symbolic height of the constrainable.
    height = ConstraintMember()

    #: A symbolic expression representing the top boundary.
    right = Constant()

    #: A symbolic expression representing the bottom boundary.
    bottom = Constant()

    #: A symbolic expression representing the horizontal center.
    h_center = Constant()

    #: A symbolic expression representing the vertical center.
    v_center = Constant()

    def _default_right(self):
        return self.left + self.width

    def _default_bottom(self):
        return self.top + self.height

    def _default_h_center(self):
        return self.left + 0.5 * self.width

    def _default_v_center(self):
        return self.top + 0.5 * self.height


Constrainable.register(ConstrainableMixin)


class ContentsConstrainableMixin(ConstrainableMixin):
    """ An atom mixin class which defines contents constraint members.

    This class implements the ContentsConstrainable interface.

    """
    #: The symbolic left contents boundary of the constrainable.
    contents_left = ConstraintMember()

    #: The symbolic right contents boundary of the constrainable.
    contents_right = ConstraintMember()

    #: The symbolic top contents boundary of the constrainable.
    contents_top = ConstraintMember()

    #: The symbolic bottom contents boundary of the constrainable.
    contents_bottom = ConstraintMember()

    #: A symbolic expression representing the content width.
    contents_width = Constant()

    #: A symbolic expression representing the content height.
    contents_height = Constant()

    #: A symbolic expression representing the content horizontal center.
    contents_h_center = Constant()

    #: A symbolic expression representing the content vertical center.
    contents_v_center = Constant()

    def _default_contents_width(self):
        return self.contents_right - self.contents_left

    def _default_contents_height(self):
        return self.contents_bottom - self.contents_top

    def _default_contents_h_center(self):
        return self.contents_left + 0.5 * self.contents_width

    def _default_contents_v_center(self):
        return self.contents_top + 0.5 * self.contents_height


ContentsConstrainable.register(ContentsConstrainableMixin)
