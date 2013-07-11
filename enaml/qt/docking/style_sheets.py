#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------


#: The global dict of registered stylesheets. This dict should never be
#: modified directly. Use the functions 'register_style_sheet' and
#: 'get_style_sheet' instead.
_style_sheets = {}


def get_style_sheet(name):
    """ Get the style sheet for the given style id.

    Parameters
    ----------
    name : basestring
        The string name of the style previously registered with the
        'register_style_sheet' function.

    Returns
    -------
    result : unicode
        The unicode stylesheet for the style name, or an empty string
        if the style is not found.

    """
    return _style_sheets.get(name, u'')


def register_style_sheet(name, sheet):
    """ Register a dock area style sheet.

    Parameters
    ----------
    name : basestring
        The name to associate with the stylesheet for later lookup.

    sheet : unicode
        A unicode string containing the style sheet for the dock area.

    Raises
    ------
    ValueError
        If the given name is already registered, a value error will be
        raised.

    """
    assert isinstance(sheet, unicode), 'style sheet must a unicode string'
    if name in _style_sheets:
        raise ValueError("'%s' style is already registered" % name)
    _style_sheets[name] = sheet


#: A null stylesheet.
register_style_sheet(u'', u'')


#: A stylesheet inspired by Visual Studio 2010
register_style_sheet(u'vs-2010', u"""
    QDockArea {
        padding: 4px;
        spacing: 5px;
        background: rgb(49, 67, 98);
        border: 1px solid rgb(40, 60, 90);
    }

    QDockSplitterHandle {
        background: rgba(0, 0, 0, 0);
    }

    QDockWindow {
        background: rgb(53, 73, 106);
        border: 1px solid rgb(40, 60, 90);
    }

    QDockRubberBand {
        background: rgba(69, 147, 209, 130);
        border: 2px solid rgb(69, 147, 209);
    }

    QDockContainer {
        background: rgb(53, 73, 106);
    }

    QDockContainer[floating="true"] {
        border: 1px solid rgb(40, 60, 90);
    }

    QDockItem {
        background: rgb(240, 240, 240);
    }

    QDockTitleBar {
        background: rgb(77, 96, 130);
    }

    QDockTitleBar > QTextLabel {
        color: rgb(250, 251, 254);
        font: 9pt "Segoe UI";
    }

    /* Correct a bug in the default pane sizing on Windows 7 */
    QDockTabWidget::pane {}

    QDockTabBar {
        font: 9pt "Segoe UI";
    }

    QDockTabBar::tab {
        background: rgba(255, 255, 255, 15);
        color: rgb(250, 251, 254);
    }

    QDockTabBar::tab:top,
    QDockTabBar::tab:bottom {
        margin-right: 1px;
        padding-left: 5px;
        padding-right: 5px;
        height: 19px;
    }

    QDockTabBar::tab:left,
    QDockTabBar::tab:right {
        margin-bottom: 1px;
        padding-top: 5px;
        padding-bottom: 5px;
        width: 20px;
    }

    QDockTabBar::tab:hover {
        background: rgba(255, 255, 255, 70);
    }

    QDockTabBar::tab:selected {
        background: rgb(240, 240, 240);
        color: black;
    }

    QDockTabBar QBitmapButton,
    QDockTitleBar QBitmapButton,
    QDockWindowButtons QBitmapButton {
        color: rgb(250, 251, 254);
    }

    QBitmapButton#dockwindow-close-button {
        background: #C75050;
    }

    QBitmapButton#dockwindow-close-button:hover {
        background: #E04343;
    }

    QBitmapButton#dockwindow-close-button:pressed {
        background: #993D3D;
    }

    QBitmapButton#dockwindow-maximize-button:hover,
    QBitmapButton#dockwindow-restore-button:hover,
    QBitmapButton#dockwindow-link-button:hover {
        background: #3665B3;
    }

    QBitmapButton#dockwindow-maximize-button:pressed,
    QBitmapButton#dockwindow-restore-button:pressed,
    QBitmapButton#dockwindow-link-button:pressed {
        background: #3D6099;
    }

    QDockTabBar QBitmapButton:hover,
    QDockTitleBar QBitmapButton:hover {
        border: 1px solid rgb(229, 195, 101);
        background: rgb(250, 251, 254);
        color: black;
    }

    QDockTabBar QBitmapButton:pressed,
    QDockTitleBar QBitmapButton:pressed {
        background: rgb(255, 229, 128);
    }

    QBitmapButton#docktab-close-button:selected {
        color: black;
    }

    QDockBar {
        spacing: 3px;
    }

    QDockBarButton {
        padding: 1px 10px 2px 10px;
        border: 1px solid rgba(0, 0, 0, 0);
        background: rgb(77, 96, 130);
        color: rgb(250, 251, 254);
    }

    QDockBarButton::hover {
        border: 1px solid rgb(229, 195, 101);
        background: rgb(250, 251, 254);
        color: black;
    }

    QDockBarButton::checked {
        border: 1px solid rgb(229, 195, 101);
        background: rgb(255, 229, 128);
        color: black;
    }

    QDockBarItem[position="0"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="1"] QDockBarItemHandle {
        background: qlineargradient(x1:1, y1:0, x2:0, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="2"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="3"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }
""")


