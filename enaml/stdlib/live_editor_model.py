#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import traceback
from types import ModuleType

from atom.api import Atom, Str, Typed, observe

import enaml
from enaml.core.object import Object
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.parser import parse


class LiveEditorModel(Atom):
    """ The model which supports the live editor views.

    """
    #: The Enaml text to input into the model.
    input_text = Str()

    #: The generated Enaml output object.
    output_item = Typed(Object)

    #: The string name of the enamldef to embed into the view.
    view_item = Str('Unknown')

    #: An optional filename to use when compile the code.
    file_name = Str('unknown.enaml')

    #: A string with the most recent trackback.
    traceback = Str()

    #: A strong reference to the module created from the code.
    module = Typed(ModuleType)

    #--------------------------------------------------------------------------
    # Post Validators
    #--------------------------------------------------------------------------
    def _post_validate_input_text(self, old, new):
        return new.replace('\r\n', '\n')

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('input_text', 'view_item'))
    def _refresh_model(self, change):
        self.refresh()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def refresh(self):
        try:
            ast = parse(self.input_text, filename=self.file_name)
            code = EnamlCompiler.compile(ast, self.file_name)
            module = ModuleType('__main__')
            module.__file__ = self.file_name
            namespace = module.__dict__
            with enaml.imports():
                exec code in namespace
        except Exception:
            self.traceback = traceback.format_exc()
        else:
            self.traceback = ''
            self.module = module
            self.output_item = namespace.get(self.view_item, lambda: None)()
