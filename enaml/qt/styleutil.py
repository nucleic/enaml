#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import re

from enaml.styling import StyleCache


_grad_re = re.compile(r'(lineargradient|radialgradient)')

_alert_re = re.compile(r'alert\((-?[_a-zA-Z][_a-zA-Z0-9-]*)\)')


def _translate_gradient(v):
    return _grad_re.sub(r'q\1', v)


_KNOWN_FIELDS = set([
    'alternate-background-color',
    'background',
    'background-clip',
    'background-color',
    'border',
    'border-top',
    'border-right',
    'border-bottom',
    'border-left',
    'border-color',
    'border-top-color',
    'border-right-color',
    'border-bottom-color',
    'border-left-color',
    'border-radius',
    'border-top-left-radius',
    'border-top-right-radius',
    'border-bottom-right-radius',
    'border-bottom-left-radius',
    'border-style',
    'border-top-style',
    'border-right-style',
    'border-bottom-style',
    'border-left-style',
    'border-width',
    'border-top-width',
    'border-right-width',
    'border-bottom-width',
    'border-left-width',
    'bottom',
    'color',
    'font',
    'font-family',
    'font-size',
    'font-style',
    'font-weight',
    'height',
    'icon-size',
    'left',
    'line-edit-password-character',
    'margin',
    'margin-top',
    'margin-right',
    'margin-bottom',
    'margin-left',
    'max-height',
    'max-width',
    'min-height',
    'min-width',
    'padding',
    'padding-top',
    'padding-right',
    'padding-bottom',
    'padding-left',
    'position',
    'right',
    'selection-background-color',
    'selection-color',
    'spacing',
    'subcontrol-origin',
    'subcontrol-position',
    'text-align',
    'text-decoration',
    'top',
    'width',
])


_MAY_HAVE_GRADIENT = set([
    'background',
    'background-color',
    'border',
    'border-top',
    'border-right',
    'border-bottom',
    'border-left',
    'border-color',
    'border-top-color',
    'border-right-color',
    'border-bottom-color',
    'border-left-color',
    'color',
    'selection-background-color',
    'selection-color',
])


def _translate_setter(setter):
    field = setter.field
    if field in _KNOWN_FIELDS:
        value = setter.value
        if value:
            if field in _MAY_HAVE_GRADIENT:
                value = _translate_gradient(value)
            value = '    %s: %s;' % (field, value)
            return value


def _translate_style_body(style):
    translated = []
    for setter in style.setters():
        tks = StyleCache.toolkit_setter(setter, _translate_setter)
        if tks is not None:
            translated.append(tks)
    return '\n'.join(translated)


def translate_style(name, style):
    parts = ['#%s' % name]
    if style.pseudo_element:
        root = parts.pop()
        for pe in style.pseudo_element.split(','):
            parts.append(root + '::%s' % pe.strip())
    if style.pseudo_class:
        these = parts[:]
        parts = []
        for pc in style.pseudo_class.split(','):
            pc = pc.strip()
            for this in these:
                parts.append(this + ':%s' % pc)
    selector = ','.join(parts)
    body = '{\n%s\n}' % _translate_style_body(style)
    return '%s %s' % (selector, body)


#------------------------------------------------------------------------------
# Dock Area Styling
#------------------------------------------------------------------------------
def _basic_pc(root, pc):
    if pc:
        root += ':%s' % pc
    return root


def _base_dock_area(name, pc):
    rest = []
    floating = False
    for part in pc.split(':'):
        if part == 'floating':
            floating = True
        else:
            rest.append(part)
    if floating:
        root = 'QDockWindow > QDockArea'
    else:
        root = 'QDockArea'
    return _basic_pc(root, ':'.join(rest))


def _dock_bar(name, pc):
    return _basic_pc('QDockBar', pc)


def _dock_bar_button(name, pc):
    return _maybe_alert('QDockBarButton', name, pc)


_position_map = {'top': '0', 'right': '1', 'bottom': '2', 'left': '3'}
def _dock_bar_handle(name, pc):
    rest = []
    position = None
    for part in pc.split(':'):
        if part in _position_map:
            position = _position_map[part]
        else:
            rest.append(part)
    if position is not None:
        root = 'QDockBarItem[position="%s"] QDockBarItemHandle' % position
    else:
        root = 'QDockBarItem QDockBarItemHandle'
    return _basic_pc(root, ':'.join(rest))


def _dock_container(name, pc):
    rest = []
    tabbed = False
    floating = False
    for part in pc.split(':'):
        if part == 'tabbed':
            tabbed = True
        elif part == 'floating':
            floating = True
        else:
            rest.append(part)
    if tabbed:
        root = 'QDockTabWidget QDockContainer'
    elif floating:
        root = 'QDockContainer[floating="true"]'
    else:
        root = 'QDockContainer'
    return _maybe_alert(root, name, ':'.join(rest))


def _dock_window(name, pc):
    return _basic_pc('QDockWindow', pc)


def _dock_window_button(name, pc):
    return _basic_pc('QDockWindowButtons QBitmapButton', pc)


def _dock_window_close_button(name, pc):
    return _basic_pc('QBitmapButton#dockwindow-close-button', pc)


def _dock_window_link_button(name, pc):
    return _basic_pc('QBitmapButton#dockwindow-link-button', pc)