#: A mild grey and brown stylesheet.
#: Inspired by http://www.colourlovers.com/palette/2866138/Grey_Wind
register_style_sheet(u'grey-wind', u"""
    QDockArea {
        padding: 4px;
        spacing: 5px;
        background: rgb(175, 178, 183);
        border: 1px solid rgb(161, 164, 168);
    }

    QDockWindow > QDockArea {
        border: 1px solid rgb(129, 121, 119);
    }

    QDockSplitterHandle {
        background: rgba(0, 0, 0, 0);
    }

    QDockWindow {
        background: rgb(139, 131, 129);
        background: rgb(149, 141, 139);
        border: 1px solid rgb(129, 121, 119);
    }

    QDockRubberBand {
        background: rgba(175, 178, 183, 130);
        border: 2px solid rgb(100, 100, 100);
    }

    QDockContainer {
        background: rgb(175, 178, 183);
    }

    QDockContainer[floating="true"] {
        border: 1px solid rgb(144, 144, 152);
    }

    QDockItem {
        background: rgb(244, 244, 244);
    }

    QDockTitleBar {
        background: rgb(144, 144, 152);
    }

    QDockTitleBar > QTextLabel {
        color: rgb(244, 244, 244);
        font: 9pt "Segoe UI";
    }

    /* Correct a bug in the default pane sizing on Windows 7 */
    QDockTabWidget::pane {}

    QDockTabBar {
        font: 9pt "Segoe UI";
    }

    QDockTabBar::tab {
        background: rgba(0, 0, 0, 20);
        color: rgb(244, 244, 244);
    }

    QDockTabBar::tab:top,
    QDockTabBar::tab:bottom {
        margin-right: 1px;
        padding-left: 5px;
        padding-right: 5px;
        height: 19px;
    }

    QDockTabBar::tab:left,
    QDockTabBar::tab:right {
        margin-bottom: 1px;
        padding-top: 5px;
        padding-bottom: 5px;
        width: 20px;
    }

    QDockTabBar::tab:hover {
        background: rgb(144, 144, 152);
    }

    QDockTabBar::tab:selected {
        background: rgb(244, 244, 244);
        color: black;
    }

    QDockTabBar QBitmapButton,
    QDockTitleBar QBitmapButton {
        color: rgb(250, 251, 254);
    }

    QDockTabBar QBitmapButton:hover,
    QDockTitleBar QBitmapButton:hover {
        color: rgb(80, 80, 80);
    }

    QDockTabBar QBitmapButton:pressed,
    QDockTitleBar QBitmapButton:pressed {
        color: black;
    }

    QBitmapButton#docktab-close-button:selected {
        color: rgb(80, 80, 80);
    }

    QBitmapButton#docktab-close-button:selected:hover {
        color: black;
    }

    QBitmapButton#dockwindow-close-button {
        background: #C75050;
        color: rgb(250, 251, 254);
    }

    QBitmapButton#dockwindow-close-button:hover {
        background: #E04343;
    }

    QBitmapButton#dockwindow-close-button:pressed {
        background: #993D3D;
    }

    QBitmapButton#dockwindow-maximize-button:hover,
    QBitmapButton#dockwindow-restore-button:hover,
    QBitmapButton#dockwindow-link-button:hover {
        background: rgb(175, 178, 183);
    }

    QBitmapButton#dockwindow-maximize-button:pressed,
    QBitmapButton#dockwindow-restore-button:pressed,
    QBitmapButton#dockwindow-link-button:pressed {
        background: rgb(144, 144, 152);
    }

    QDockBar {
        spacing: 3px;
    }

    QDockBarButton {
        padding: 1px 10px 2px 10px;
        border: 1px solid rgba(0, 0, 0, 0);
        background: rgb(144, 144, 152);
        color: rgb(244, 244, 244);
    }

    QDockBarButton::hover {
        background: rgb(149, 141, 139);
        border: 1px solid rgb(129, 121, 119);
    }

    QDockBarButton::checked {
        background: rgb(149, 141, 139);
        border: 1px solid rgb(129, 121, 119);
        color: black;
    }

    QDockBarItem[position="0"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="1"] QDockBarItemHandle {
        background: qlineargradient(x1:1, y1:0, x2:0, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="2"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="3"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }
""")


