#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import os
import sys
import types

import pytest

from enaml import imports
from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.widgets.api import PopupView, Window
from utils import (close_window_or_popup, get_popup,
                   wait_for_window_displayed,
                   wait_for_destruction,
                   handle_dialog, handle_question,
                   is_qt_available)

try:
    import numpy
except ImportError:
    NUMPY_AVAILABLE = False
else:
    NUMPY_AVAILABLE = True

try:
    import matplotlib
except ImportError:
    MATPLOTLIB_AVAILABLE = False
else:
    MATPLOTLIB_AVAILABLE = True


try:
    try:
        from PyQt4 import Qsci
    except Exception:
        from PyQt5 import Qsci
except ImportError:
    SCINTILLA_AVAILABLE = False
else:
    SCINTILLA_AVAILABLE = True


try:
    import vtk
except ImportError:
    VTK_AVAILABLE = False
else:
    VTK_AVAILABLE = True


try:
    from enaml.qt import QtWebEngineWidgets
    WEBVIEW_AVAILABLE = True
except Exception:
    WEBVIEW_AVAILABLE = False


if is_qt_available():
    try:
        import enaml.qt.qt_ipython_console
    except ImportError:
        IPY_AVAILABLE = False
    else:
        IPY_AVAILABLE = True
else:
    IPY_AVAILABLE = False


def handle_popup_view_example(qtbot, window):
    """Test showing the popups.

    """
    from conftest import DIALOG_SLEEP

    popup_triggers = window.central_widget().widgets()
    # Test configuration popup
    popup_triggers[0].clicked = True
    popup = get_popup(qtbot)
    qtbot.wait(DIALOG_SLEEP*1000)
    popup.central_widget().widgets()[-1].clicked = True
    wait_for_destruction(qtbot, popup)

    # Test transient popups
    for t in popup_triggers[1:]:
        t.clicked = True
        popup = get_popup(qtbot)
        qtbot.wait(DIALOG_SLEEP*1000)
        close_window_or_popup(qtbot, popup)


def handle_window_closing(qtbot, window):
    """Test answering the question to close the window.

    """
    with handle_question(qtbot, 'yes'):
        window.close()

    def check_window_closed():
        assert not Window.windows

    qtbot.wait_until(check_window_closed)

