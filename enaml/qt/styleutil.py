#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import re


_grad_re = re.compile('(lineargradient|radialgradient)')


def _translate_gradient(v):
    return _grad_re.sub(r'q\1', v)


KNOWN_PROPERTIES = set([
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


MAY_HAVE_GRADIENT = set([
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


def translate_style_property(prop):
    tkdata = prop._tkdata
    if tkdata is not None:
        return tkdata
    name = prop.name
    if name in KNOWN_PROPERTIES:
        tkdata = prop.value
        if tkdata:
            if name in MAY_HAVE_GRADIENT:
                tkdata = _translate_gradient(tkdata)
            tkdata = '%s:%s;' % (name, tkdata)
        prop._tkdata = tkdata
    return tkdata
