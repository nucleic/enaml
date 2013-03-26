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

from enaml.widgets.spin_box import ProxySpinBox

from .wx_control import WxControl


#: The changed event for the custom spin box
wxSpinBoxEvent, EVT_SPIN_BOX = wx.lib.newevent.NewEvent()


class wxProperSpinBox(wx.SpinCtrl):
    """ A custom wx spin control that acts more like QSpinBox.

    The standard wx.SpinCtrl doesn't support too many features, and
    the ones it does support are (like wrapping) are limited. So,
    this custom control hard codes the internal range to the maximum
    range of the wx.SpinCtrl and implements wrapping manually.

    For changed events, users should bind to EVT_SPIN_BOX rather than
    EVT_SPINCTRL.

    See the method docstrings for supported functionality.

    This control is really a god awful hack and needs to be rewritten
    using a combination wx.SpinButton and wx.TextCtrl.

    """
    def __init__(self, *args, **kwargs):
        """ CustomSpinCtrl constructor.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments for initializing a
            wx.SpinCtrl.

        """
        # The max range of the wx.SpinCtrl is the range of a signed
        # 32bit integer. We don't care about wx's internal value of
        # the control, since we maintain our own internal counter.
        # and because the internal value of the widget gets reset to
        # the minimum of the range whenever SetValueString is called.
        self._hard_min = -(1 << 31)
        self._hard_max = (1 << 31) - 1
        self._internal_value = 0
        self._low = 0
        self._high = 100
        self._step = 1
        self._prefix = u''
        self._suffix = u''
        self._special_value_text = u''
        self._value_string = unicode(self._low)
        self._wrap = False
        self._read_only = False

        # Stores whether spin-up or spin-down was pressed.
        self._spin_state = None

        super(wxProperSpinBox, self).__init__(*args, **kwargs)
        super(wxProperSpinBox, self).SetRange(self._hard_min, self._hard_max)

        # Setting the spin control to process the enter key removes
        # its processing of the Tab key. This is desired for two reasons:
        # 1) It is consistent with the Qt version of the control.
        # 2) The default tab processing is kinda wacky in that when
        #    tab is pressed, it emits a text event with the string
        #    representation of the integer value of the control,
        #    regardless of the value of the user supplied string.
        #    This is definitely not correct and so processing on
        #    Enter allows us to avoid the issue entirely.
        self.WindowStyle |= wx.TE_PROCESS_ENTER

        self.Bind(wx.EVT_SPIN_UP, self.OnSpinUp)
        self.Bind(wx.EVT_SPIN_DOWN, self.OnSpinDown)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpinCtrl)
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnterPressed)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnEnterPressed(self, event):
        """ The event handler for an enter key press. It forces an
        interpretation of the current text control value.

        """
        self.InterpretText()

    def OnKillFocus(self, event):
        """ Handles evaluating the text in the control when the control
        loses focus.

        """
        # The spin control doesn't emit a spin event when losing focus
        # to process typed input change unless it results in a different
        # value, so we have to handle it manually and update the control
        # again after the event. It must be invoked on a CallAfter or it
        # doesn't work properly. The lambda avoids a DeadObjectError if
        # the app is exited before the callback executes.
        wx.CallAfter(lambda: self.InterpretText() if self else None)

    def OnText(self, event):
        """ Handles the text event of the spin control to store away the
        user typed text for later conversion.

        """
        if self._read_only:
            return
        # Do not be tempted to try to implement the 'tracking' feature
        # by adding logic to this method. Wx emits this event at weird
        # times such as ctrl-a select all as well as when SetValueString
        # is called. Granted, this can be avoided with a recursion guard,
        # however, there is no way to get/set the caret position on the
        # control and every call to SetValueString resets the caret
        # position to Zero. So, there is really no possible way to
        # implement 'tracking' without creating an entirely new custom
        # control. So for now, the wx backend just lacks that feature.
        self._value_string = event.GetString()

    def OnSpinUp(self, event):
        """ The event handler for the spin up event. We veto the spin
        event to prevent the control from changing it's internal value.
        Instead, we maintain complete control of the value.

        """
        event.Veto()
        if self._read_only:
            return
        self._spin_state = 'up'
        self.OnSpinCtrl(event)
        self._spin_state = None

    def OnSpinDown(self, event):
        """ The event handler for the spin down event. We veto the spin
        event to prevent the control from changing it's internal value.
        Instead, we maintain complete control of the value.

        """
        event.Veto()
        if self._read_only:
            return
        self._spin_state = 'down'
        self.OnSpinCtrl(event)
        self._spin_state = None

    def OnSpinCtrl(self, event):
        """ Handles the spin control being changed by user interaction.
        All of the manual stepping and wrapping logic is computed by
        this method.

        """
        if self._read_only:
            return
        last = self._internal_value
        low = self._low
        high = self._high
        step = self._step
        wrap = self._wrap
        spin_state = self._spin_state
        if spin_state == 'down':
            if last == low:
                if wrap:
                    computed = high
                else:
                    computed = low
            else:
                computed = last - step
                if computed < low:
                    computed = low
            self.SetValue(computed)
        elif spin_state == 'up':
            if last == high:
                if wrap:
                    computed = low
                else:
                    computed = high
            else:
                computed = last + step
                if computed > high:
                    computed = high
            self.SetValue(computed)
        else:
            # A suprious spin event generated by wx when the widget loses
            # focus. We can safetly ignore it.
            pass

    #--------------------------------------------------------------------------
    # Getters/Setters
    #--------------------------------------------------------------------------
    def GetLow(self):
        """ Returns the minimum value of the control.

        """
        return self._low

    def GetMin(self):
        """ Equivalent to GetLow().

        """
        return self._low

    def SetLow(self, low):
        """ Sets the minimum value of the control and changes the
        value to the min if the current value would be out of range.

        """
        if low < self._hard_min:
            raise ValueError('%s is too low for wxProperSpinBox.' % low)
        self._low = low
        if self.GetValue() < low:
            self.SetValue(low)

    def GetHigh(self):
        """ Returns the maximum value of the control.

        """
        return self._high

    def GetMax(self):
        """ Equivalent to GetHigh().

        """
        return self._high

    def SetHigh(self, high):
        """ Sets the maximum value of the control and changes the
        value to the max if the current value would be out of range.

        """
        if high > self._hard_max:
            raise ValueError('%s is too high for wxProperSpinBox.' % high)
        self._high = high
        if self.GetValue() > high:
            self.SetValue(high)

    def SetRange(self, low, high):
        """ Sets the low and high values of the control.

        """
        self.SetLow(low)
        self.SetHigh(high)

    def GetStep(self):
        """ Returns the step size of the control.

        """
        return self._step

    def SetStep(self, step):
        """ Sets the step size of the control.

        """
        self._step = step

    def GetWrap(self):
        """ Gets the wrap flag of the control.

        """
        return self._wrap

    def SetWrap(self, wrap):
        """ Sets the wrap flag of the control.

        """
        self._wrap = wrap

    def GetPrefix(self):
        """ Get the prefix text for the control.

        Returns
        -------
        result : unicode
            The unicode prefix text.

        """
        return self._prefix

    def SetPrefix(self, prefix):
        """ Set the prefix text for the control.

        Parameters
        ----------
        prefix : unicode
            The unicode prefix text for the control.

        """
        self._prefix = prefix

    def GetSuffix(self):
        """ Get the suffix text for the control.

        Returns
        -------
        result : unicode
            The unicode suffix text.

        """
        return self._suffix

    def SetSuffix(self, suffix):
        """ Set the suffix text for the control.

        Parameters
        ----------
        suffix : unicode
            The unicode suffix text for the control.

        """
        self._suffix = suffix

    def GetSpecialValueText(self):
        """ Returns the special value text for the spin box.

        Returns
        -------
        result : unicode
            The unicode special value text.

        """
        return self._special_value_text

    def SetSpecialValueText(self, text):
        """ Set the special value text for the control.

        Parameters
        ----------
        text : unicode
            The unicode special value text for the control.

        """
        self._special_value_text = text

    def GetReadOnly(self):
        """ Get the read only flag for the control.

        Returns
        -------
        result : bool
            True if the control is read only, False otherwise.

        """
        return self._suffix

    def SetReadOnly(self, read_only):
        """ Set the read only flag for the control

        Parameters
        ----------
        read_only : bool
            True if the control should be read only, False otherwise.

        """
        self._read_only = read_only

    def GetValue(self):
        """ Returns the internal integer value of the control.

        """
        return self._internal_value

    def SetValue(self, value):
        """ Sets the value of the control to the given value, provided
        that the value is within the range of the control. If the
        given value is within range, and is different from the current
        value of the control, an EVT_SPIN_BOX will be emitted.

        """
        different = False
        if self._low <= value <= self._high:
            different = (self._internal_value != value)
            self._internal_value = value

        # Always set the value string, just to be overly
        # safe that we don't fall out of sync.
        self._value_string = self.TextFromValue(self._internal_value)
        self.SetValueString(self._value_string)

        if different:
            evt = wxSpinBoxEvent()
            wx.PostEvent(self, evt)

    #--------------------------------------------------------------------------
    # Support Methods
    #--------------------------------------------------------------------------
    def InterpretText(self):
        """ Interprets the user supplied text and updates the control.

        """
        prefix = self._prefix
        suffix = self._suffix
        svt = self._special_value_text
        text = self._value_string
        if svt and text == svt:
            self.SetValue(self._low)
            return
        if prefix and text.startswith(prefix):
            text = text[len(prefix):]
        if suffix and text.endswith(suffix):
            text = text[:-len(suffix)]
        try:
            value = int(text)
        except ValueError:
            value = self._internal_value
        self.SetValue(value)

    def TextFromValue(self, value):
        """ Converts the given integer to a string for display.

        """
        prefix = self._prefix
        suffix = self._suffix
        svt = self._special_value_text
        if value == self._low and svt:
            return svt
        text = unicode(value)
        if prefix:
            text = '%s%s' % (prefix, text)
        if suffix:
            text = '%s%s' % (text, suffix)
        return text