@pytest.mark.skipif(not is_qt_available(), reason='Requires a Qt binding')
@pytest.mark.parametrize("path, handler",
                         [('aliases/chained_attribute_alias.enaml', None),
                          ('aliases/chained_widget_alias.enaml', None),
                          ('aliases/simple_attribute_alias.enaml', None),
                          ('aliases/simple_widget_alias.enaml', None),
                          pytest.param('applib/live_editor.enaml', None,
                                       marks=pytest.mark.skipif(
                                           not SCINTILLA_AVAILABLE,
                                           reason='Requires scintilla')),
                          ('dynamic/conditional.enaml', None),
                          ('dynamic/fields.enaml', None),
                          ('dynamic/looper.enaml', None),
                          ('dynamic/notebook_pages.enaml', None),
                          ('functions/declare_function.enaml', None),
                          ('functions/observe_model_signal.enaml', None),
                          ('functions/override_function.enaml', None),
                          ('layout/basic/align_offset.enaml', None),
                          ('layout/basic/align.enaml', None),
                          ('layout/basic/grid.enaml', None),
                          ('layout/basic/hbox_equal_widths.enaml', None),
                          ('layout/basic/hbox_spacing.enaml', None),
                          ('layout/basic/hbox.enaml', None),
                          ('layout/basic/horizontal.enaml', None),
                          ('layout/basic/linear_relations.enaml', None),
                          ('layout/basic/vbox.enaml', None),
                          ('layout/basic/vertical.enaml', None),
                          pytest.param('layout/advanced/button_ring.enaml',
                                       None,
                                       marks=pytest.mark.skipif(
                                           not (NUMPY_AVAILABLE and
                                                is_qt_available()),
                                           reason='Requires numpy and Qt'),),
                          ('layout/advanced/factory_func.enaml', None),
                          ('layout/advanced/find_replace.enaml', None),
                          ('layout/advanced/fluid.enaml', None),
                          ('layout/advanced/manual_hbox.enaml', None),
                          ('layout/advanced/manual_vbox.enaml', None),
                          ('layout/advanced/nested_boxes.enaml', None),
                          ('layout/advanced/nested_containers.enaml', None),
                          ('layout/advanced/override_layout_constraints.enaml',
                           None),
                          ('stdlib/mapped_view.enaml', None),
                          ('stdlib/message_box.enaml', None),
                          ('stdlib/slider_transform.enaml', None),
                          ('stdlib/task_dialog.enaml', None),
                          ('styling/banner.enaml', None),
                          ('styling/dock_item_alerts.enaml', None),
                          ('styling/gradient_push_button.enaml', None),
                          ('templates/basic.enaml', None),
                          ('templates/advanced.enaml', None),
                          ('widgets/buttons.enaml', None),
                          ('widgets/context_menu.enaml', None),
                          ('widgets/dock_area.enaml', None),
                          ('widgets/dock_pane.enaml', None),
                          ('widgets/dual_slider.enaml', None),
                          ('widgets/file_dialog.enaml', None),
                          ('widgets/flow_area.enaml', None),
                          ('widgets/focus_traversal.enaml', None),
                          ('widgets/form_spacing.enaml', None),
                          ('widgets/form.enaml', None),
                          ('widgets/group_box.enaml', None),
                          ('widgets/h_group.enaml', None),
                          pytest.param('widgets/ipython_console.enaml', None,
                                       marks=pytest.mark.skipif(
                                           not IPY_AVAILABLE,
                                           reason=('Requires IPython and its '
                                                   'qt console.'))),
                          ('widgets/image_view.enaml', None),
                          ('widgets/main_window.enaml', None),
                          ('widgets/menu_bar.enaml', None),
                          pytest.param('widgets/mpl_canvas.enaml', None,
                                       marks=pytest.mark.skipif(
                                           not MATPLOTLIB_AVAILABLE,
                                           reason='Requires matplotlib')),
                          ('widgets/notebook.enaml', None),
                          ('widgets/popup_menu.enaml', None),
                          ('widgets/popup_view.enaml',
                           handle_popup_view_example),
                          ('widgets/progress_bar.enaml', None),
                          ('widgets/scroll_area.enaml', None),
                          ('widgets/slider.enaml', None),
                          ('widgets/spin_box.enaml', None),
                          ('widgets/splitter.enaml', None),
                          ('widgets/tool_bar.enaml', None),
                          ('widgets/tool_buttons.enaml', None),
                          ('widgets/v_group.enaml', None),
                          pytest.param('widgets/vtk_canvas.enaml', None,
                                       marks=pytest.mark.skipif(
                                           not VTK_AVAILABLE,
                                           reason='Requires vtk')),
                          pytest.param('widgets/web_view.enaml', None,
                                       marks=pytest.mark.skipif(
                                           not WEBVIEW_AVAILABLE,
                                           reason='Requires webview')),
                          ('widgets/window_children.enaml', None),
                          ('widgets/window_closing.enaml',
                           handle_window_closing),
                          ('widgets/window.enaml', None)])
def test_examples(enaml_qtbot, enaml_sleep, path, handler):
    """ Test the enaml examples.

    """
    dir_path = os.path.abspath(os.path.split(os.path.dirname(__file__))[0])
    enaml_file = os.path.join(dir_path, 'examples', os.path.normpath(path))

    with open(enaml_file, 'r') as f:
        enaml_code = f.read()

    # Parse and compile the Enaml source into a code object
    ast = parse(enaml_code, filename=enaml_file)
    code = EnamlCompiler.compile(ast, enaml_file)

    # Create a proper module in which to execute the compiled code so
    # that exceptions get reported with better meaning
    try:
        module = types.ModuleType('enaml_test')
        module.__file__ = os.path.abspath(enaml_file)
        sys.modules['enaml_test'] = module
        ns = module.__dict__

        # Put the directory of the Enaml file first in the path so relative
        # imports can work.
        sys.path.insert(0, os.path.abspath(os.path.dirname(enaml_file)))
        with imports():
            exec(code, ns)

        window = ns['Main']()
        window.show()
        window.send_to_front()
        wait_for_window_displayed(enaml_qtbot, window)
        enaml_qtbot.wait(enaml_sleep*1000)

        if handler is not None:
            handler(enaml_qtbot, window)

    finally:
        # Make sure we clean up the sys modification before leaving
        sys.path.pop(0)
        del sys.modules['enaml_test']
