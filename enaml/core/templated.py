#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import List

from .declarative import Declarative


class Templated(Declarative):
    """ A declarative which serves as a base class for templated types.

    The `Templated` class serves as a base class for classes such as
    `Looper` and `Conditional` which never create their children, but
    the descriptions of their children as templates for generating new
    objects at runtime.

    """
    #: Private storage for the templates used to create items.
    _templates = List()

    def _populate(self, description, f_locals, f_globals):
        """ An overridden parent class populator.

        A `Templated` object never actually constructs its children.
        Instead, the child descriptions are used as templates by the
        various subclasses to generate objects at runtime.

        """
        scopename = description['scopename']
        if scopename and description['bindings']:
            setattr(self, scopename, f_locals)
        ident = description['identifier']
        if ident:
            f_locals[ident] = self
        children = description['children']
        if len(children) > 0:
            template = (f_locals, f_globals, children)
            self._templates.append(template)
