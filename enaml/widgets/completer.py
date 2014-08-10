#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Str, Enum, List, ForwardTyped, observe
)

from enaml.core.declarative import d_, d_func

from .toolkit_object import ProxyToolkitObject, ToolkitObject


class ProxyCompleter(ProxyToolkitObject):
    """ The abstract definition of a proxy Completer object.

    """
    #: A reference to the Field declaration.
    declaration = ForwardTyped(lambda: Completer)

    def set_mode(self, mode):
        raise NotImplementedError

    def set_completion_model(self, completion_model):
        raise NotImplementedError

    def set_prefix(self, prefix):
        raise NotImplementedError

    def set_sorting(self, sorting):
        raise NotImplementedError


class Completer(ToolkitObject):
    """
    """
    #:
    mode = d_(Enum('popup', 'inline', 'unfiltered_popup'))

    #:
    completion_model = d_(List())

    #:
    sorting = d_(Enum('unsorted', 'case_insensitve_sorting',
                      'case_sensitive_sorting'))

    #:
    prefix = Str()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @d_func
    def propose_completion(self, text):
        """
        """
        return text.split(' ')[-1], None

    @d_func
    def entry_highlighted(self, choice):
        """
        """
        pass

    @d_func
    def complete(self, choice, text, cursor_pos):
        """
        """
        before = text[0:cursor_pos]
        after = text[cursor_pos::]
        aux = before.rsplit(' ', 1)
        if len(aux) > 1:
            return ' '.join((aux[0], choice, after)), len(aux[0]) + len(choice)

        else:
            return ' '.join((choice, after)), len(choice)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('mode', 'completion_model', 'prefix', 'sorting')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass implementation is sufficient.
        super(Completer, self)._update_proxy(change)
