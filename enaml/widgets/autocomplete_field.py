#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, Enum, List, ForwardTyped, observe, Typed
)

from enaml.core.declarative import d_
from .field import Field, ProxyField


class ProxyAutocompleteField(ProxyField):

    #: A reference to the ObjectCombo declaration.
    declaration = ForwardTyped(lambda: AutocompleteField)

    def set_items(self, items):
        raise NotImplementedError

    def set_filter_mode(self, filter_mode):
        raise NotImplementedError

    def set_case_sensitive(self, case_sensitive):
        raise NotImplementedError

    def set_completion_mode(self, completion_mode):
        raise NotImplementedError


class AutocompleteField(Field):
    #: The list of items that can be matched using autocomplete
    items = d_(List())

    #: How should filtering on the list of items work?
    filter_mode = d_(Enum('starts_with', 'contains', 'ends_with'))

    #: Is filtering case-sensitive?
    case_sensitive = d_(Bool(True))

    #: How are completions displayed to the user? For unfiltered, all
    #: completions are shown with the most likely suggestion indicated as
    #: current.
    completion_mode = d_(Enum('popup', 'inline', 'unfiltered_popup'))

    #: A reference to the ProxyObjectCombo object.
    proxy = Typed(ProxyAutocompleteField)

    @observe('items', 'filter_mode', 'case_sensitive', 'completion_mode')
    def _update_proxy_items(self, change):
        super()._update_proxy(change)
