#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os


def prepare_pyqt():
    import sip
    sip.setapi('QDate', 2)
    sip.setapi('QDateTime', 2)
    sip.setapi('QString', 2)
    sip.setapi('QTextStream', 2)
    sip.setapi('QTime', 2)
    sip.setapi('QUrl', 2)
    sip.setapi('QVariant', 2)


QT_API = os.environ.get('QT_API', '').lower().strip()


if not QT_API:
    try:
        import PyQt4
        prepare_pyqt()
        QT_API = os.environ['QT_API'] = 'pyqt'
    except ImportError:
        try:
            import PySide
            QT_API = os.environ['QT_API'] = 'pyside'
        except ImportError:
            raise ImportError('Cannot import PyQt4 or PySide')
elif QT_API == 'pyqt':
    prepare_pyqt()
elif QT_API != 'pyside':
    msg = "Invalid Qt API %r, valid values are: 'pyqt' or 'pyside'"
    raise ValueError(msg % QT_API)
