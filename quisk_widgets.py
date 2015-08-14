# These are Quisk widgets

import sys, re
import wx, wx.lib.buttons, wx.lib.stattext
from types import *
# The main script will alter quisk_conf_defaults to include the user's config file.
import quisk_conf_defaults as conf
import _quisk as QS

def FreqFormatter(freq):	# Format the string or integer frequency by adding blanks
  freq = int(freq)
  if freq >= 0:
    t = str(freq)
    minus = ''
  else:
    t = str(-freq)
    minus = '- '
  l = len(t)
  if l > 9:
    txt = "%s%s %s %s %s" % (minus, t[0:-9], t[-9:-6], t[-6:-3], t[-3:])
  elif l > 6:
    txt = "%s%s %s %s" % (minus, t[0:-6], t[-6:-3], t[-3:])
  elif l > 3:
    txt = "%s%s %s" % (minus, t[0:-3], t[-3:])
  else:
    txt = minus + t
  return txt

class FrequencyDisplay(wx.lib.stattext.GenStaticText):
  """Create a frequency display widget."""
  def __init__(self, frame, width, height):
    wx.lib.stattext.GenStaticText.__init__(self, frame, -1, '3',
         style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
    border = 4
    for points in range(30, 6, -1):
      font = wx.Font(points, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL, face=conf.quisk_typeface)
      self.SetFont(font)
      w, h = self.GetTextExtent('333 444 555 Hz')
      if w < width and h < height - border * 2:
        break
    self.SetSizeHints(w, h, w * 5, h)
    self.height = h
    self.points = points
    border = self.border = (height - self.height) // 2
    self.height_and_border = h + border * 2
    self.SetBackgroundColour(conf.color_freq)
    self.SetForegroundColour(conf.color_freq_txt)
    self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)	# Click on a digit changes the frequency
    self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDown)
    self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
    self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheel)
    if sys.platform == 'win32':
      self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
    self.timer = wx.Timer(self)                     # Holding a digit continuously changes the frequency
    self.Bind(wx.EVT_TIMER, self.OnTimer)
    self.repeat_time = 0                           # Repeat function is inactive
  def OnEnter(self, event):
    if not application.w_phase:
      self.SetFocus()	# Set focus so we get mouse wheel events
  def Clip(self, clip):
    """Change color to indicate clipping."""
    if clip:
      self.SetBackgroundColour('deep pink')
    else:
      self.SetBackgroundColour(conf.color_freq)
    self.Refresh()
  def Display(self, freq):
    """Set the frequency to be displayed."""
    txt = FreqFormatter(freq)
    self.SetLabel('%s Hz' % txt)
  def GetIndex(self, event):		# Determine which digit is being changed
    mouse_x, mouse_y = event.GetPosition()
    width, height = self.GetClientSizeTuple()
    text = self.GetLabel()
    tw, th = self.GetTextExtent(text)
    edge = (width - tw) / 2
    digit = self.GetTextExtent('0')[0]
    blank = self.GetTextExtent(' ')[0]
    if mouse_x < edge - digit:
      return None
    x = width - edge - self.GetTextExtent(" Hz")[0] - mouse_x
    if x < 0:
      return None
    #print ('size', width, height, 'mouse', mouse_x, mouse_y, 'digit', digit, 'blank', blank)
    shift = 0
    while x > digit * 3:
      shift += 1
      x -= digit * 3 + blank
    if x < 0:
      return None
    return x / digit + shift * 3	# index of digit being changed
  def OnLeftDown(self, event):		# Click on a digit changes the frequency
    if self.repeat_time:
      self.timer.Stop()
      self.repeat_time = 0
    index = self.GetIndex(event)
    if index is not None:
      self.index = index
      mouse_x, mouse_y = event.GetPosition()
      width, height = self.GetClientSizeTuple()
      if mouse_y < height / 2:
        self.increase = True
      else:
        self.increase = False
      self.ChangeFreq()
      self.repeat_time = 300		# first button push
      self.timer.Start(milliseconds=300, oneShot=True)
  def OnLeftUp(self, event):
    self.timer.Stop()
    self.repeat_time = 0
  def ChangeFreq(self):
    text = self.GetLabel()
    text = text.replace(' ', '')[:-2]
    text = text[:len(text)-self.index] + '0' * self.index
    if self.increase:
      freq = int(text) + 10 ** self.index
    else:
      freq = int(text) - 10 ** self.index
      if freq <= 0 and self.index > 0:
        freq = 10 ** (self.index - 1)
    #print ('X', x, 'N', n, text, 'freq', freq)
    application.ChangeRxTxFrequency(None, freq)
  def OnTimer(self, event):
    if self.repeat_time == 300:     # after first push, turn on repeats
      self.repeat_time = 150
    elif self.repeat_time > 20:
      self.repeat_time -= 5
    self.ChangeFreq()
    self.timer.Start(milliseconds=self.repeat_time, oneShot=True)
  def OnWheel(self, event):
    index = self.GetIndex(event)
    if index is not None:
      self.index = index
      if event.GetWheelRotation() > 0:
        self.increase = True
      else:
        self.increase = False
      self.ChangeFreq()

