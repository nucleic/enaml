#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from atom.api import Int, Typed

from enaml.widgets.slider import ProxySlider

from .wx_control import WxControl


#: Horizontal tick mapping
_TICK_POSITION_MAP = {
    'top': wx.SL_TOP | wx.SL_AUTOTICKS,
    'bottom': wx.SL_BOTTOM | wx.SL_AUTOTICKS,
    'left': wx.SL_LEFT | wx.SL_AUTOTICKS,
    'right': wx.SL_RIGHT | wx.SL_AUTOTICKS,
    'both': wx.SL_BOTH | wx.SL_AUTOTICKS,
}


#: An OR'd combination of all the tick flags.
_TICK_MASK = (
    wx.SL_TOP | wx.SL_BOTTOM | wx.SL_LEFT | wx.SL_RIGHT | wx.SL_BOTH |
    wx.SL_AUTOTICKS
)


#: A map adapting orientation to tick positions
_TICK_ADAPT_MAP = {
    'vertical': {
        'left': 'left',
        'right': 'right',
        'both': 'both',
        'top': 'left',
        'bottom': 'right',
    },
    'horizontal': {
        'left': 'top',
        'right': 'bottom',
        'both': 'both',
        'top': 'top',
        'bottom': 'bottom',
    },
}


#: A map from string orientation to wx slider orientation
_ORIENTATION_MAP = {
    'horizontal': wx.SL_HORIZONTAL,
    'vertical': wx.SL_VERTICAL,
}


#: An OR'd combination of all the orientation flags
_ORIENTATION_MASK = wx.SL_HORIZONTAL | wx.SL_VERTICAL


#: A new event emitted by the custom slider control
wxSliderEvent, EVT_SLIDER = wx.lib.newevent.NewEvent()


class wxProperSlider(wx.Slider):
    """ A wx.Slider subclass which supports tracking.

    """
    #: The event types for the frequent thumb track event
    _tracking_evt = wx.EVT_SCROLL_THUMBTRACK.evtType[0]

    #: The event type for the thumb release event.
    _release_evt = wx.EVT_SCROLL_THUMBRELEASE.evtType[0]

    #: The event type for the scroll end event.
    _end_evt = wx.EVT_SCROLL_CHANGED.evtType[0]

    def __init__(self, *args, **kwargs):
        """ Initialize a wxProperSlider.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments for initializing a
            wx.Slider.

        """
        super(wxProperSlider, self).__init__(*args, **kwargs)
        self._tracking = True
        self.Bind(wx.EVT_SCROLL, self.OnScroll)

    def OnScroll(self, event):
        """ An event handler which handles all scroll events.

        This handler determines whether or not a slider event sould be
        emitted for the scroll changed, based on whether tracking is
        enabled for the slider.

        """
        evt_type = event.EventType

        # We never emit on the _end_event since that is windows-only
        if evt_type == self._end_evt:
            return

        if self._tracking:
            if evt_type != self._release_evt:
                emit = True
            else:
                emit = False
        else:
            emit = evt_type != self._tracking_evt

        if emit:
            evt = wxSliderEvent()
            wx.PostEvent(self, evt)

    def GetTracking(self):
        """ Whether or not tracking is enabled for the slider.

        Returns
        -------
        result : bool
            True if tracking is enabled for the slider, False otherwise.

        """
        return self._tracking

    def SetTracking(self, tracking):
        """ Set whether tracking is enabled for the slider.

        Parameters
        ----------
        tracking : bool
            True if tracking should be enabled, False otherwise.

        """
        self._tracking = tracking


#: A cyclic guard flag
VALUE_FLAG = 0x1


class WxSlider(WxControl, ProxySlider):
    """ A Wx implementation of an Enaml ProxySlider.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxProperSlider)

    #: Cyclic notification guard flags.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying wxProperSlider widget.

        """
        self.widget = wxProperSlider(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        # NOTE: The tick interval must be set *after* the tick position
        # or Wx will ignore the tick interval. grrr...
        super(WxSlider, self).init_widget()
        d = self.declaration
        self.set_minimum(d.minimum)
        self.set_maximum(d.maximum)
        self.set_value(d.value)
        self.set_orientation(d.orientation)
        self.set_page_step(d.page_step)
        self.set_single_step(d.single_step)
        self.set_tick_position(d.tick_position)
        self.set_tick_interval(d.tick_interval)
        self.set_tracking(d.tracking)
        self.widget.Bind(EVT_SLIDER, self.on_value_changed)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_value_changed(self, event):
        """ Send the 'value_changed' action to the Enaml widget when the
        slider value has changed.

        """
        if not self._guard & VALUE_FLAG:
            self._guard |= VALUE_FLAG
            try:
                self.declaration.value = self.widget.GetValue()
            finally:
                self._guard &= ~VALUE_FLAG

    #--------------------------------------------------------------------------
    # ProxySlider API
    #--------------------------------------------------------------------------
    def set_value(self, value):
        """ Set the value of the underlying widget.

        """
        if not self._guard & VALUE_FLAG:
            self._guard |= VALUE_FLAG
            try:
                self.widget.SetValue(value)
            finally:
                self._guard &= ~VALUE_FLAG

    def set_maximum(self, maximum):
        """ Set the maximum value of the underlying widget.

        """
        widget = self.widget
        minimum, _ = widget.GetRange()
        widget.SetRange(minimum, maximum)

    def set_minimum(self, minimum):
        """ Set the minimum value of the underlying widget.

        """
        widget = self.widget
        _, maximum = widget.GetRange()
        widget.SetRange(minimum, maximum)

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        widget = self.widget
        style = widget.GetWindowStyle()
        style &= ~_ORIENTATION_MASK
        style |= _ORIENTATION_MAP[orientation]
        widget.SetWindowStyle(style)

    def set_page_step(self, page_step):
        """ Set the page step of the underlying widget.

        """
        self.widget.SetPageSize(page_step)

    def set_single_step(self, single_step):
        """ Set the single step of the underlying widget.

        """
        self.widget.SetLineSize(single_step)

    def set_tick_interval(self, interval):
        """ Set the tick interval of the underlying widget.

        """
        self.widget.SetTickFreq(interval)

    def set_tick_position(self, tick_position):
        """ Set the tick position of the underlying widget.

        """
        widget = self.widget
        style = widget.GetWindowStyle()
        style &= ~_TICK_MASK
        if tick_position != 'no_ticks':
            if style & wx.SL_VERTICAL:
                tick_position = _TICK_ADAPT_MAP['vertical'][tick_position]
            else:
                tick_position = _TICK_ADAPT_MAP['horizontal'][tick_position]
            style |= _TICK_POSITION_MAP[tick_position]
        widget.SetWindowStyle(style)

    def set_tracking(self, tracking):
        """ Set the tracking of the underlying widget.

        """
        self.widget.SetTracking(tracking)
