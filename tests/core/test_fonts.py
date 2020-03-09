# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import pytest

from enaml.fonts import (coerce_font, Font, _SIZES, _UNITS, _WEIGHTS, _STYLES,
                         _VARIANTS, _STRETCH)

# The order defining a CSS3 string is:
# style variant weight stretch size line-height family.
# In our case line-height is not supported


@pytest.mark.parametrize('family', ['Helvetica', 'Arial'])
@pytest.mark.parametrize('size', ['small', 'medium', 'large',
                                  '1in', '1cm', '10mm', '10pt', '10pc', '10px']
                         )
@pytest.mark.parametrize('weight', ['', 'normal', 'bold', '300'])
@pytest.mark.parametrize('style', ['', 'normal', 'italic', 'oblique'])
@pytest.mark.parametrize('variant', ['', 'normal', 'small-caps'])
@pytest.mark.parametrize('stretch', ['', 'condensed', 'normal', 'expanded'])
def test_font_coercion(family, size, weight, style, variant, stretch):
    """Test the font parsing produce the expected font objects.

    """
    font = ' '.join([style, variant, weight,
                     stretch, size, family])
    font = ' '.join(font.split())  # Handle multiple whitespaces
    print('CSS3 font: ', font)
    font = coerce_font(font)
    assert isinstance(font, Font)
    assert repr(font)

    assert font.family == family
    if size in _SIZES:
        assert font.pointsize == _SIZES[size]
    else:
        pt_size = (_UNITS[size[-2:]](int(size[:-2])) if len(size) > 2
                   else int(size))
        assert font.pointsize == pt_size
    assert font.weight == _WEIGHTS[weight or 'normal']
    assert font.style == _STYLES[style or 'normal']
    assert font.caps == _VARIANTS[variant or 'normal']
    assert font.stretch == _STRETCH[stretch or 'normal']

    assert font._tkdata is None

    try:
        from enaml.qt.q_resource_helpers import get_cached_qfont
    except Exception:
        return
    get_cached_qfont(font)
    assert font._tkdata is not None
