from . import QT_API


if QT_API == 'pyqt':
    from PyQt5.QtWidgets import *
else:
    from PySide.QtWidgets import *
