#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import logging

from .qt.QtCore import QSize
from .qt.QtGui import QIcon, QImage, QPixmap
from .qt_constraints_widget import size_hint_guard
from .qt_control import QtControl


logger = logging.getLogger(__name__)


class QtAbstractButton(QtControl):
    """ A Qt implementation of the Enaml AbstractButton class.

    This class can serve as a base class for widgets that implement
    button behavior such as CheckBox, RadioButton and PushButtons.
    It is not meant to be used directly.

    """
    #: Temporary internal storage for the icon source url.
    _icon_source = ''

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ This method must be implemented by subclasses to create
        the proper button widget.

        """
        raise NotImplementedError

    def create(self, tree):
        """ Create and initialize the abstract button widget.

        """
        super(QtAbstractButton, self).create(tree)
        self.set_checkable(tree['checkable'])
        self.set_checked(tree['checked'])
        self.set_text(tree['text'])
        self._icon_source = tree['icon_source']
        self.set_icon_size(tree['icon_size'])
        widget = self.widget()
        widget.clicked.connect(self.on_clicked)
        widget.toggled.connect(self.on_toggled)

    def activate(self):
        """ Activate the button widget.

        """
        self.set_icon_source(self._icon_source)
        super(QtAbstractButton, self).activate()

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_clicked(self):
        """ The signal handler for the 'clicked' signal.

        """
        content = {'checked': self.widget().isChecked()}
        self.send_action('clicked', content)

    def on_toggled(self):
        """ The signal handler for the 'toggled' signal.

        """
        content = {'checked': self.widget().isChecked()}
        self.send_action('toggled', content)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_checked(self, content):
        """ Handle the 'set_checked' action from the Enaml widget.

        """
        self.set_checked(content['checked'])

    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        with size_hint_guard(self):
            self.set_text(content['text'])

    def on_action_set_icon_source(self, content):
        """ Handle the 'set_icon_source' action from the Enaml widget.

        """
        self.set_icon_source(content['icon_source'])

    def on_action_set_icon_size(self, content):
        """ Handle the 'set_icon_size' action from the Enaml widget.

        """
        with size_hint_guard(self):
            self.set_icon_size(content['icon_size'])

    #--------------------------------------------------------------------------
    # Widget update methods
    #--------------------------------------------------------------------------
    def set_checkable(self, checkable):
        """ Sets whether or not the widget is checkable.

        """
        self.widget().setCheckable(checkable)

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        widget = self.widget()
        # This handles the case where, by default, Qt will not allow
        # all of the radio buttons in a group to be disabled. By
        # temporarily turning off auto-exclusivity, we are able to
        # handle that case.
        if not checked and widget.isChecked() and widget.autoExclusive():
            widget.setAutoExclusive(False)
            widget.setChecked(checked)
            widget.setAutoExclusive(True)
        else:
            widget.setChecked(checked)

    def set_text(self, text):
        """ Sets the widget's text with the provided value.

        """
        self.widget().setText(text)

    def set_icon_source(self, icon_source):
        """ Sets the widget's icon to the provided image.

        """
        if icon_source:
            loader = self._session.load_resource(icon_source)
            loader.on_load(self._on_icon_load)
        else:
            self._on_icon_load(QIcon())

    def set_icon_size(self, icon_size):
        """ Sets the widget's icon size to the provided size.

        """
        self.widget().setIconSize(QSize(*icon_size))

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_icon_load(self, icon):
        """ A private resource loader callback.

        This method is invoked when the requested icon is successfully
        loaded. It will update the icon on the button widget and issue
        a size hint updated event to the layout system if needed.

        Parameters
        ----------
        icon : QIcon or QImage
            The icon or image that was loaded by the request.

        """
        if isinstance(icon, QImage):
            icon = QIcon(QPixmap.fromImage(icon))
        elif not isinstance(icon, QIcon):
            msg = 'got incorrect type for icon: `%s`'
            logger.error(msg % type(icon).__name__)
            icon = QIcon()
        with size_hint_guard(self):
            self.widget().setIcon(icon)

