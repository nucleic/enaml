#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import enaml
from enaml.qt.qt_application import QtApplication

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    with enaml.imports():
        from hello_world_view import Main

    app = QtApplication()

    view = Main(message="Hello World, from Python!")
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    main()
