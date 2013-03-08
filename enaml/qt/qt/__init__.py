#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------

import os

def prepare_pyqt4():
    # Set PySide compatible APIs.
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

qt_api = os.environ.get('QT_API')

if qt_api is None:
    try:
        import PySide
        qt_api = 'pyside'
        os.environ['QT_API'] = qt_api
    except ImportError:
        try:
            prepare_pyqt4()
            import PyQt4
            qt_api = 'pyqt'
            os.environ['QT_API'] = qt_api
        except ImportError:
            raise ImportError('Cannot import PySide or PyQt4')

elif qt_api == 'pyqt':
    prepare_pyqt4()

elif qt_api != 'pyside':
    raise RuntimeError("Invalid Qt API %r, valid values are: 'pyqt' or 'pyside'"
                       % qt_api)
