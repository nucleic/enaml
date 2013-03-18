#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed, List

from .group import Group


class Editor(Atom):
    """ A class which defines an editor for a model object.

    An Editor comprises a 'model' object and groups of items to use for
    viewing and editing that model. Instances of Editor are added to the
    various item model class to generate a model usable by the UI.

    """
    #: The model object to be edited by this editor. Subclasses may
    #: redefine this member to enforce stricter type checking.
    model = Typed(object)

    #: The list of groups for the model editor. When possible, Group
    #: instances should be shared between Editors. This helps keep the
    #: memory footprint of an application low. The list of groups will
    #: not be copied on assignment, so the list can also be shared.
    groups = List(Group, copy=False)
