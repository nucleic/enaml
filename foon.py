# -*- coding: utf-8 -*-
import sip
from PyQt4.QtCore import *
from PyQt4.QtGui import *

app = QApplication([])
w = QFrame()
class Spam(QFrame): pass
w2 = Spam()

w.setLayout(QVBoxLayout())
w.layout().addWidget(w2)
w.layout().setContentsMargins(QMargins(0, 25, 0, 0))
w.setStyleSheet("""
    Spam {
        background: red;
    }""")
w.resize(QSize(100, 100))
w.setContentsMargins(QMargins(10, 10, 10, 10))
w.show()
app.exec_()
