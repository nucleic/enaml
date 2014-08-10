#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.completer import ProxyCompleter

from .QtGui import QCompleter, QStringListModel

from .qt_toolkit_object import QtToolkitObject


COMPLETION_MODES = {
    'popup': QCompleter.PopupCompletion,
    'inline': QCompleter.InlineCompletion,
    'unfiltered_popup': QCompleter.UnfilteredPopupCompletion
}

MODEL_SORTING = {
    'unsorted': QCompleter.UnsortedModel,
    'case_insensitive_sorting': QCompleter.CaseInsensitivelySortedModel,
    'case_sensitive_sorting': QCompleter.CaseSensitivelySortedModel
}


class QtCompleter(QtToolkitObject, ProxyCompleter):
    """ A Qt4 implementation of an Enaml ProxyField.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QCompleter)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QFocusLineEdit widget.

        """
        w = QCompleter(self.parent_widget())
        w.setWidget(self.parent_widget())
        self.widget = w

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(QtCompleter, self).init_widget()
        d = self.declaration
        if d.completion_model:
            self.set_completion_model(d.completion_model)
        self.set_mode(d.mode)
        self.set_sorting(d.sorting)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_higligting(self, choice):
        """ The signal handler for the 'activated' signal.

        """
        d = self.declaration
        d.entry_higlighted(choice)

    #--------------------------------------------------------------------------
    # ProxyField API
    #--------------------------------------------------------------------------
    def set_mode(self, mode):
        """ Set the mode for the widget.

        """
        self.widget.setCompletionMode(COMPLETION_MODES[mode])

    def set_sorting(self, sorting):
        """ Set the sorting for the widget.

        """
        self.widget.setModelSorting(MODEL_SORTING[sorting])

    def set_completion_model(self, completion_model):
        """ Set the completion model.

        """
        if isinstance(completion_model, list):
            self.widget.setModel(QStringListModel(completion_model,
                                                  self.widget))

    def set_prefix(self, prefix):
        """ Set the prefix use to propose completion.

        """
        self.widget.setCompletionPrefix(prefix)
