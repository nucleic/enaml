#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.image_view import ProxyImageView

from .QtGui import QFrame, QPainter, QPixmap

from .q_resource_helpers import get_cached_qimage
from .qt_constraints_widget import size_hint_guard
from .qt_control import QtControl


class QImageView(QFrame):
    """ A custom QFrame that will paint a QPixmap as an image. The
    api is similar to QLabel, but with a few more options to control
    how the image scales.

    """
    def __init__(self, parent=None):
        """ Initialize a QImageView.

        Parameters
        ----------
        parent : QWidget or None, optional
            The parent widget of this image viewer.

        """
        super(QImageView, self).__init__(parent)
        self._pixmap = None
        self._scaled_contents = False
        self._allow_upscaling = False
        self._preserve_aspect_ratio = False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def paintEvent(self, event):
        """ A custom paint event handler which draws the image according
        to the current size constraints.

        """
        pixmap = self._pixmap
        if pixmap is None:
            return

        pm_size = pixmap.size()
        pm_width = pm_size.width()
        pm_height = pm_size.height()
        if pm_width == 0 or pm_height == 0:
            return

        # Use the widget rect instead of the event rect so the image
        # paints properly in a scroll area where it may be clipped.
        evt_rect = self.rect()
        evt_x = evt_rect.x()
        evt_y = evt_rect.y()
        evt_width = evt_rect.width()
        evt_height = evt_rect.height()

        if not self._scaled_contents:
            # If the image isn't scaled, it is centered if possible.
            # Otherwise, it's painted at the origin and clipped.
            paint_x = max(0, int((evt_width / 2. - pm_width / 2.) + evt_x))
            paint_y = max(0, int((evt_height / 2. - pm_height / 2.) + evt_y))
            paint_width = pm_width
            paint_height = pm_height
        else:
            # If the image *is* scaled, it's scaled size depends on the
            # size of the paint area as well as the other scaling flags.
            if self._preserve_aspect_ratio:
                pm_ratio = float(pm_width) / pm_height
                evt_ratio = float(evt_width) / evt_height
                if evt_ratio >= pm_ratio:
                    if self._allow_upscaling:
                        paint_height = evt_height
                    else:
                        paint_height = min(pm_height, evt_height)
                    paint_width = int(paint_height * pm_ratio)
                else:
                    if self._allow_upscaling:
                        paint_width = evt_width
                    else:
                        paint_width = min(pm_width, evt_width)
                    paint_height = int(paint_width / pm_ratio)
            else:
                if self._allow_upscaling:
                    paint_height = evt_height
                    paint_width = evt_width
                else:
                    paint_height = min(pm_height, evt_height)
                    paint_width = min(pm_width, evt_width)
            # In all cases of scaling, we know that the scaled image is
            # no larger than the paint area, and can thus be centered.
            paint_x = int((evt_width / 2. - paint_width / 2.) + evt_x)
            paint_y = int((evt_height / 2. - paint_height / 2.) + evt_y)

        # Finally, draw the pixmap into the calculated rect.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(paint_x, paint_y, paint_width, paint_height, pixmap)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def sizeHint(self):
        """ Returns a appropriate size hint for the image based on the
        underlying QPixmap.

        """
        pixmap = self._pixmap
        if pixmap is not None:
            return pixmap.size()
        return super(QImageView, self).sizeHint()

    def pixmap(self):
        """ Returns the underlying pixmap for the image view.

        """
        return self._pixmap

    def setPixmap(self, pixmap):
        """ Set the pixmap to use as the image in the widget.

        Parameters
        ----------
        pixamp : QPixmap
            The QPixmap to use as the image in the widget.

        """
        self._pixmap = pixmap
        self.update()

    def scaledContents(self):
        """ Returns whether or not the contents scale with the widget
        size.

        """
        return self._scaled_contents

    def setScaledContents(self, scaled):
        """ Set whether the contents scale with the widget size.

        Parameters
        ----------
        scaled : bool
            If True, the image will be scaled to fit the widget size,
            subject to the other sizing constraints in place. If False,
            the image will not scale and will be clipped as required.

        """
        self._scaled_contents = scaled
        self.update()

    def allowUpscaling(self):
        """ Returns whether or not the image can be scaled greater than
        its natural size.

        """
        return self._allow_upscaling

    def setAllowUpscaling(self, allow):
        """ Set whether or not to allow the image to be scaled beyond
        its natural size.

        Parameters
        ----------
        allow : bool
            If True, then the image may be scaled larger than its
            natural if it is scaled to fit. If False, the image will
            never be scaled larger than its natural size. In either
            case, the image may be scaled smaller.

        """
        self._allow_upscaling = allow
        self.update()

    def preserveAspectRatio(self):
        """ Returns whether or not the aspect ratio of the image is
        maintained during a resize.

        """
        return self._preserve_aspect_ratio

    def setPreserveAspectRatio(self, preserve):
        """ Set whether or not to preserve the image aspect ratio.

        Parameters
        ----------
        preserve : bool
            If True then the aspect ratio of the image will be preserved
            if it is scaled to fit. Otherwise, the aspect ratio will be
            ignored.

        """
        self._preserve_aspect_ratio = preserve
        self.update()


class QtImageView(QtControl, ProxyImageView):
    """ A Qt implementation of an Enaml ProxyImageView.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QImageView)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QImageView widget.

        """
        self.widget = QImageView(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying control.

        """
        super(QtImageView, self).init_widget()
        d = self.declaration
        self.set_image(d.image)
        self.set_scale_to_fit(d.scale_to_fit)
        self.set_allow_upscaling(d.allow_upscaling)
        self.set_preserve_aspect_ratio(d.preserve_aspect_ratio)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_image(self, image, sh_guard=True):
        """ Set the image on the underlying widget.

        """
        qpixmap = None
        if image:
            qimage = get_cached_qimage(image)
            qpixmap = QPixmap.fromImage(qimage)
        if sh_guard:
            with size_hint_guard(self):
                self.widget.setPixmap(qpixmap)
        else:
            self.widget.setPixmap(qpixmap)

    def set_scale_to_fit(self, scale):
        """ Sets whether or not the image scales with the underlying
        control.

        """
        self.widget.setScaledContents(scale)

    def set_allow_upscaling(self, allow):
        """ Sets whether or not the image will scale beyond its natural
        size.

        """
        self.widget.setAllowUpscaling(allow)

    def set_preserve_aspect_ratio(self, preserve):
        """ Sets whether or not to preserve the aspect ratio of the
        image when scaling.

        """
        self.widget.setPreserveAspectRatio(preserve)
