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
    #: A strong reference to the current live view object.
    output_view = Typed(Object)

    #: The Enaml text defining the view module.
    module_text = Str()

    #: The string name of the enamldef to embed into the view.
    view_item = Str('Unknown')

    #: An optional filename to use when compiling the view code.
    filename = Str('unknown_view.enaml')

    #: A string with the most recent trackback.
    traceback = Str()

    #: A strong reference to the module created from the code.
    module = Typed(ModuleType)

    #--------------------------------------------------------------------------
    # Post Validators
    #--------------------------------------------------------------------------
    def _post_validate_module_text(self, old, new):
        return new.replace('\r\n', '\n')

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('module_text', 'view_item'))
    def _refresh_view_trigger(self, change):
        self.refresh_view()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def refresh_view(self):
        try:
            ast = parse(self.module_text, filename=self.filename)
            code = EnamlCompiler.compile(ast, self.filename)
            module = ModuleType('__main__')
            module.__file__ = self.filename
            namespace = module.__dict__
            with enaml.imports():
                exec code in namespace
        except Exception:
            self.traceback = traceback.format_exc()
        else:
            self.traceback = ''
            self.module = module
            view_class = namespace.get(self.view_item)
            if view_class is not None:
                self.output_view = view_class()
            else:
                self.output_view = None