class SliderBoxH:
  """A horizontal control with a slider and text with a value.  The text must have a %d or %f if display is True."""
  def __init__(self, parent, text, init, themin, themax, handler, display, pos, width, scale=1):
    self.text = text
    self.handler = handler
    self.display = display
    self.scale = scale
    if display:		# Display the slider value
      t1 = self.text % (themin * scale)
      t2 = self.text % (themax * scale)
      if len(t1) > len(t2):		# set text size to the largest
        t = t1
      else:
        t = t2
    else:
      t = self.text
    if pos is None:
      self.text_ctrl = wx.StaticText(parent, -1, t, style=wx.ST_NO_AUTORESIZE)
      w2, h2 = self.text_ctrl.GetSize()
      self.text_ctrl.SetSizeHints(w2, -1, w2)
      self.slider = wx.Slider(parent, -1, init, themin, themax)
    else:
      self.text_ctrl = wx.StaticText(parent, -1, t, pos=pos)
      w2, h2 = self.text_ctrl.GetSize()
      self.slider = wx.Slider(parent, -1, init, themin, themax, (pos[0] + w2, pos[1]), (width - w2, h2))
    self.slider.Bind(wx.EVT_SCROLL, self.OnScroll)
    self.text_ctrl.SetForegroundColour(parent.GetForegroundColour())
    self.OnScroll()
  def OnScroll(self, event=None):
    if event:
      event.Skip()
      if self.handler:
        self.handler(event)
    if self.display:
      t = self.text % (self.slider.GetValue() * self.scale)
    else:
      t = self.text
    self.text_ctrl.SetLabel(t)
  def GetValue(self):
    return self.slider.GetValue()
  def SetValue(self, value):
    # Set slider visual position; does not call handler
    self.slider.SetValue(value)
    self.OnScroll()

class SliderBoxHH(SliderBoxH, wx.BoxSizer):
  """A horizontal control with a slider and text with a value.  The text must have a %d if display is True."""
  def __init__(self, parent, text, init, themin, themax, handler, display):
    wx.BoxSizer.__init__(self, wx.HORIZONTAL)
    SliderBoxH.__init__(self, parent, text, init, themin, themax, handler, display, None, None)
    #font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL, face=conf.quisk_typeface)
    #self.text_ctrl.SetFont(font)
    self.Add(self.text_ctrl, 0, wx.ALIGN_CENTER)
    self.Add(self.slider, 1, wx.ALIGN_CENTER)

