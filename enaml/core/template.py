#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Bool, List, Str, Tuple, Typed

from .compilers_nodes import TemplateNode


class TemplateInstance(Atom):
    """ A class representing a template instantiation.

    """
    #: The template node assigned by the compiler.
    node = Typed(TemplateNode)

    def __call__(self, parent=None, **kwargs):
        """ Instantiate the list of items for the template.

        Parameters
        ----------
        parent : Object or None
            The parent object for the generated objects.

        **kwargs
            Additional keyword arguments to pass to the generated
            objects during construction.

        """


class Specialization(Atom):
    """

    """
    #: The argument type specification.
    argspec = Tuple()

    #: Whether or not the template is variadic.
    variadic = Bool()


class Template(Atom):
    """ A class representing a 'template' definition.

    """
    #: The list of specializations associated with the template.
    specializations = List(Specialization)

    #: The name associated with the template.
    name = Str()

    #: The module name in which the template lives.
    module = Str()

    #: The cache of template instantiations.
    instance_cache = Typed(dict, ())

    #: Teh cache of template specializations.
    specialization_cache =  Typed(dict, ())

    def __repr__(self):
        """ A nice repr for an object created by the `template` keyword.

        """
        return "<template '%s.%s'>" % (self.module, self.name)

    def __call__(self, *args):
        """ Instantiate the template for the given arguments.

        Parameters
        ----------
        *args
            The arguments to use to instantiate the template.

        Returns
        -------
        result : TemplateInstance
            The instantiated template.

        Raises
        ------
        TypeError
            A TypeError will be raised if no matching template
            specialization can be found for the given arguments

        """
        inst = self.cache.get(args)
        if inst is not None:
            return inst
        matches = []
        argspec = tuple(type(arg) for arg in args)
        for spec in self.specializations:
            match, score = spec.match(argspec)
            if match:
                matches.append((score, spec))
        if len(matches) == 0:
            msg = 'no matching template for arguments %s'
            raise TypeError(msg % args)
        matches.sort()
        score, match = matches[0]
        if len(matches > 1):
            if score == matches[1][0]:
                msg = 'ambiguous overload for arguments %s'
                raise TypeError(msg % args)
        inst = match(*args)
        self.cache[args] = inst
        return inst
