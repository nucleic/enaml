# ------------------------------------------------------------------------------
# Copyright (c) 2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
"""Test importing modules from the stdlib."""


def test_dialog_buttons():
    import enaml
    with enaml.imports():
        import enaml.stdlib.dialog_buttons


def test_dock_area_styles():
    import enaml
    with enaml.imports():
        import enaml.stdlib.dock_area_styles


def test_fields():
    import enaml
    with enaml.imports():
        import enaml.stdlib.fields


def test_mapped_view():
    import enaml
    with enaml.imports():
        import enaml.stdlib.mapped_view


def test_task_dialog():
    import enaml
    with enaml.imports():
        import enaml.stdlib.task_dialog


def test_message_box():
    import enaml
    with enaml.imports():
        import enaml.stdlib.message_box