class SliderBoxV(wx.BoxSizer):
  """A vertical box containing a slider and a text heading"""
  # Note: A vertical wx slider has the max value at the bottom.  This is
  # reversed for this control.
  def __init__(self, parent, text, init, themax, handler, display=False):
    wx.BoxSizer.__init__(self, wx.VERTICAL)
    self.slider = wx.Slider(parent, -1, init, 0, themax, style=wx.SL_VERTICAL)
    self.slider.Bind(wx.EVT_SCROLL, handler)
    sw, sh = self.slider.GetSize()
    self.text = text
    self.themax = themax
    if display:		# Display the slider value when it is thumb'd
      self.text_ctrl = wx.StaticText(parent, -1, str(themax), style=wx.ALIGN_CENTER)
      w1, h1 = self.text_ctrl.GetSize()	# Measure size with max number
      self.text_ctrl.SetLabel(text)
      w2, h2 = self.text_ctrl.GetSize()	# Measure size with text
      self.width = max(w1, w2, sw)
      self.text_ctrl.SetSizeHints(self.width, -1, self.width)
      self.slider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.Change)
      self.slider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.ChangeDone)
    else:
      self.text_ctrl = wx.StaticText(parent, -1, text)
      w2, h2 = self.text_ctrl.GetSize()	# Measure size with text
      self.width = max(w2, sw)
    self.text_ctrl.SetForegroundColour(parent.GetForegroundColour())
    self.Add(self.text_ctrl, 0, wx.ALIGN_CENTER)
    self.Add(self.slider, 1, wx.ALIGN_CENTER)
  def Change(self, event):
    event.Skip()
    self.text_ctrl.SetLabel(str(self.themax - self.slider.GetValue()))
  def ChangeDone(self, event):
    event.Skip()
    self.text_ctrl.SetLabel(self.text)
  def GetValue(self):
    return self.themax - self.slider.GetValue()
  def SetValue(self, value):
    # Set slider visual position; does not call handler
    self.slider.SetValue(self.themax - value)

class _QuiskText1(wx.lib.stattext.GenStaticText):
  # Self-drawn text for QuiskText.
  def __init__(self, parent, size_text, height, style, fixed):
    wx.lib.stattext.GenStaticText.__init__(self, parent, -1, '',
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.ST_NO_AUTORESIZE|style,
                 name = "QuiskText1")
    self.fixed = fixed
    self.size_text = size_text
    self.pen = wx.Pen(conf.color_btn, 2)
    self.brush = wx.Brush(conf.color_freq)
    self.SetForegroundColour(conf.color_freq_txt)
    self.SetSizeHints(-1, height, -1, height)
  def _MeasureFont(self, dc, width, height):
    # Set decreasing point size until size_text fits in the space available
    for points in range(20, 6, -1):
      if self.fixed:
        font = wx.Font(points, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.FONTWEIGHT_NORMAL, face=conf.quisk_typeface)
      else:
        font = wx.Font(points, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL, face=conf.quisk_typeface)
      dc.SetFont(font)
      w, h = dc.GetTextExtent(self.size_text)
      if w < width and h < height:
        break
    self.size_text = ''
    self.SetFont(font)
  def OnPaint(self, event):
    dc = wx.PaintDC(self)
    width, height = self.GetClientSize()
    if not width or not height:
      return
    dc.SetPen(self.pen)
    dc.SetBrush(self.brush)
    dc.DrawRectangle(1, 1, width-1, height-1)
    label = self.GetLabel()
    if not label:
      return
    if self.size_text:
      self._MeasureFont(dc, width-2, height-2)
    else:
      dc.SetFont(self.GetFont())
    if self.IsEnabled():
      dc.SetTextForeground(self.GetForegroundColour())
    else:
      dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
    style = self.GetWindowStyleFlag()
    w, h = dc.GetTextExtent(label)
    y = (height - h) // 2
    if y < 0:
      y = 0
    if style & wx.ALIGN_RIGHT:
      x = width - w - 4
    elif style & wx.ALIGN_CENTER:
      x = (width - w - 1)/2
    else:
      x = 3
    dc.DrawText(label, x, y)

