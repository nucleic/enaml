#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import re

from enaml.styling import StyleCache


_grad_re = re.compile(ur'(lineargradient|radialgradient)')


def _translate_gradient(v):
    return _grad_re.sub(ur'q\1', v)


_KNOWN_FIELDS = set([
    u'alternate-background-color',
    u'background',
    u'background-clip',
    u'background-color',
    u'border',
    u'border-top',
    u'border-right',
    u'border-bottom',
    u'border-left',
    u'border-color',
    u'border-top-color',
    u'border-right-color',
    u'border-bottom-color',
    u'border-left-color',
    u'border-radius',
    u'border-top-left-radius',
    u'border-top-right-radius',
    u'border-bottom-right-radius',
    u'border-bottom-left-radius',
    u'border-style',
    u'border-top-style',
    u'border-right-style',
    u'border-bottom-style',
    u'border-left-style',
    u'border-width',
    u'border-top-width',
    u'border-right-width',
    u'border-bottom-width',
    u'border-left-width',
    u'bottom',
    u'color',
    u'font',
    u'font-family',
    u'font-size',
    u'font-style',
    u'font-weight',
    u'height',
    u'icon-size',
    u'left',
    u'line-edit-password-character',
    u'margin',
    u'margin-top',
    u'margin-right',
    u'margin-bottom',
    u'margin-left',
    u'max-height',
    u'max-width',
    u'min-height',
    u'min-width',
    u'padding',
    u'padding-top',
    u'padding-right',
    u'padding-bottom',
    u'padding-left',
    u'position',
    u'right',
    u'selection-background-color',
    u'selection-color',
    u'spacing',
    u'subcontrol-origin',
    u'subcontrol-position',
    u'text-align',
    u'text-decoration',
    u'top',
    u'width',
])


_MAY_HAVE_GRADIENT = set([
    u'background',
    u'background-color',
    u'border',
    u'border-top',
    u'border-right',
    u'border-bottom',
    u'border-left',
    u'border-color',
    u'border-top-color',
    u'border-right-color',
    u'border-bottom-color',
    u'border-left-color',
    u'color',
    u'selection-background-color',
    u'selection-color',
])


def _translate_setter(setter):
    field = setter.field
    if field in _KNOWN_FIELDS:
        value = setter.value
        if value:
            if field in _MAY_HAVE_GRADIENT:
                value = _translate_gradient(value)
            value = u'    %s: %s;' % (field, value)
        return value


def _translate_style_body(style):
    translated = []
    for setter in style.setters():
        tks = StyleCache.toolkit_setter(setter, _translate_setter)
        if tks is not None:
            translated.append(tks)
    return u'\n'.join(translated)


def translate_style(name, style):
    parts = [u'#%s' % name]
    if style.pseudo_element:
        root = parts.pop()
        for pe in style.pseudo_element.split(u','):
            parts.append(root + u'::%s' % pe.strip())
    if style.pseudo_class:
        these = parts[:]
        parts = []
        for pc in style.pseudo_class.split(u','):
            pc = pc.strip()
            for this in these:
                parts.append(this + u':%s' % pc)
    selector = u','.join(parts)
    body = u'{\n%s\n}' % _translate_style_body(style)
    return u'%s %s' % (selector, body)


#------------------------------------------------------------------------------
# Dock Area Styling
#------------------------------------------------------------------------------
def _basic_pc(root, pc):
    if pc:
        root += u':%s' % pc
    return root


def _base_area(pc):
    return _basic_pc(u'QDockArea', pc)


def _dock_bar(pc):
    return _basic_pc(u'QDockBar', pc)


def _dock_bar_button(pc):
    return _basic_pc(u'QDockBarButton', pc)


_position_map = {'top': '0', 'right': '1', 'bottom': '2', 'left': '3'}
def _dock_bar_handle(pc):
    rest = []
    position = None
    for part in pc.split(u':'):
        part = part.strip()
        if part in _position_map:
            position = _position_map[part]
        else:
            rest.append(part)
    if position is not None:
        root = u'QDockBarItem[position="%s"] QDockBarItemHandle' % position
    else:
        root = u'QDockBarItem QDockBarItemHandle'
    return _basic_pc(root, u':'.join(rest))


def _dock_window(pc):
    return _basic_pc(u'QDockWindow', pc)


def _dock_window_button(pc):
    return _basic_pc(u'QDockWindowButtons QBitmapButton', pc)


def _dock_window_close_button(pc):
    return _basic_pc(u'QBitmapButton#dockwindow-close-button', pc)


def _dock_window_link_button(pc):
    return _basic_pc(u'QBitmapButton#dockwindow-link-button', pc)


def _dock_window_maximize_button(pc):
    return _basic_pc(u'QBitmapButton#dockwindow-maximize-button', pc)


def _dock_window_restore_button(pc):
    return _basic_pc(u'QBitmapButton#dockwindow-restore-button', pc)


def _rubber_band(pc):
    return _basic_pc(u'QDockRubberBand', pc)


def _splitter_handle(pc):
    return _basic_pc(u'QDockSplitter::handle', pc)


def _tab_bar(pc):
    return _basic_pc(u'QDockTabBar', pc)


def _tab_bar_tab(pc):
    return _basic_pc(u'QDockTabBar::tab', pc)


def _tab_bar_close_button(pc):
    return _basic_pc(u'QBitmapButton#docktab-close-button', pc)


_DOCK_AREA_PSEUDO_ELEMENTS = {
    u'': _base_area,
    u'dock-bar': _dock_bar,
    u'dock-bar-button': _dock_bar_button,
    u'dock-bar-handle': _dock_bar_handle,
    u'dock-window': _dock_window,
    u'dock-window-button': _dock_window_button,
    u'dock-window-close-button': _dock_window_close_button,
    u'dock-window-link-button': _dock_window_link_button,
    u'dock-window-maximize-button': _dock_window_maximize_button,
    u'dock-window-restore-button': _dock_window_restore_button,
    u'rubber-band': _rubber_band,
    u'splitter-handle': _splitter_handle,
    u'tab-bar': _tab_bar,
    u'tab-bar-tab': _tab_bar_tab,
    u'tab-bar-close-button': _tab_bar_close_button,
}


def translate_dock_area_style(name, style):
    handlers = []
    for pe in style.pseudo_element.split(u','):
        handler = _DOCK_AREA_PSEUDO_ELEMENTS.get(pe.strip())
        if handler:
            handlers.append(handler)
    if not handlers:
        return
    parts = []
    for pc in style.pseudo_class.split(u','):
        pc = pc.strip()
        for handler in handlers:
            parts.append(handler(pc))
    selector = u','.join(parts)
    body = u'{%s}' % _translate_style_body(style)
    extra = u'QDockTabWidget::pane{}'  # workaround win-7 sizing bug
    return u'%s%s%s' % (extra, selector, body)
