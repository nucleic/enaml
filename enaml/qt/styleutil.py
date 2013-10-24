#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import re


_grad_re = re.compile(ur'(lineargradient|radialgradient)')


def _translate_gradient(v):
    return _grad_re.sub(ur'q\1', v)


KNOWN_FIELDS = set([
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


MAY_HAVE_GRADIENT = set([
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


def translate_setter(setter):
    field = setter.field
    if field in KNOWN_FIELDS:
        value = setter.value
        if value:
            if field in MAY_HAVE_GRADIENT:
                value = _translate_gradient(value)
            value = u'%s:%s;' % (field, value)
        return value