class QuiskText(wx.BoxSizer):
  # A one-line text display left/right/center justified and vertically centered.
  # The height of the control is fixed as "height".  The width is expanded.
  # The font is chosen so size_text fits in the client area.
  def __init__(self, parent, size_text, height, style=0, fixed=False):
    wx.BoxSizer.__init__(self, wx.HORIZONTAL)
    self.TextCtrl = _QuiskText1(parent, size_text, height, style, fixed)
    self.Add(self.TextCtrl, 1, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
  def SetLabel(self, label):
    self.TextCtrl.SetLabel(label)

# Start of our button classes.  They are compatible with wxPython GenButton
# buttons.  Use the usual methods for access:
# GetLabel(self), SetLabel(self, label):	Get and set the label
# Enable(self, flag), Disable(self), IsEnabled(self):	Enable / Disable
# GetValue(self), SetValue(self, value):	Get / Set check button state True / False
# SetIndex(self, index):	For cycle buttons, set the label from its index

class QuiskButtons:
  """Base class for special buttons."""
  button_bezel = 3		# size of button bezel in pixels
  def InitButtons(self, text):
    self.SetBezelWidth(self.button_bezel)
    self.SetBackgroundColour(conf.color_btn)
    self.SetUseFocusIndicator(False)
    self.font = wx.Font(conf.button_font_size, wx.FONTFAMILY_SWISS, wx.NORMAL,
             wx.FONTWEIGHT_NORMAL, face=conf.quisk_typeface)
    self.SetFont(self.font)
    if text:
      w, h = self.GetTextExtent(text)
    else:
      w, h = self.GetTextExtent("OK")
      self.Disable()	# create a size for null text, but Disable()
    w += self.button_bezel * 2 + self.GetCharWidth()
    h = h * 12 // 10
    h += self.button_bezel * 2
    self.SetSizeHints(w, h, w * 6, h, 1, 1)
  def DrawLabel(self, dc, width, height, dx=0, dy=0):	# Override to change Disable text color
      dc.SetFont(self.GetFont())
      label = self.GetLabel()
      tw, th = dc.GetTextExtent(label)
      dx = dy = self.labelDelta
      slabel = re.split('('+unichr(0x25CF)+')', label)	# unicode symbol for record: a filled dot
      for part in slabel:		# This code makes the symbol red.  Thanks to Christof, DJ4CM.
        if self.IsEnabled():
          if part == unichr(0x25CF):
            dc.SetTextForeground('red')
          else:
            dc.SetTextForeground(conf.color_enable)
        else:
          dc.SetTextForeground(conf.color_disable)
        dc.DrawText(part, (width-tw)//2+dx, (height-th)//2+dy)
        dx += dc.GetTextExtent(part)[0]
  def OnKeyDown(self, event):
    pass
  def OnKeyUp(self, event):
    pass

class QuiskPushbutton(QuiskButtons, wx.lib.buttons.GenButton):
  """A plain push button widget."""
  def __init__(self, parent, command, text, use_right=False):
    wx.lib.buttons.GenButton.__init__(self, parent, -1, text)
    self.command = command
    self.Bind(wx.EVT_BUTTON, self.OnButton)
    self.InitButtons(text)
    self.direction = 1
    if use_right:
      self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
      self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
  def OnButton(self, event):
    if self.command:
      self.command(event)
  def OnRightDown(self, event):
    self.direction = -1
    self.OnLeftDown(event) 
  def OnRightUp(self, event):
    self.OnLeftUp(event)
    self.direction = 1
      

class QuiskRepeatbutton(QuiskButtons, wx.lib.buttons.GenButton):
  """A push button that repeats when held down."""
  def __init__(self, parent, command, text, up_command=None, use_right=False):
    wx.lib.buttons.GenButton.__init__(self, parent, -1, text)
    self.command = command
    self.up_command = up_command
    self.timer = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self.OnTimer)
    self.Bind(wx.EVT_BUTTON, self.OnButton)
    self.InitButtons(text)
    self.repeat_state = 0		# repeater button inactive
    self.direction = 1
    if use_right:
      self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
      self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
  def SendCommand(self, command):
    if command:
      event = wx.PyEvent()
      event.SetEventObject(self)
      command(event)
  def OnLeftDown(self, event):
    if self.IsEnabled():
      self.shift = event.ShiftDown()
      self.control = event.ControlDown()
      self.SendCommand(self.command)
      self.repeat_state = 1		# first button push
      self.timer.Start(milliseconds=300, oneShot=True)
    wx.lib.buttons.GenButton.OnLeftDown(self, event)
  def OnLeftUp(self, event):
    if self.IsEnabled():
      self.SendCommand(self.up_command)
      self.repeat_state = 0
      self.timer.Stop()
    wx.lib.buttons.GenButton.OnLeftUp(self, event)
  def OnRightDown(self, event):
    if self.IsEnabled():
      self.shift = event.ShiftDown()
      self.control = event.ControlDown()
      self.direction = -1
      self.OnLeftDown(event) 
  def OnRightUp(self, event):
    if self.IsEnabled():
      self.OnLeftUp(event)
      self.direction = 1
  def OnTimer(self, event):
    if self.repeat_state == 1:	# after first push, turn on repeats
      self.timer.Start(milliseconds=150, oneShot=False)
      self.repeat_state = 2
    if self.repeat_state:		# send commands until button is released
      self.SendCommand(self.command)
  def OnButton(self, event):
    pass	# button command not used

class QuiskCheckbutton(QuiskButtons, wx.lib.buttons.GenToggleButton):
  """A button that pops up and down, and changes color with each push."""
  # Check button; get the checked state with self.GetValue()
  def __init__(self, parent, command, text, color=None, use_right=False):
    wx.lib.buttons.GenToggleButton.__init__(self, parent, -1, text)
    self.InitButtons(text)
    self.Bind(wx.EVT_BUTTON, self.OnButton)
    self.button_down = 0		# used for radio buttons
    self.command = command
    if color is None:
      self.color = conf.color_check_btn
    else:
      self.color = color
    self.direction = 1
    if use_right:
      self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
      self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
  def SetValue(self, value, do_cmd=False):
    wx.lib.buttons.GenToggleButton.SetValue(self, value)
    self.button_down = value
    if value:
      self.SetBackgroundColour(self.color)
    else:
      self.SetBackgroundColour(conf.color_btn)
    if do_cmd and self.command:
      event = wx.PyEvent()
      event.SetEventObject(self)
      self.command(event)
  def OnButton(self, event):
    if self.GetValue():
      self.SetBackgroundColour(self.color)
    else:
      self.SetBackgroundColour(conf.color_btn)
    if self.command:
      self.command(event)
  def OnRightDown(self, event):
    self.direction = -1
    self.OnLeftDown(event) 
  def OnRightUp(self, event):
    self.OnLeftUp(event)
    self.direction = 1

class QFilterButtonWindow(wx.Frame):
  """Create a window with controls for the button"""
  def __init__(self, button):
    self.button = button
    l = self.valuelist = []
    value = 10
    incr = 10
    for i in range(0, 101):
      l.append(value)
      value += incr
      if value == 100:
        incr = 20
      elif value == 500:
        incr = 50
      elif value == 1000:
        incr = 100
      elif value == 5000:
        incr = 500
      elif value == 10000:
        incr = 1000
    x, y = button.GetPositionTuple()
    x, y = button.GetParent().ClientToScreenXY(x, y)
    w, h = button.GetSize()
    height = h * 10
    size = (w, height)
    if sys.platform == 'win32':
      pos = (x, y - height)
      t = 'Filter'
    else:
      pos = (x, y - height - h)
      t = ''
    wx.Frame.__init__(self, button.GetParent(), -1, t, pos, size,
      wx.FRAME_TOOL_WINDOW|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX|wx.CAPTION|wx.SYSTEM_MENU)
    self.SetBackgroundColour(conf.color_freq)
    self.Bind(wx.EVT_CLOSE, self.OnClose)
    value = int(button.GetLabel())
    try:
      index = 100 - self.valuelist.index(value)
    except ValueError:
      index = 0
    self.slider = wx.Slider(self, -1, index, 0, 100, (0, 0), (w/2, height), wx.SL_VERTICAL)
    self.slider.Bind(wx.EVT_SCROLL, self.OnSlider)
    self.Show()
    self.slider.SetFocus()
  def OnSlider(self, event):
    value = self.slider.GetValue()
    value = 100 - value
    value = self.valuelist[value]
    self.button.SetLabel(str(value))
    self.button.Refresh()
    self.button.SetValue(True, True)
    application.filterAdjBw1 = value
  def OnClose(self, event):
    self.button.adjust = None
    self.Destroy()

class QuiskFilterButton(QuiskCheckbutton):
  """An adjustable check button for filter width; right-click to adjust."""
  def __init__(self, parent, command=None, text='', color=None):
    if color is None:
      color = conf.color_adjust_btn
    QuiskCheckbutton.__init__(self, parent, command, text, color)
    self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
    self.adjust = None
  def OnRightDown(self, event):
    self.OnButton(event)
    if self.adjust:
      self.adjust.Destroy()
      self.adjust = None
    else:
      self.adjust = QFilterButtonWindow(self)

class QSliderButtonWindow(wx.Frame):
  """Create a window with controls for the button"""
  def __init__(self, button, value):
    self.button = button
    x, y = button.GetPositionTuple()
    x, y = button.GetParent().ClientToScreenXY(x, y)
    w, h = button.GetSize()
    height = h * 10
    size = (w, height)
    if sys.platform == 'win32':
      pos = (x, y - height)
    else:
      pos = (x, y - height - h)
    wx.Frame.__init__(self, button.GetParent(), -1, '', pos, size,
      wx.FRAME_TOOL_WINDOW|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX|wx.CAPTION|wx.SYSTEM_MENU)
    self.SetBackgroundColour(conf.color_freq)
    self.Bind(wx.EVT_CLOSE, self.OnClose)
    self.slider = wx.Slider(self, -1, value,
             self.button.slider_min, self.button.slider_max,
             (0, 0), (w/2, height), wx.SL_VERTICAL)
    self.slider.Bind(wx.EVT_SCROLL, self.button.OnSlider)
    self.Show()
    self.slider.SetFocus()
  def OnClose(self, event):
    self.button.adjust = None
    self.Destroy()

class QuiskSliderButton(QuiskCheckbutton):
  """An adjustable check button; right-click to adjust."""
  def __init__(self, parent, command=None, text='', color=None, slider_value=0,
        slider_min=0, slider_max=1000, display=False):
    if color is None:
      color = conf.color_adjust_btn
    self.text = text
    self.dual = False						# separate values for button up or down
    self.display = display					# Display the value at the top
    self.slider_value = slider_value		# value for not dual
    self.slider_value_off = slider_value	# value for dual and button up
    self.slider_value_on = slider_value		# value for dual and button down
    self.slider_min = slider_min
    self.slider_max = slider_max
    QuiskCheckbutton.__init__(self, parent, command, text, color)
    self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
    self.adjust = None
  def SetDual(self, dual):		# dual means separate slider values for on and off
    self.dual = dual
    if self.adjust:
      self.adjust.Destroy()
      self.adjust = None
  def OnRightDown(self, event):
    if self.adjust:
      self.adjust.Destroy()
      self.adjust = None
    else:
      if not self.dual:
        value = self.slider_value
      elif self.GetValue():
        value = self.slider_value_on
      else:
        value = self.slider_value_off
      self.adjust = QSliderButtonWindow(self, value)
      if self.display:
        self.DisplaySliderValue(value)
  def SetLabel(self, text=None):
    if text is not None:
      QuiskCheckbutton.SetLabel(self, text)
  def DisplaySliderValue(self, value):
    value = self.slider_min + self.slider_max - value		# values are backwards
    value = float(value) / self.slider_max
    self.adjust.SetTitle("%6.3f" % value)
  def SetSlider(self, value=None, value_off=None, value_on=None):
    if value is not None:
      self.slider_value = value
    if value_off is not None:
      self.slider_value_off = value_off
    if value_on is not None:
      self.slider_value_on = value_on
  def OnSlider(self, event):
    value = event.GetEventObject().GetValue()
    if not self.dual:
      self.slider_value = value
    elif self.GetValue():
      self.slider_value_on = value
    else:
      self.slider_value_off = value
    self.SetValue(self.GetValue(), True)
    if self.display and self.adjust:
      self.DisplaySliderValue(value)
  def OnButton(self, event):
    if self.adjust:
      self.adjust.Destroy()
      self.adjust = None
    QuiskCheckbutton.OnButton(self, event)

class QuiskSpotButton(QuiskSliderButton):
  def SetLabel(self, text=None):
    if text is None:
      if self.adjust:
        value = self.slider_min + self.slider_max - self.slider_value
        text = "%.3f" % (value / 1000.)
      else:
        text = self.text
    QuiskCheckbutton.SetLabel(self, text)
    self.Refresh()

class QuiskImdButton(QuiskSliderButton):
  def OnSlider(self, event):
    value = event.GetEventObject().GetValue()
    self.slider_value = value
    if self.display and self.adjust:
      self.DisplaySliderValue(value)
    value = self.slider_min + self.slider_max - self.slider_value
    QS.set_imd_level(value)

class QuiskCycleCheckbutton(QuiskCheckbutton):
  """A button that cycles through its labels with each push.

  The button is up for labels[0], down for all other labels.  Change to the
  next label for each push.  If you call SetLabel(), the label must be in the list.
  The self.index is the index of the current label.
  """
  def __init__(self, parent, command, labels, color=None, is_radio=False):
    self.labels = list(labels)		# Be careful if you change this list
    self.index = 0		# index of selected label 0, 1, ...
    self.direction = 0	# 1 for up, -1 for down, 0 for no change to index
    self.is_radio = is_radio	# Is this a radio cycle button?
    if color is None:
      color = conf.color_cycle_btn
    QuiskCheckbutton.__init__(self, parent, command, labels[0], color)
    self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
    self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDclick)
  def SetLabel(self, label, do_cmd=False):
    self.index = self.labels.index(label)
    QuiskCheckbutton.SetLabel(self, label)
    QuiskCheckbutton.SetValue(self, self.index)
    if do_cmd and self.command:
      event = wx.PyEvent()
      event.SetEventObject(self)
      self.command(event)
  def SetIndex(self, index, do_cmd=False):
    self.index = index
    QuiskCheckbutton.SetLabel(self, self.labels[index])
    QuiskCheckbutton.SetValue(self, index)
    if do_cmd and self.command:
      event = wx.PyEvent()
      event.SetEventObject(self)
      self.command(event)
  def OnButton(self, event):
    if not self.is_radio or self.button_down:
      self.direction = 1
      self.index += 1
      if self.index >= len(self.labels):
        self.index = 0
      self.SetIndex(self.index)
    else:
      self.direction = 0
    if self.command:
      self.command(event)
  def OnRightDown(self, event):		# Move left in the list of labels
    if not self.is_radio or self.GetValue():
      self.index -= 1
      if self.index < 0:
        self.index = len(self.labels) - 1
      self.SetIndex(self.index)
      self.direction = -1
      if self.command:
        self.command(event)
  def OnLeftDclick(self, event):	# Left double-click: Set index zero
    if not self.is_radio or self.GetValue():
      self.index = 0
      self.SetIndex(self.index)
      self.direction = 1
      if self.command:
        self.command(event)

