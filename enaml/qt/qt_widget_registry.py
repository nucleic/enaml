#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict


class QtWidgetRegistry(object):
    """ A class for registering Qt widget factories.

    This is a process-widget registry class. Interaction is done through
    the two classmethods `register` and `lookup`.

    """
    #: Private storage for the widget factories.
    _groups = defaultdict(dict)

    @classmethod
    def register(cls, name, factory, group, strict=False):
        """ Registery a widget factory.

        Parameters
        ----------
        name : str
            The name of the Enaml widget class which is implemented
            by the class returned by the given factory.

        factory : callable
            A callable which takes no arguments and returns the class
            which implements the widget.

        group : str
            The widget group with which this factory is associated.

        strict : bool, optional
            If True, attempting to register a factory for a widget
            which is already registered will raise a ValueError.
            The default is False.

        """
        thisgroup = cls._groups[group]
        if strict and name in thisgroup:
            msg = ('Factory already registered for the `%s` widget in the '
                   '`%s` widget group.')
            raise ValueError(msg % (name, group))
        thisgroup[name] = factory

    @classmethod
    def lookup(cls, name, groups):
        """ Lookup a widget factory.

        Parameters
        ----------
        name : str
            The name of the Enaml widget for which to lookup a factory.

        groups : list of str
            The list of groups to check for a matching factory. The
            groups are checked in order with the first match being
            returned. If no match is found, None will be returned.

        """
        thesegroups = cls._groups
        for group in groups:
            if group in thesegroups:
                thisgroup = thesegroups[group]
                if name in thisgroup:
                    return thisgroup[name]

