#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import linecache
import traceback
from types import ModuleType

from atom.api import Atom, Str, Typed, observe

import enaml
from enaml.core.object import Object
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.parser import parse


def fake_linecache(text, filename):
    size = len(text)
    mtime = 1343290295L
    lines = text.splitlines()
    lines = [l + '\n' for l in lines]
    linecache.cache[filename] = size, mtime, lines, filename


class LiveEditorModel(Atom):
    """ The model which supports the live editor views.

    """
    #: The current live model object bound to the main view.
    output_model = Typed(Atom)

    #: The current live view object to include in the main view.
    output_view = Typed(Object)

    #: The Python module text for the model module.
    model_text = Str()

    #: The Enaml module text for the view module.
    view_text = Str()

    #: The string name of the Atom class to use as the model.
    model_item = Str()

    #: The string name of the enamldef to use as the view.
    view_item = Str()

    #: An optional filename to use when compiling the python code.
    py_filename = Str('main.py')

    #: An optional filename to use when compiling the enaml code.
    enaml_filename = Str('main.enaml')

    #: A string which holds the most recent trackback.
    traceback = Str()

    #: The module created from the model code.
    _model_module = Typed(ModuleType)

    #: The module created from the view code.
    _view_module = Typed(ModuleType)

    #--------------------------------------------------------------------------
    # Post Validators
    #--------------------------------------------------------------------------
    def _post_validate_model_text(self, old, new):
        return new.replace('\r\n', '\n')

    def _post_validate_view_text(self, old, new):
        return new.replace('\r\n', '\n')

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('model_text', 'model_item'))
    def _refresh_model_trigger(self, change):
        self.refresh_model()

    @observe(('view_text', 'view_item'))
    def _refresh_view_trigger(self, change):
        self.refresh_view()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _build_model(self):
        text = self.model_text
        fake_linecache(text, self.py_filename)
        if not text:
            self.output_model = None
            return
        try:
            code = compile(text, self.py_filename, 'exec')
            module = ModuleType('__main__')
            module.__file__ = self.py_filename
            namespace = module.__dict__
            exec code in namespace
        except Exception:
            self.traceback = traceback.format_exc()
        else:
            self.traceback = ''
            self._model_module = module
            model_class = namespace.get(self.model_item, lambda: None)
            self.output_model = model_class()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def refresh_model(self):
        self._build_model()
        view = self.output_view
        if view is not None and hasattr(view, 'model'):
            view.model = self.output_model

    def refresh_view(self):
        text = self.view_text
        fake_linecache(text, self.enaml_filename)
        if not text:
            self.output_view = None
            return

        try:
            ast = parse(text, filename=self.enaml_filename)
            code = EnamlCompiler.compile(ast, self.enaml_filename)
            module = ModuleType('__main__')
            module.__file__ = self.enaml_filename
            namespace = module.__dict__
            with enaml.imports():
                exec code in namespace
        except Exception:
            self.traceback = traceback.format_exc()
            return
            
        self.traceback = ''
        vc = namespace.get(self.view_item)
        if isinstance(vc, type) and issubclass(vc, Object):
            try:
                if 'model' in vc.members():
                    model = self.output_model
                    view = vc(model=model)
                else:
                    view = vc()
                old_view = self.output_view
                try:
                    self.output_view = view
                except Exception:
                    self.output_view = old_view
                    if hasattr(old_view, 'show'):
                        old_view.show()
                    raise
                self._view_module = module
                if old_view is not None:
                    old_view.destroy()
            except Exception:
                self.traceback = traceback.format_exc()
