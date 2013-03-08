#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Str, observe, set_default

from enaml.declarative.api import d_

from .control import Control


class ImageView(Control):
    """ A widget which can display an Image with optional scaling.

    """
    #: The source url of the image to load.
    source = d_(Str())

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

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attribute for the control.

        """
        snap = super(ImageView, self).snapshot()
        snap['source'] = self.source
        snap['scale_to_fit'] = self.scale_to_fit
        snap['allow_upscaling'] = self.allow_upscaling
        snap['preserve_aspect_ratio'] = self.preserve_aspect_ratio
        return snap

    @observe(r'^(source|scale_to_fit|allow_upscaling|preserve_aspect_ratio)$',
             regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(ImageView, self).send_member_change(change)

