#------------------------------------------------------------------------------
# Copyright (c) 2019, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Test the button group widget.

"""
import pytest

from utils import is_qt_available, compile_source, wait_for_window_displayed


SOURCE ="""
import os
from enaml.image import Image
from enaml.widgets.api import Window, Container, ImageView

def image_path(name):
    dirname = os.path.dirname(r"%s")
    return os.path.join(dirname, 'images', name)

IMAGES = {
    'None': None,
    'Image A': Image(data=open(image_path('img1.png'), 'rb').read()),
}

enamldef Main(Window):

    attr img_name = 'None'
    alias view: img

    Container:
        ImageView: img:
            image << IMAGES[img_name]

""" % __file__


@pytest.mark.skipif(not is_qt_available(), reason='Requires a Qt binding')
def test_displaying_no_image(enaml_qtbot, enaml_sleep):
    """Test that we can set the image attribute to None.

    """
    win = compile_source(SOURCE, 'Main')()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)
    enaml_qtbot.wait(enaml_sleep)

    win.img_name = 'Image A'
    enaml_qtbot.wait(enaml_sleep)


# XXX The following test require to compare to a reference image since we
# cannot access the size of the painted area to ensure that scaling was done
# properly

# @pytest.mark.skipif(not is_qt_available(), reason='Requires a Qt binding')
# @pytest.mark.parametrize('factor', [0.5, 2])
# def test_refuse_to_scale(enaml_qtbot, enaml_sleep, factor):
#     """Test that we do not scale the image if scale_to_fit is False.

#     """
#     win = compile_source(SOURCE, 'Main')()
#     win.img_name = 'Image A'
#     win.show()
#     wait_for_window_displayed(enaml_qtbot, win)

#     img_size = win.view.proxy.widget.size()
#     size = win.size()
#     win.set_size((size.width*factor, size.height*factor))
#     enaml_qtbot.wait(enaml_sleep)

#     new_img_size = win.view.proxy.widget.size()
#     assert new_img_size.width() == img_size.width()
#     assert new_img_size.height() == img_size.height()


# @pytest.mark.skipif(not is_qt_available(), reason='Requires a Qt binding')
# @pytest.mark.parametrize('preserve_aspect_ratio', [False, True])
# def test_downscale(enaml_qtbot, enaml_sleep, preserve_aspect_ratio):
#     """Test that scale_to_fit will allow to downscale the image.

#     """
#     win = compile_source(SOURCE, 'Main')()
#     win.img_name = 'Image A'
#     win.view.scale_to_fit = True
#     win.view.preserve_aspect_ratio = preserve_aspect_ratio
#     win.show()
#     wait_for_window_displayed(enaml_qtbot, win)

#     img_size = win.view.proxy.widget.size()
#     size = win.size()
#     win.set_size((size.width*0.2, size.height*0.5))
#     enaml_qtbot.wait(enaml_sleep)

#     new_img_size = win.view.proxy.widget.size()
#     assert new_img_size.width() < img_size.width()
#     assert new_img_size.height() < img_size.height()
#     if preserve_aspect_ratio:
#         assert new_img_size.width()/new_img_size.height() ==\
#             img_size.width()/img_size.height()
#     else:
#         assert new_img_size.width()/new_img_size.height() !=\
#             img_size.width()/img_size.height()


# @pytest.mark.skipif(not is_qt_available(), reason='Requires a Qt binding')
# @pytest.mark.parametrize('preserve_aspect_ratio', [False, True])
# @pytest.mark.parametrize('allow_upscaling', [False, True])
# def test_upscale(enaml_qtbot, enaml_sleep, preserve_aspect_ratio,
#                  allow_upscaling):
#     """Test that scale_to_fit and allow_upscaling allow to upscale.

#     """
#     win = compile_source(SOURCE, 'Main')()
#     win.img_name = 'Image A'
#     win.view.scale_to_fit = True
#     win.view.preserve_aspect_ratio = preserve_aspect_ratio
#     win.show()
#     wait_for_window_displayed(enaml_qtbot, win)

#     img_size = win.view.proxy.widget.size()
#     size = win.size()
#     win.set_size((size.width*2, size.height*4))
#     enaml_qtbot.wait(enaml_sleep)

#     new_img_size = win.view.proxy.widget.size()
#     if allow_upscaling:
#         assert new_img_size.width() > img_size.width()
#         assert new_img_size.height() > img_size.height()
#     else:
#         assert new_img_size.width() == img_size.width()
#         assert new_img_size.height() == img_size.height()
#     if preserve_aspect_ratio:
#         assert new_img_size.width()/new_img_size.height() ==\
#             img_size.width()/img_size.height()
#     else:
#         assert new_img_size.width()/new_img_size.height() !=\
#             img_size.width()/img_size.height()
