import sys
import traceback
import types
from atom.api import Atom, Value, Unicode

import enaml
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.exceptions import DeclarativeNameError
from enaml.core.parser import parse

HEADER = """
from enaml.widgets.api import Container, Label


enamldef DemoContainer( Container ): demo:
    Label:
        text = 'test'
"""


class GuiBuilderModel( Atom ):
    """
    The model which supports the live gui builder.

    input_text      : the current text in the code entry panel
    compiled_object : the enaml object representing the selected
                      item from the available code.
    view_item       : a Unicode string representing the name of
                      the enamldef you want to view.
    file_name       : a utility add-on for the parse/compile stage.
    error_message   : a Unicode string of the latest error message
                      if the last _process() call raised an exception.
    """
    input_text = Value()
    compiled_object = Value()
    view_item = Unicode( default='DemoContainer' )
    file_name = Unicode( default='temp_file_name.enaml' )
    error_message = Unicode(default='')

    def _observe_input_text( self, change ):
        self._process()

    def _observe_view_item( self, change ):
        self._process()

    def _process( self ):
        try:
            text = str( self.input_text )
            ast = parse( text, filename=self.file_name )
            code = EnamlCompiler.compile( ast, self.file_name )
            module = types.ModuleType( '__main__' )
            module.__file__ = self.file_name
            ns = module.__dict__
            with enaml.imports():
                exec code in ns
        except (SyntaxError, ImportError, DeclarativeNameError):
            self.error_message = traceback.format_exc()
            return

        self.error_message = ''
        self.compiled_object = ns[self.view_item]()


if __name__ == '__main__':
    import enaml
    from enaml.qt.qt_application import QtApplication
    with enaml.imports():
        from enaml.stdlib.gui_builder_view import Main

    app = QtApplication()
    model = GuiBuilderModel( input_text=HEADER )
    view = Main( model=model )

    view.show()
    app.start()

