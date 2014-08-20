#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RtrayModel.py: View part of rtray."""

import wx
from wx.lib.wordwrap import wordwrap


from RtrayViewWxg import RttrayFrame, AuthFrame
import logging
logger = logging.getLogger(__name__)

__author__ = "Yann Melikoff"
__copyright__ = "Copyright 2011"
__credits__ = ["Yann Melikoff"]
__license__ = "GPL"
__version__ = "0.1.0"
__email__ = "yakemema@gmail.com"
__status__ = "Development"

class Icon(wx.TaskBarIcon):
    """notifier's taskbar icon"""

    def __init__(self, menuitems):
        wx.TaskBarIcon.__init__(self)

        # menu options
        self.menuitems = menuitems
        self.current_status = None
        self.tooltip = u''

        # icon state
        self.states = {
            u"idle": wx.Icon("assets/rtray_idle.ico", wx.BITMAP_TYPE_ICO),
            u"load": wx.Icon("assets/rtray_load.ico", wx.BITMAP_TYPE_ICO),
            u"error": wx.Icon("assets/rtray_error.ico", wx.BITMAP_TYPE_ICO),
            u"alert": wx.Icon("assets/rtray_alert.ico", wx.BITMAP_TYPE_ICO),
            u"blink_on": wx.Icon("assets/rtray_blink_on.ico", wx.BITMAP_TYPE_ICO),
            u"blink_off": wx.Icon("assets/rtray_blink_off.ico", wx.BITMAP_TYPE_ICO)
        }
        self.setStatus("idle")
        self.blink_state = False
        self.menu = wx.Menu()
        for id, item in enumerate(self.menuitems):
            self.menu.Append(id, item)

    def click(self, event):
        """shows the menu"""
        self.PopupMenu(self.menu)

    def select(self, event):
        """handles menu item selection"""

        self.menu[event.GetId()][1]()

    def Blink(self, evt):
        if not self.current_status == 'blink_on':
            self.setStatus('blink_on')
        else:
            self.setStatus('blink_off')

    def setStatus(self, which):
        """sets the icon status"""
        logger.debug("Icon:setStatus(%s)" % (which,))
        self.SetIcon(self.states[which], self.tooltip)
        #self.SetIcon(self.states[which])
        self.current_status = which

    def close(self, event):
        """destroys the icon"""

        self.Destroy()

class RtrayAuth(AuthFrame):
    def __init__(self, *args, **kwds):
        AuthFrame.__init__(self, *args, **kwds)


class RtrayView(RttrayFrame):
    def __init__(self, *args, **kwds):
        RttrayFrame.__init__(self, *args, **kwds)
        #self.frame = rtrayFrame('rtray',(300,300),(600,400))
        #self.frame.Show()
        #self.SetTopWindow(self.frame)e
        #self.frame.Bind(wx.EVT_MOTION, self.on_mouse)
        #self.frame.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_windows)
        #self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_windows)
        #setup taskbar icon
        self.icon = Icon(['force check', 'about', 'exit'])

        #self.timer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.test, self.timer)
        #self.timer.Start(1000)

        #About box
        self.info = wx.AboutDialogInfo()
        self.info.Name = "Rtray"
        self.info.Version = "0.1.0 Beta"
        self.info.Copyright = "(C) 2011 Yann Melikoff"
        self.info.Description = wordwrap(
            "System tray Icon that periodically checks for "
            "updated tickets in observed queries",
            250, wx.ClientDC(self))
        #self.info.WebSite = ("http://www.pythonlibrary.org", "My Home Page")
        self.info.Developers = ["Yann Melikoff"]
        #self.info.License = wordwrap("Completely and totally open source!", 500, wx.ClientDC(self))

    def test(self,event):
        print "on_mouse",event

    def on_enter_windows(self,event):
        print "on_enter_windows",event

    def on_leave_windows(self,event):
        print "on_leave_windows",event

    def update_domain_list(self,domainList):
        print self.frame.update_domain_list(domainList)

    def about_dlg(self, event):
        # Show the wx.AboutBox
        wx.AboutBox(self.info)

if __name__ == '__main__':
    #logging.basicConfig(level = logging.INFO)
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    view = rtrayView(None, -1, "")
    app.SetTopWindow(view)
    view.Show()
    app.MainLoop()
