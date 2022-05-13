#------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed
from enaml.widgets.autocomplete_field import ProxyAutocompleteField

from .QtCore import QStringListModel, Qt
from .QtWidgets import QCompleter

from .qt_field import QtField


FILTER_MODES = {
    'starts_with': Qt.MatchStartsWith,
    'contains': Qt.MatchContains,
    'ends_with': Qt.MatchEndsWith,
}


COMPLETION_MODES = {
    'popup': QCompleter.PopupCompletion,
    'inline': QCompleter.InlineCompletion,
    'unfiltered_popup': QCompleter.UnfilteredPopupCompletion,
}


class QtAutocompleteField(QtField, ProxyAutocompleteField):

    completer = Typed(QCompleter)

    def init_widget(self):
        super().init_widget()
        self.completer = QCompleter()
        self.widget.setCompleter(self.completer)

        d = self.declaration
        if d.items:
            self.set_items(d.items)
        self.set_filter_mode(d.filter_mode)
        self.set_case_sensitive(d.case_sensitive)
        self.set_completion_mode(d.completion_mode)

    def set_items(self, items):
        self.completer.setModel(QStringListModel(items))

    def set_filter_mode(self, filter_mode):
        self.completer.setFilterMode(FILTER_MODES[filter_mode])

    def set_case_sensitive(self, case_sensitive):
        if case_sensitive:
            self.completer.setCaseSensitivity(Qt.CaseSensitive)
        else:
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)

    def set_completion_mode(self, completion_mode):
        self.completer.setCompletionMode(COMPLETION_MODES[completion_mode])