class RadioButtonGroup:
  """This class encapsulates a group of radio buttons.  This class is not a button!

  The "labels" is a list of labels for the toggle buttons.  An item
  of labels can be a list/tuple, and the corresponding button will
  be a cycle button.
  """
  def __init__(self, parent, command, labels, default):
    self.command = command
    self.buttons = []
    self.button = None
    for text in labels:
      if type(text) in (ListType, TupleType):
        b = QuiskCycleCheckbutton(parent, self.OnButton, text, is_radio=True)
        for t in text:
          if t == default and self.button is None:
            b.SetLabel(t)
            self.button = b
      else:
        b = QuiskCheckbutton(parent, self.OnButton, text)
        if text == default and self.button is None:
          b.SetValue(True)
          self.button = b
      self.buttons.append(b)
  def ReplaceButton(self, index, button):	# introduce a specialized button
    b =  self.buttons[index]
    b.Destroy()
    self.buttons[index] = button
    button.command = self.OnButton
  def SetLabel(self, label, do_cmd=False):
    self.button = None
    for b in self.buttons:
      if self.button is not None:
        b.SetValue(False)
      elif isinstance(b, QuiskCycleCheckbutton):
        try:
          index = b.labels.index(label)
        except ValueError:
          b.SetValue(False)
          continue
        else:
          b.SetIndex(index)
          self.button = b
          b.SetValue(True)
      elif b.GetLabel() == label:
        b.SetValue(True)
        self.button = b
      else:
        b.SetValue(False)
    if do_cmd and self.command and self.button:
      event = wx.PyEvent()
      event.SetEventObject(self.button)
      self.command(event)
  def GetButtons(self):
    return self.buttons
  def OnButton(self, event):
    win = event.GetEventObject()
    for b in self.buttons:
      if b is win:
        self.button = b
        b.SetValue(True)
      else:
        b.SetValue(False)
    if self.command:
      self.command(event)
  def GetLabel(self):
    if not self.button:
      return None
    return self.button.GetLabel()
  def GetSelectedButton(self):		# return the selected button
    return self.button
  def GetIndex(self):	# Careful.  Some buttons are complex.
    return self.buttons.index(self.button)

