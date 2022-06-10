#------------------------------------------------------------------------------
# Copyright (c) 2018-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import os
import importlib
from utils import cd


def test_workbench(enaml_run, qtbot):
    from enaml.qt.QtCore import Qt

    # Run normally to generate cache files
    dir_path = os.path.abspath(os.path.split(os.path.dirname(__file__))[0])
    example = os.path.join(dir_path, 'examples', 'workbench')

    def handler(app, window):
        widget = window.proxy.widget
        qtbot.wait(1000)
        for i in range(1, 4):
            qtbot.keyClick(widget, str(i), Qt.ControlModifier)
            qtbot.wait(100)
            # TODO: Verify each screen somehow

        qtbot.keyClick(widget, 'q', Qt.ControlModifier)
        # Wait for exit, otherwise it unregisters the commands
        qtbot.wait(100)

    enaml_run.run = handler

    # Add to example folder to the sys path or we get an import error
    with cd(example, add_to_sys_path=True):
        # Now run from cache
        mod = importlib.import_module('sample')
        mod.main()
