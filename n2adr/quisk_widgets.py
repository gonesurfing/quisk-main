# Please do not change this widgets module for Quisk.  Instead copy
# it to your own quisk_widgets.py and make changes there.
#
# This module is used to add extra widgets to the QUISK screen.

from __future__ import print_function

import wx, time
import _quisk as QS

class BottomWidgets:	# Add extra widgets to the bottom of the screen
  def __init__(self, app, hardware, conf, frame, gbs, vertBox):
    self.config = conf
    self.hardware = hardware
    self.application = app
    row = app.widget_row			# The next available row
    b = app.QuiskCycleCheckbutton(frame, self.OnAntTuner, ('Antenna', 'Ant 0', 'Ant 1'))
    bw, bh = b.GetMinSize()
    gbs.Add(b, (row, 0), (1, 2), flag=wx.EXPAND)
    b = app.QuiskPushbutton(frame, self.OnAntTuner, 'L+')
    b.Enable(0)
    gbs.Add(b, (row, 2), (1, 2), flag=wx.EXPAND)
    b = app.QuiskPushbutton(frame, self.OnAntTuner, 'L-')
    b.Enable(0)
    gbs.Add(b, (row, 4), (1, 2), flag=wx.EXPAND)
    b = app.QuiskPushbutton(frame, self.OnAntTuner, 'C+')
    b.Enable(0)
    gbs.Add(b, (row, 6), (1, 2), flag=wx.EXPAND)
    b = app.QuiskPushbutton(frame, self.OnAntTuner, 'C-')
    b.Enable(0)
    gbs.Add(b, (row, 8), (1, 2), flag=wx.EXPAND)
    b = app.QuiskPushbutton(frame, self.OnAntTuner, 'Save')
    b.Enable(0)
    gbs.Add(b, (row, 10), (1, 2), flag=wx.EXPAND)
    self.swr_label = app.QuiskText(frame, 'Watts 000   SWR 10.1  Zh Ind 22 Cap 33   Freq 28100 (7777)', bh)
    gbs.Add(self.swr_label, (row, 15), (1, 10), flag=wx.EXPAND)
    b = app.QuiskCheckbutton(frame, None, text='')
    gbs.Add(b, (row, 25), (1, 2), flag=wx.EXPAND)
#  Example of a horizontal slider:
#    lab = wx.StaticText(frame, -1, 'Preamp', style=wx.ALIGN_CENTER)
#    gbs.Add(lab, (5,0), flag=wx.EXPAND)
#    sl = wx.Slider(frame, -1, 1024, 0, 2048)	# parent, -1, initial, min, max
#    gbs.Add(sl, (5,1), (1, 5), flag=wx.EXPAND)
#    sl.Bind(wx.EVT_SCROLL, self.OnPreamp)
#  def OnPreamp(self, event):
#    print event.GetPosition()
  def OnAntTuner(self, event):
    btn = event.GetEventObject()
    text = btn.GetLabel()
    self.hardware.OnAntTuner(text)
  def UpdateText(self, text):
    self.swr_label.SetLabel(text)
