#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from atom.api import Atom, Enum, Instance, List

from .image_provider import Image
from .resource import Resource


class IconImage(Atom):
    """ An object representing an image in an icon.

    Instances of this class are used to populate the `images` list of
    an `Icon` instance. Instances of this class should be treated as
    read-only once they are created.

    """
    #: The widget mode for which this icon should apply.
    mode = Enum('normal', 'active', 'disabled', 'selected')

    #: The widget state for which this icon should apply.
    state = Enum('off', 'on')

    #: The image to use for this icon.
    image = Instance(Image)

    def snapshot(self):
        """ Get a snapshot dictionary for this icon image.

        """
        snap = {}
        snap['mode'] = self.mode
        snap['state'] = self.state
        snap['image'] = self.image.snapshot() if self.image else None
        return snap


class Icon(Resource):
    """ A resource object representing an icon.

    Instances of this class are created by an `IconProvider` when it
    handles a request for an icon. Instances of this class should be
    treated as read-only once they are created.

    """
    #: The list of icon images which compose this icon.
    images = List(IconImage)

    def snapshot(self):
        """ Get a snapshot dictionary for this icon.

        """
        snap = super(Icon, self).snapshot()
        snap['images'] = [image.snapshot() for image in self.images]
        return snap


class IconProvider(object):
    """ An abstract API definition for an icon provider object.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def request_icon(self, path, callback):
        """ Request an icon from this provider.

        Parameters
        ----------
        path : str
            The requested path of the icon, with the provider prefix
            removed. For example, if the full icon source path was:
            `icon://myprovider/icons/foo` then the path passed to this
            method will be `icons/foo`.

        callback : callable
            A callable which should be invoked when the icon is loaded.
            It accepts a single argument, which is the loaded `Icon`
            object. It is safe to invoke this callable from a thread.

        """
        raise NotImplementedError