#: Cyclic guard flag
VALUE_FLAG = 0x1


class WxSpinBox(WxControl, ProxySpinBox):
    """ A Wx implementation of an Enaml ProxySpinBox.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxProperSpinBox)

    #: Cyclic guard flags
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying wxProperSpinBox widget.

        """
        self.widget = wxProperSpinBox(self.parent_widget())

    def init_widget(self, ):
        """ Create and initialize the slider control.

        """
        super(WxSpinBox, self).init_widget()
        d = self.declaration
        self.set_maximum(d.maximum)
        self.set_minimum(d.minimum)
        self.set_value(d.value)
        self.set_prefix(d.prefix)
        self.set_suffix(d.suffix)
        self.set_special_value_text(d.special_value_text)
        self.set_single_step(d.single_step)
        self.set_read_only(d.read_only)
        self.set_wrapping(d.wrapping)
        self.widget.Bind(EVT_SPIN_BOX, self.on_value_changed)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_value_changed(self, event):
        """ The event handler for the 'EVT_SPIN_BOX' event.

        """
        if not self._guard & VALUE_FLAG:
            self._guard |= VALUE_FLAG
            try:
                self.declaration.value = self.widget.GetValue()
            finally:
                self._guard &= ~VALUE_FLAG

    #--------------------------------------------------------------------------
    # ProxySpinBox API
    #--------------------------------------------------------------------------
    def set_maximum(self, maximum):
        """ Set the widget's maximum value.

        """
        self.widget.SetHigh(maximum)

    def set_minimum(self, minimum):
        """ Set the widget's minimum value.

        """
        self.widget.SetLow(minimum)

    def set_value(self, value):
        """ Set the spin box's value.

        """
        if not self._guard & VALUE_FLAG:
            self._guard |= VALUE_FLAG
            try:
                self.widget.SetValue(value)
            finally:
                self._guard &= ~VALUE_FLAG


    def set_prefix(self, prefix):
        """ Set the prefix for the spin box.

        """
        self.widget.SetPrefix(prefix)

    def set_suffix(self, suffix):
        """ Set the suffix for the spin box.

        """
        self.widget.SetSuffix(suffix)

    def set_special_value_text(self, text):
        """ Set the special value text for the spin box.

        """
        self.widget.SetSpecialValueText(text)

    def set_single_step(self, step):
        """ Set the widget's single step value.

        """
        self.widget.SetStep(step)

    def set_read_only(self, read_only):
        """ Set the widget's read only flag.

        """
        self.widget.SetReadOnly(read_only)

    def set_wrapping(self, wrapping):
        """ Set the widget's wrapping flag.

        """
        self.widget.SetWrap(wrapping)
