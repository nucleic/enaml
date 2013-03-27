#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Callable, List, ForwardTyped, observe, set_default

from enaml.core.declarative import d_
from enaml.widgets.control import Control, ProxyControl


class ProxyEditorView(ProxyControl):
    """ The abstract definition of a proxy EditorView object.

    """
    #: A reference to the EditorView declaration.
    declaration = ForwardTyped(lambda: EditorView)

    def set_models(self, models):
        raise NotImplementedError


class EditorView(Control):
    """

    """
    models = d_(List())

    editor_factory = d_(Callable())

    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    @observe('models')
    def _update_proxy(self, change):
        super(EditorView, self)._update_proxy(change)