#: A yellow, brown, and grey stylesheet.
#: Inspired by http://www.colourlovers.com/palette/90734/Newly_Risen_Moon
register_style_sheet(u'new-moon', u"""
    QDockArea {
        padding: 4px;
        spacing: 5px;
        background: rgb(54, 57, 59);
        border: 1px solid rgb(45, 45, 45);
    }

    QDockWindow > QDockArea {
        border: 1px solid #9E935D;
    }

    QDockSplitterHandle {
        background: rgba(0, 0, 0, 0);
    }

    QDockWindow {
        background: rgb(197, 188, 142);
        border: 1px solid #9E935D;
    }

    QDockRubberBand {
        background: rgba(197, 188, 142, 130);
        border: 2px solid rgb(197, 188, 142);
    }

    QDockContainer {
        background: rgb(54, 57, 59);
    }

    QDockContainer[floating="true"] {
        border: 1px solid rgb(45, 45, 45);
    }

    QDockItem {
        background: rgb(240, 240, 240);
    }

    QDockTitleBar {
        background: rgb(105, 103, 88);
    }

    QDockTitleBar > QTextLabel {
        color: rgb(240, 240, 240);
        font: 9pt "Segoe UI";
    }

    /* Correct a bug in the default pane sizing on Windows 7 */
    QDockTabWidget::pane {}

    QDockTabBar {
        font: 9pt "Segoe UI";
    }

    QDockTabBar::tab {
        background: rgba(255, 255, 255, 30);
        color: rgb(240, 240, 240);
    }

    QDockTabBar::tab:top,
    QDockTabBar::tab:bottom {
        margin-right: 1px;
        padding-left: 5px;
        padding-right: 5px;
        height: 19px;
    }

    QDockTabBar::tab:left,
    QDockTabBar::tab:right {
        margin-bottom: 1px;
        padding-top: 5px;
        padding-bottom: 5px;
        width: 20px;
    }

    QDockTabBar::tab:hover {
        background: rgba(197, 188, 142, 170);
    }

    QDockTabBar::tab:selected {
        background: rgb(240, 240, 240);
        color: black;
    }

    QDockTabBar QBitmapButton,
    QDockTitleBar QBitmapButton {
        color: rgb(240, 240, 240);
    }

    QDockTabBar QBitmapButton:hover,
    QDockTitleBar QBitmapButton:hover {
        color: rgb(50, 50, 50);
    }

    QDockTabBar QBitmapButton:pressed,
    QDockTitleBar QBitmapButton:pressed {
        color: black;
    }

    QBitmapButton#docktab-close-button:selected {
        color: rgb(100, 100, 100);
    }

    QBitmapButton#docktab-close-button:selected:hover {
        color: black;
    }

    QBitmapButton#dockwindow-close-button {
        background: #C75050;
        color: rgb(240, 240, 240);
    }

    QBitmapButton#dockwindow-close-button:hover {
        background: #E04343;
    }

    QBitmapButton#dockwindow-close-button:pressed {
        background: #993D3D;
    }

    QBitmapButton#dockwindow-maximize-button:hover,
    QBitmapButton#dockwindow-restore-button:hover,
    QBitmapButton#dockwindow-link-button:hover {
        background: #9E935D;
    }

    QBitmapButton#dockwindow-maximize-button:pressed,
    QBitmapButton#dockwindow-restore-button:pressed,
    QBitmapButton#dockwindow-link-button:pressed {
        background: rgb(105, 103, 88);
    }

    QDockBar {
        spacing: 3px;
    }

    QDockBarButton {
        padding: 1px 10px 2px 10px;
        border: 1px solid rgba(0, 0, 0, 0);
        background: rgb(105, 103, 88);
        color: rgb(240, 240, 240);
    }

    QDockBarButton::hover {
        background: rgba(197, 188, 142, 170);
    }

    QDockBarButton::checked {
        background: rgb(197, 188, 142);
        color: black;
    }

    QDockBarItem[position="0"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="1"] QDockBarItemHandle {
        background: qlineargradient(x1:1, y1:0, x2:0, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="2"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="3"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }
""")


