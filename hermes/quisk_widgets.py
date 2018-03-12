# Please do not change this widgets module for Quisk.  Instead copy
# it to your own quisk_widgets.py and make changes there.
#
# This module is used to add extra widgets to the QUISK screen.

from __future__ import print_function

import wx

class BottomWidgets:	# Add extra widgets to the bottom of the screen
  def __init__(self, app, hardware, conf, frame, gbs, vertBox):
    self.config = conf
    self.hardware = hardware
    self.application = app
    self.start_row = app.widget_row			# The first available row
    self.start_col = app.button_start_col	# The start of the button columns
    self.Widgets_0x06(app, hardware, conf, frame, gbs, vertBox)
  def Widgets_0x06(self, app, hardware, conf, frame, gbs, vertBox):
    self.num_rows_added = 1
    start_row = self.start_row
    b = app.QuiskCheckbutton(frame, self.OnAGC, 'RfAgc')
    if hardware.hermes_code_version >= 40:
      b.Enable(False)
    gbs.Add(b, (start_row, self.start_col), (1, 2), flag=wx.EXPAND)
    bw, bh = b.GetMinSize()
    init = self.config.hermes_LNA_dB
    sl = app.SliderBoxHH(frame, 'RfLna %d dB', init, -12, 48, self.OnLNA, True)
    hardware.ChangeLNA(init)
    gbs.Add(sl, (start_row, self.start_col + 2), (1, 8), flag=wx.EXPAND)
    if conf.button_layout == "Small screen":
      # Display four data items in a single window
      self.text_temperature = app.QuiskText1(frame, '', bh)
      self.text_pa_current = app.QuiskText1(frame, '', bh)
      self.text_fwd_power = app.QuiskText1(frame, '', bh)
      self.text_swr = app.QuiskText1(frame, '', bh)
      self.text_data = self.text_temperature
      self.text_pa_current.Hide()
      self.text_fwd_power.Hide()
      self.text_swr.Hide()
      b = app.QuiskPushbutton(frame, self.OnTextDataMenu, '..')
      szr = self.data_sizer = wx.BoxSizer(wx.HORIZONTAL)
      szr.Add(self.text_data, 1, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
      szr.Add(b, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
      gbs.Add(szr, (start_row, self.start_col + 10), (1, 2), flag=wx.EXPAND)
      # Make a popup menu for the data window
      self.text_data_menu = wx.Menu()
      item = self.text_data_menu.Append(-1, 'Temperature')
      app.Bind(wx.EVT_MENU, self.OnDataTemperature, item)
      item = self.text_data_menu.Append(-1, 'PA Current')
      app.Bind(wx.EVT_MENU, self.OnDataPaCurrent, item)
      item = self.text_data_menu.Append(-1, 'Fwd Power')
      app.Bind(wx.EVT_MENU, self.OnDataFwdPower, item)
      item = self.text_data_menu.Append(-1, 'SWR')
      app.Bind(wx.EVT_MENU, self.OnDataSwr, item)
    else:
      self.text_temperature = app.QuiskText(frame, '', bh)
      self.text_pa_current = app.QuiskText(frame, '', bh)
      self.text_fwd_power = app.QuiskText(frame, '', bh)
      self.text_swr = app.QuiskText(frame, '', bh)
      gbs.Add(self.text_temperature, (start_row, self.start_col + 10), (1, 2), flag=wx.EXPAND)
      gbs.Add(self.text_pa_current, (start_row, self.start_col + 12), (1, 2), flag=wx.EXPAND)
      gbs.Add(self.text_fwd_power, (start_row, self.start_col + 15), (1, 2), flag=wx.EXPAND)
      gbs.Add(self.text_swr, (start_row, self.start_col + 17), (1, 2), flag=wx.EXPAND)
  def OnAGC(self, event):
    btn = event.GetEventObject()
    value = btn.GetValue()
    self.hardware.ChangeAGC(value)
  def OnLNA(self, event):
    sl = event.GetEventObject()
    value = sl.GetValue()
    self.hardware.ChangeLNA(value)
  def UpdateText(self):
    temp = self.hardware.hermes_temperature
    ## For best accuracy, 3.26 should be a user's measured 3.3V supply voltage.
    temp = (3.26 * (temp/4096.0) - 0.5)/0.01
    temp = (" Temp %3.1f" % temp) + unichr(0x2103)
    self.text_temperature.SetLabel(temp)
    current = self.hardware.hermes_pa_current
    ## 3.26 Ref voltage
    ## 4096 steps in ADC
    ## Gain of x50 for sense amp
    ## Sense resistor is 0.04 Ohms
    current = ((3.26 * (current/4096.0))/50.0)/0.04
    current = " Ampl %4d ma" % (1000*current)
    self.text_pa_current.SetLabel(current)
    fwd = self.hardware.hermes_fwd_power
    fwd = " %3.1f watts" % float(fwd)
    self.text_fwd_power.SetLabel(fwd)
    rev = self.hardware.hermes_rev_power
    swr = 1.2
    swr = " SWR %3.1f" % swr
    self.text_swr.SetLabel(swr)
  def OnTextDataMenu(self, event):
    btn = event.GetEventObject()
    btn.PopupMenu(self.text_data_menu, (0,0))
  def OnDataTemperature(self, event):
    self.data_sizer.Replace(self.text_data, self.text_temperature)
    self.text_data.Hide()
    self.text_data = self.text_temperature
    self.text_data.Show()
    self.data_sizer.Layout()
  def OnDataPaCurrent(self, event):
    self.data_sizer.Replace(self.text_data, self.text_pa_current)
    self.text_data.Hide()
    self.text_data = self.text_pa_current
    self.text_data.Show()
    self.data_sizer.Layout()
  def OnDataFwdPower(self, event):
    self.data_sizer.Replace(self.text_data, self.text_fwd_power)
    self.text_data.Hide()
    self.text_data = self.text_fwd_power
    self.text_data.Show()
    self.data_sizer.Layout()
  def OnDataSwr(self, event):
    self.data_sizer.Replace(self.text_data, self.text_swr)
    self.text_data.Hide()
    self.text_data = self.text_swr
    self.text_data.Show()
    self.data_sizer.Layout()
