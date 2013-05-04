#------------------------------------------------------------------------------
#  Copyright (c) 2013, Nucleic Development Team.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml
from enaml.qt.qt_application import QtApplication


def main():
    with enaml.imports():
        from examples.tutorial.hello_world.hello_world_view import Main

    app = QtApplication()

    view = Main()
    view.show()

    # Start the application event loop
    app.start()