def _dock_window_maximize_button(name, pc):
    return _basic_pc('QBitmapButton#dockwindow-maximize-button', pc)


def _dock_window_restore_button(name, pc):
    return _basic_pc('QBitmapButton#dockwindow-restore-button', pc)


def _rubber_band(name, pc):
    return _basic_pc('QDockRubberBand', pc)


def _splitter_handle(name, pc):
    return _basic_pc('QDockSplitter::handle', pc)


def _tab_bar(name, pc):
    return _basic_pc('QDockTabBar', pc)


def _tab_bar_tab(name, pc):
    rest = []
    alert = ''
    for part in pc.split(':'):
        match = _alert_re.match(part)
        if match is not None:
            alert = match.group(1)
        else:
            rest.append(part)
    if alert:
        root = 'QDockTabBar[alert="%s"]::tab' % alert
    else:
        root = 'QDockTabBar::tab'
    return _basic_pc(root, ':'.join(rest))


def _tab_bar_close_button(name, pc):
    return _basic_pc('QBitmapButton#docktab-close-button', pc)


def _maybe_alert(root, name, pc):
    rest = []
    alert = ''
    for part in pc.split(':'):
        match = _alert_re.match(part)
        if match is not None:
            alert = match.group(1)
        else:
            rest.append(part)
    if alert:
        root = '%s[alert="%s"]' % (root, alert)
    return _basic_pc(root, ':'.join(rest))


def _base_dock_item(name, pc):
    rest = []
    tabbed = False
    floating = False
    for part in pc.split(':'):
        if part == 'tabbed':
            tabbed = True
        elif part == 'floating':
            floating = True
        else:
            rest.append(part)
    if tabbed:
        root = 'QDockTabWidget QDockItem'
    elif floating:
        root = 'QDockContainer[floating="true"] QDockItem'
    else:
        root = 'QDockItem'
    return _maybe_alert(root, name, ':'.join(rest))


def _title_bar(name, pc):
    return _maybe_alert('QDockTitleBar', name, pc)


def _title_bar_label(name, pc):
    return _maybe_alert('QDockTitleBar > QTextLabel', name, pc)


def _title_bar_button(name, pc):
    return _basic_pc('QDockTitleBar > QBitmapButton', pc)


def _title_bar_close_button(name, pc):
    return _basic_pc('QBitmapButton#docktitlebar-close-button', pc)


def _title_bar_link_button(name, pc):
    return _basic_pc('QBitmapButton#docktitlebar-link-button', pc)


def _title_bar_maximize_button(name, pc):
    return _basic_pc('QBitmapButton#docktitlebar-maximize-button', pc)


def _title_bar_pin_button(name, pc):
    return _basic_pc('QBitmapButton#docktitlebar-pin-button', pc)


def _title_bar_restore_button(name, pc):
    return _basic_pc('QBitmapButton#docktitlebar-restore-button', pc)


_DOCK_AREA_PSEUDO_ELEMENTS = {
    '': _base_dock_area,
    'dock-bar': _dock_bar,
    'dock-bar-button': _dock_bar_button,
    'dock-bar-handle': _dock_bar_handle,
    'dock-container': _dock_container,
    'dock-window': _dock_window,
    'dock-window-button': _dock_window_button,
    'dock-window-close-button': _dock_window_close_button,
    'dock-window-link-button': _dock_window_link_button,
    'dock-window-maximize-button': _dock_window_maximize_button,
    'dock-window-restore-button': _dock_window_restore_button,
    'rubber-band': _rubber_band,
    'splitter-handle': _splitter_handle,
    'tab-bar': _tab_bar,
    'tab-bar-tab': _tab_bar_tab,
    'tab-bar-close-button': _tab_bar_close_button,
}


_DOCK_ITEM_PSEUDO_ELEMENTS = {
    '': _base_dock_item,
    'title-bar': _title_bar,
    'title-bar-label': _title_bar_label,
    'title-bar-button': _title_bar_button,
    'title-bar-close-button': _title_bar_close_button,
    'title-bar-link-button': _title_bar_link_button,
    'title-bar-maximize-button': _title_bar_maximize_button,
    'title-bar-pin-button': _title_bar_pin_button,
    'title-bar-restore-button': _title_bar_restore_button,
}


def _dock_style_selector(name, style, elements):
    handlers = []
    for pe in style.pseudo_element.split(','):
        handler = elements.get(pe.strip())
        if handler:
            handlers.append(handler)
    if not handlers:
        return
    parts = []
    for pc in style.pseudo_class.split(','):
        pc = pc.strip()
        for handler in handlers:
            parts.append(handler(name, pc))
    return ', '.join(parts)


def translate_dock_area_style(name, style):
    selector = _dock_style_selector(name, style, _DOCK_AREA_PSEUDO_ELEMENTS)
    if not selector:
        return
    body = '{\n%s\n}' % _translate_style_body(style)
    return '%s %s' % (selector, body)


def translate_dock_item_style(name, style):
    selector = _dock_style_selector(name, style, _DOCK_ITEM_PSEUDO_ELEMENTS)
    if not selector:
        return
    body = '{\n%s\n}' % _translate_style_body(style)
    return '%s %s' % (selector, body)