#: A stylesheet inspired by Windows Metro.
register_style_sheet(u'metro', u"""
    QDockArea {
        padding: 4px;
        spacing: 5px;
        background: #C0C0C0;
        border: 1px solid #B0B0B0;
    }

    QDockSplitterHandle {
        background: rgba(0, 0, 0, 0);
    }

    QDockWindow {
        background: white;
        border: 1px solid #B0B0B0;
    }

    QDockRubberBand {
        background: rgba(255, 255, 255, 130);
        border: 2px solid #666666;
    }

    QDockContainer {
        background: #C0C0C0;
    }

    QDockContainer[floating="true"] {
        border: 1px solid #B0B0B0;
    }

    QDockItem {
        background: rgb(240, 240, 240);
    }

    QDockTitleBar {
        background: rgb(53, 139, 202);
    }

    QDockTitleBar > QTextLabel {
        color: rgb(240, 240, 240);
        font: 9pt "Segoe UI";
    }

    /* Correct a bug in the default pane sizing on Windows 7 */
    QDockTabWidget::pane {}

    QDockTabBar {
        font: 9pt "Segoe UI";
    }

    QDockTabBar::tab {
        background: #838587;
        color: rgb(240, 240, 240);
    }

    QDockTabBar::tab:top,
    QDockTabBar::tab:bottom {
        margin-right: 1px;
        padding-left: 5px;
        padding-right: 5px;
        height: 19px;
    }

    QDockTabBar::tab:left,
    QDockTabBar::tab:right {
        margin-bottom: 1px;
        padding-top: 5px;
        padding-bottom: 5px;
        width: 20px;
    }

    QDockTabBar::tab:hover {
        background: #959799;
    }

    QDockTabBar::tab:selected {
        background: rgb(240, 240, 240);
        color: black;
    }

    QDockTabBar QBitmapButton,
    QDockTitleBar QBitmapButton {
        color: rgb(240, 240, 240);
    }

    QDockTabBar QBitmapButton:hover,
    QDockTitleBar QBitmapButton:hover {
        color: black;
    }

    QBitmapButton#docktab-close-button:selected {
        color: rgb(100, 100, 100);
    }

    QBitmapButton#docktab-close-button:selected:hover {
        color: black;
    }

    QBitmapButton#dockwindow-close-button {
        background: #C75050;
        color: white;
    }

    QBitmapButton#dockwindow-close-button:hover {
        background: #E04343;
    }

    QBitmapButton#dockwindow-close-button:pressed {
        background: #993D3D;
    }

    QBitmapButton#dockwindow-maximize-button:hover,
    QBitmapButton#dockwindow-restore-button:hover,
    QBitmapButton#dockwindow-link-button:hover {
        background: #3665B3;
        color: white;
    }

    QBitmapButton#dockwindow-maximize-button:pressed,
    QBitmapButton#dockwindow-restore-button:pressed,
    QBitmapButton#dockwindow-link-button:pressed {
        background: #3D6099;
    }

    QDockBar {
        spacing: 3px;
    }

    QDockBarButton {
        padding: 1px 10px 2px 10px;
        border: 1px solid rgba(0, 0, 0, 0);
        background: rgb(53, 139, 202);
        color: rgb(240, 240, 240);
    }

    QDockBarButton::hover {
        background: rgb(61, 159, 229);
    }

    QDockBarButton::checked {
        background: #838587;
    }

    QDockBarItem[position="0"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="1"] QDockBarItemHandle {
        background: qlineargradient(x1:1, y1:0, x2:0, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="2"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }

    QDockBarItem[position="3"] QDockBarItemHandle {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(50, 50, 50, 175),
                    stop:1 rgba(50, 50, 50, 0));
    }
""")
