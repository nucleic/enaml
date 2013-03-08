#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import logging

from .qt.QtGui import QImage, QIcon, QPixmap


logger = logging.getLogger(__name__)


_ICON_MODE_MAP = {
    'normal': QIcon.Normal,
    'disabled': QIcon.Disabled,
    'active': QIcon.Active,
    'selected': QIcon.Selected,
}


_ICON_STATE_MAP = {
    'off': QIcon.Off,
    'on': QIcon.On,
}


def convert_from_Image(image):
    """ Convert the given resource dict into a QImage.

    Parameters
    ----------
    image : dict
        A dictionary representation of an Enaml Image.

    Returns
    -------
    result : QImage
        The QImage instance for the given Enaml image dict.

    """
    format = image['format']
    if format == 'auto':
        format = ''
    return QImage.fromData(image['data'], format)


def convert_from_Icon(icon):
    """ Convert the given resource dict into a QIcon.

    Parameters
    ----------
    image : dict
        A dictionary representation of an Enaml Icon.

    Returns
    -------
    result : QIcon
        The QIcon instance for the given Enaml icon dict.

    """
    qicon = QIcon()
    for img in icon['images']:
        mode = _ICON_MODE_MAP[img['mode']]
        state = _ICON_STATE_MAP[img['state']]
        image = convert_resource(img['image'])
        qicon.addPixmap(QPixmap.fromImage(image), mode, state)
    return qicon


def convert_resource(resource):
    """ Convert a resource dict into a Qt resource handle.

    Parameters
    ----------
    resource : dict
        A dictionary representation of the Qt resource to create.

    Returns
    -------
    result : QObject or None
        An appropriate Qt object for the resource, or None if the
        resource could not be converted.

    """
    items = globals()
    name = resource['class']
    handler = items.get('convert_from_' + name)
    if handler is None:
        for name in resource['bases']:
            handler = items.get('load_' + name)
            if handler is not None:
                break
        if handler is None:
            msg = 'failed to create resource `%s:%s`'
            logger.error(msg % (resource['class'], resource['bases']))
            return
    return handler(resource)