class FreqSetter(wx.TextCtrl):
  def __init__(self, parent, x, y, label, fmin, fmax, freq, command):
    self.pos = (x, y)
    self.label = label
    self.fmin = fmin
    self.fmax = fmax
    self.command = command
    self.font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL, face=conf.quisk_typeface)
    t = wx.StaticText(parent, -1, label, pos=(x, y))
    t.SetFont(self.font)
    freq_w, freq_h = t.GetTextExtent(" 662 000 000")
    tw, th = t.GetSizeTuple()
    x += tw + 20
    wx.TextCtrl.__init__(self, parent, size=(freq_w, freq_h), pos=(x, y),
      style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER)
    self.SetFont(self.font)
    self.Bind(wx.EVT_TEXT, self.OnText)
    self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
    w, h = self.GetSizeTuple()
    x += w + 1
    self.butn = b = wx.SpinButton(parent, size=(freq_h, freq_h), pos=(x, y))
    w, h = b.GetSizeTuple()
    self.end_pos = (x + w, y + h)
    b.Bind(wx.EVT_SPIN, self.OnSpin)	# The spin button frequencies are in kHz
    b.SetMin(fmin / 1000)
    b.SetMax(fmax / 1000)
    self.SetValue(freq)
  def OnText(self, event):
    self.SetBackgroundColour('pink')
  def OnEnter(self, event):
    text = wx.TextCtrl.GetValue(self)
    text = text.replace(' ', '')
    if '-' in text:
      return
    try:
      if '.' in text:
        freq = int(float(text) * 1000000 + 0.5)
      else:
        freq = int(text)
    except:
      return
    self.SetValue(freq)
    self.command(self)
  def OnSpin(self, event):
    freq = self.butn.GetValue() * 1000
    self.SetValue(freq)
    self.command(self)
  def SetValue(self, freq):
    if freq < self.fmin:
      freq = self.fmin
    elif freq > self.fmax:
      freq = self.fmax
    self.butn.SetValue(freq / 1000)
    txt = FreqFormatter(freq)
    wx.TextCtrl.SetValue(self, txt)
    self.SetBackgroundColour(conf.color_entry)
  def GetValue(self):
    value = wx.TextCtrl.GetValue(self)
    value = value.replace(' ', '')
    try:
      value = int(value)
    except:
      value = 7000
    return value
