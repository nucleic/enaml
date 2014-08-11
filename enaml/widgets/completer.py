#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Enum, List, Bool, ForwardTyped, observe
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

    def set_sorting(self, sorting):
        raise NotImplementedError

    def set_case_sensitivity(self, sensitivity):
        raise NotImplementedError


class Completer(ToolkitObject):
    """
    """
    #:
    mode = d_(Enum('popup', 'inline', 'unfiltered_popup'))

    #: Model providiing the completion.
    completion_model = d_(List())

    #: Should the completer sort the enrtries of the model.
    sorting = d_(Enum('unsorted', 'case_insensitve_sorting',
                      'case_sensitive_sorting'))

    #: Should the completer be case sensitive.
    case_sensitivity = d_(Bool(True))

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @d_func
    def propose_completion(self, text):
        """ Determine the prefix to use for the completion.

        This is called after every keystroke and receive the text before the
        current position of the cursor.

        Parameters
        ----------
        text : str
            Text from which to extract the prefix.

        Returns
        -------
        prefix : str or None
            Prefix to use for the completion or None if no completion should be
            proposed.

        model : list or None
            New model to use for the completion.

        """
        return text.split(' ')[-1], None

    @d_func
    def entry_highlighted(self, choice):
        """ Method called when an entry of the completer is highlighted.

        By default nothing happens.

        Parameters
        ----------
        choice : str
            The entry highlighted by the user.

        """
        pass

    @d_func
    def complete(self, choice, text, cursor_pos):
        """ Method called when the user asks for completion.

        Parameters
        ----------
        choice : str
            The entry selected by the user and which should be inserted.

        text : str
            The relevant portion of text in which to insert choice.
            For a field this is the whole text for a multiline widget the line
            currently edited.

        cursor_pos : int
            The current position of the cursor as an int such as
            text[:cursor_pos] is the text just to the left of the cursor.

        Returns
        -------
        new :str
            The new text as should be inserted in the widget.

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
