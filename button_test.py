
from enaml.qt.docking.button_bitmaps import restore_bitmap

from PyQt4.QtCore import QSize, QAbstractFileEngineHandler, Qt
from PyQt4.QtGui import (
    QApplication, QAbstractButton, QFrame, QVBoxLayout, QPainter,
    QStyleOption, QStyle, QColor
)

class MyButton(QAbstractButton):

    def sizeHint(self):
        return QSize(20, 20)

    def paintEvent(self, event):
        p = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        # opt.state |= QStyle.State_AutoRaise
        # if (self.isEnabled() and self.underMouse() and not
        #     self.isChecked() and not self.isDown()):
        #     opt.state |= QStyle.State_Raised
        # if self.isChecked():
        #     opt.state |= QStyle.State_On
        if self.isDown():
            opt.state |= QStyle.State_Sunken

        # if (const QTabBar *tb = qobject_cast<const QTabBar *>(parent())) {
        #     int index = tb->currentIndex();
        #     QTabBar::ButtonPosition position = (QTabBar::ButtonPosition)style()->styleHint(QStyle::SH_TabBar_CloseButtonPosition, 0, tb);
        #     if (tb->tabButton(index, position) == this)
        #         opt.state |= QStyle::State_Selected;
        # }

        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
        #self.style().drawPrimitive(QStyle.PE_IndicatorTabClose, opt, p, self)
        #print self.palette().foreground().color().blue()
        #c = self.style().styleHint(
        #    QStyle.SH_GroupBox_TextLabelColor, opt, self, None
        #)
        #c2 = QColor.fromRgba(0xffffffff & c)  # stupid signed int
        #bmp = restore_bitmap()
        #p.setBackgroundMode(Qt.OpaqueMode)
        #p.setBackground(c2)
        #p.setPen(c2)
        #p.drawPixmap(0, 0, bmp)


class MyHandler(QAbstractFileEngineHandler):

    def create(self, filename):
        print filename


app = QApplication([])
h = MyHandler()

w = QFrame()
b = MyButton()
l = QVBoxLayout()
l.addWidget(b)
w.setLayout(l)

w.setStyleSheet("""
    QFrame {
        background: rgb(20, 20, 200);
    }
    MyButton {
        background: yellow;
        border: 1px solid red;
        min-width: 40px;
        max-width: 40px;
        color: orange;
    }
    MyButton:hover {
        border: 1px solid white;
    }
    MyButton:pressed {
        background: red;
    }

    """)
w.show()
app.exec_()
