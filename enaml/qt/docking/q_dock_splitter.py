#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtGui import QSplitter, QSplitterHandle


class QDockSplitterHandle(QSplitterHandle):
    """ A sentinel subclass for dock splitter handles.

    This subclass allows selecting the splitter handle in a stylesheet
    and otherwise distinguishing dock splitter handles from standard
    QSplitterHandle instances used elsewhere in the application.

    """
    pass


class QDockSplitter(QSplitter):
    """ A sentinel subclass for distinguishing dock splitters.

    This subclass allows selecting the dock splitter in a stylesheet
    and otherwise distinguishing dock splitters from standard QSplitter
    instances used elsewhere in the application.

    """
    def createHandle(self):
        return QDockSplitterHandle(self.orientation(), self)
