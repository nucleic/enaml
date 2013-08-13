#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Typed, ForwardTyped, observe, set_default

from enaml.core.declarative import d_
from enaml.image import Image

from .control import Control, ProxyControl


class ProxyImageView(ProxyControl):
    """ The abstract definition of a proxy ImageView object.

    """
    #: A reference to the ImageView declaration.
    declaration = ForwardTyped(lambda: ImageView)

    def set_image(self, image):
        raise NotImplementedError

    def set_scale_to_fit(self, scale):
        raise NotImplementedError

    def set_allow_upscaling(self, allow):
        raise NotImplementedError

    def set_preserve_aspect_ratio(self, preserve):
        raise NotImplementedError


class ImageView(Control):
    """ A widget which can display an Image with optional scaling.

    """
    #: The image to display in the viewer.
    image = d_(Typed(Image))

    #: Whether or not to scale the image with the size of the component.
    scale_to_fit = d_(Bool(False))

    #: Whether to allow upscaling of an image if scale_to_fit is True.
    allow_upscaling = d_(Bool(True))

    #: Whether or not to preserve the aspect ratio if scaling the image.
    preserve_aspect_ratio = d_(Bool(True))

    #: An image view hugs its width weakly by default.
    hug_width = set_default('weak')

    #: An image view hugs its height weakly by default.
    hug_height = set_default('weak')

    #: A reference to the ProxyImageView object.
    proxy = Typed(ProxyImageView)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('image', 'scale_to_fit', 'allow_upscaling', 'preserve_aspect_ratio')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(ImageView, self)._update_proxy(change)
