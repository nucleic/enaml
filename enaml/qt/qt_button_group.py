from atom.api import Typed
from enaml.widgets.button_group import ProxyButtonGroup

from .QtWidgets import QButtonGroup

from .qt_toolkit_object import QtToolkitObject


class QtButtonGroup(QtToolkitObject, ProxyButtonGroup):
    widget = Typed(QButtonGroup)

    def create_widget(self):
        self.widget = QButtonGroup(self.parent_widget())

    def init_widget(self):
        super(QtButtonGroup, self).init_widget()

        d = self.declaration
        self.set_exclusive(d.exclusive)

    def set_exclusive(self, exclusive):
        self.widget.setExclusive(exclusive)

    def add_button(self, button):
        self.widget.addButton(button.proxy.widget)

    def remove_button(self, button):
        self.widget.removeButton(button.proxy.widget)
