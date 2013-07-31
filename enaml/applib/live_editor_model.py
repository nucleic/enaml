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
from enaml.widgets.widget import Widget


def _fake_linecache(text, filename):
    """ Inject text into the linecache for traceback purposes.

    Parameters
    ----------
    text : str
        The text of the file.

    filename : str
        The name of the file.

    """
    size = len(text)
    mtime = 1343290295L
    lines = text.splitlines()
    lines = [l + '\n' for l in lines]
    linecache.cache[filename] = size, mtime, lines, filename


class LiveEditorModel(Atom):
    """ A model which works in concert with the live editor panels.

    This model manages the compiling and instantiation of the model
    and view objects defined by the user.

    The model has six inputs:

        'model_text'
            The full text of the Python module which defines the model.

        'view_text'
            The full text of the Enaml module which defines the view.

        'model_item'
            The name of the target model class in the model module.

        'view_item'
            The name of the target enamldef in the view module.

        'model_filename'
            An optional filename to associate with the model module.

        'view_filename'
            An optional filename to associate with the view module.

    The model has three outputs:

        'compiled_model'
            The instance of the user defined model, or None if no model
            could be created.

        'compiled_view'
            The instance of the user defined view, or None if no view
            could be created.

        'traceback'
            A string holding the traceback for any compilation and
            instantiation errors.

    If the 'compiled_view' object has a 'model' attribute, then the
    'compiled_model' object will be assigned to that attribute.

    """
    #: The current live model object bound to the main view.
    compiled_model = Typed(Atom)

    #: The current live view object to include in the main view.
    compiled_view = Typed(Object)

    #: The Python module input text for the model module.
    model_text = Str()

    #: The Enaml module input text for the view module.
    view_text = Str()

    #: The string name of the Atom class to use as the model.
    model_item = Str()

    #: The string name of the enamldef to use as the view.
    view_item = Str()

    #: An optional filename to use when compiling the python code.
    model_filename = Str('__live_model__.py')

    #: An optional filename to use when compiling the enaml code.
    view_filename = Str('__live_view__.enaml')

    #: A string which holds the most recent tracekback.
    traceback = Str()

    #: The module created from the model text.
    _model_module = Typed(ModuleType)

    #: The module created from the view text.
    _view_module = Typed(ModuleType)

    #--------------------------------------------------------------------------
    # Post Validators
    #--------------------------------------------------------------------------
    def _post_validate_model_text(self, old, new):
        """ Post validate the model text.

        This validator replaces CRLF with LF characters.

        """
        return new.replace('\r\n', '\n')

    def _post_validate_view_text(self, old, new):
        """ Post validate the view text.

        This validator replaces CRLF with LF characters.

        """
        return new.replace('\r\n', '\n')

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('model_text', 'model_item'))
    def _refresh_model_trigger(self, change):
        """ An observer which triggers a compiled model refresh.

        """
        self.refresh_model()

    @observe(('view_text', 'view_item'))
    def _refresh_view_trigger(self, change):
        """ An observer which triggers a compiled view refresh.

        """
        self.refresh_view()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def refresh_model(self):
        """ Refresh the compiled model object.

        This method will (re)compile the model for the given model text
        and update the 'compiled_model' attribute. If a compiled view is
        available and has a member named 'model', the model will be
        applied to the view.

        """
        text = self.model_text
        filename = self.model_filename
        _fake_linecache(text, filename)
        try:
            if not text:
                self.compiled_model = None
                self._model_module = None
            else:
                code = compile(text, filename, 'exec')
                module = ModuleType(filename.rsplit('.', 1)[0])
                module.__file__ = filename
                namespace = module.__dict__
                exec code in namespace
                model = namespace.get(self.model_item, lambda: None)()
                self.compiled_model = model
                self._model_module = module
            self.relink_view()
        except Exception:
            self.traceback = traceback.format_exc()
        else:
            self.traceback = ''

    def refresh_view(self):
        """ Refresh the compiled view object.

        This method will (re)compile the view for the given view text
        and update the 'compiled_view' attribute. If a compiled model
        is available and the view has a member named 'model', the model
        will be applied to the view.

        """
        text = self.view_text
        filename = self.view_filename
        _fake_linecache(text, filename)
        try:
            if not text:
                self.compiled_view = None
                self._view_module = None
            else:
                ast = parse(text, filename=filename)
                code = EnamlCompiler.compile(ast, filename)
                module = ModuleType('__main__')
                module.__file__ = filename
                namespace = module.__dict__
                with enaml.imports():
                    exec code in namespace
                view = namespace.get(self.view_item, lambda: None)()
                if isinstance(view, Object) and 'model' in view.members():
                    view.model = self.compiled_model
                # trap any initialization errors and roll back the view
                old = self.compiled_view
                try:
                    self.compiled_view = view
                except Exception:
                    self.compiled_view = old
                    if isinstance(old, Widget):
                        old.show()
                    raise
                self._view_module = module
                if old is not None and not old.is_destroyed:
                    old.destroy()
        except Exception:
            self.traceback = traceback.format_exc()
        else:
            self.traceback = ''

    def relink_view(self):
        """ Relink the compiled view with the compiled model.

        """
        view = self.compiled_view
        if view is not None and 'model' in view.members():
            view.model = self.compiled_model
