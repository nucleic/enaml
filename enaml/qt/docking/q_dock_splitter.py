#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.QtCore import Qt
from enaml.qt.QtWidgets import QSplitter, QSplitterHandle

from .q_dock_area import QDockArea


class QDockSplitterHandle(QSplitterHandle):
    """ A subclass for dock splitter handles.

    This subclass sets the hover flag on the splitter handle so that
    the hover rules in a style sheet work correctly.

    """
    def __init__(self, orientation, parent):
        super(QDockSplitterHandle, self).__init__(orientation, parent)
        self.setAttribute(Qt.WA_Hover)


class QDockSplitter(QSplitter):
    """ A splitter subclass for distinguishing dock splitters.

    This subclass allows selecting the dock splitter in a stylesheet
    and otherwise distinguishing dock splitters from standard QSplitter
    instances used elsewhere in the application.

    """
    def createHandle(self):
        """ Create a sentinel dock splitter handle.

        """
        return QDockSplitterHandle(self.orientation(), self)

    def inheritOpaqueResize(self):
        """ Inherit the opaque resize state.

        This method traverses the ancestor hierarchy and updates its
        opaque resize state based on the first QDockArea it finds. If
        no such ancestor exists, the setting is unchanged. This method
        is called by the framework at the appropriate times.

        """
        p = self.parent()
        while p is not None:
            if isinstance(p, QDockArea):
                self.setOpaqueResize(p.opaqueItemResize())
                return
            p = p.parent()
