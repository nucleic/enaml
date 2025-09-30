# ------------------------------------------------------------------------------
# Copyright (c) 2022-2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------


def test_loading_dock_area_images(qapp):
    from enaml.qt.QtCore import QRect, QPoint
    from enaml.qt.docking.q_guide_rose import BorderGuide, CompassGuide, CompassExGuide

    # This forces to load all the images
    bg = BorderGuide()
    bg.layout(QRect())
    cg = CompassGuide()
    cg.layout(QPoint())
    ceg = CompassExGuide()
    ceg.layout(QPoint())
