#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RtrayController.py: Controller part of rtray."""

import wx
import RtrayModel as model
import RtrayView as view
import logging
logger = logging.getLogger(__name__)
import sys, os
import subprocess
from collections import defaultdict

class RtrayController():
    def __init__(self, conffile = 'rtray-test.yaml'):
        #Instantiate model and view
        logger.debug("model and view instantiation")
        self.model = model.RtrayModel(conffile)

        #Invisible main frame
        self.view = view.RtrayView(None, -1, title='RTray Notifier', pos=(300, 300), size=(600, 400))

        #Auth frame
        self.authWindow = view.RtrayAuth(None, -1, title='RTray Notifier', pos=(300, 300), size=(600, 400))
        self.authWindow.label_url.SetLabel(self.model.rturl)
        self.authWindow.text_ctrl_user.SetValue(self.model.username)
        self.authWindow.Show()

        #Bind View Events to own events
        logger.debug("Bind View Events to own events")
        #Bind Icon events
        self.view.icon.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.left_click)
        self.view.icon.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.right_click)
        self.view.icon.Bind(wx.EVT_MENU, self.menu_click)
        #Bind auth window button event
        self.authWindow.button_login.Bind(wx.EVT_BUTTON, self.login_click)

        #TODO
        #use self.view.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        #Subscribe to model events messages binding to own events
        #logger.info("Subscribe to model events messages binding to own events")
        #pub.subscribe(self.check_update_completed, "TICKETS UPDATED")

        #Prepare timers
        self.do_update_timer = wx.Timer(self.view)
        self.view.Bind(wx.EVT_TIMER, self.update_ticketinfo, self.do_update_timer)

        self.check_update_timer = wx.Timer(self.view)
        self.view.Bind(wx.EVT_TIMER, self.check_update_completed, self.check_update_timer)

        self.icon_blink_timer = wx.Timer(self.view)
        self.view.Bind(wx.EVT_TIMER, self.view.icon.Blink, self.icon_blink_timer)

        #Holds the search url for the last update with new items
        self.last_update_url = ''

    def update_ticketinfo(self,message):
        logger.debug("change icon, stop do_update timer, launch searches, start check_update timer")
        self.view.icon.setStatus('load')
        self.do_update_timer.Stop()
        self.model.get_searches_threaded()
        self.check_update_timer.Start(self.model.CHECK_UPDATE_INTERVAL)

    def check_update_completed(self, event):
        #logger.info("RtrayController:check_update_completed() remaining items: %s" % (self.model.queries_left, ))
        if self.model.check_update_completed():
            self.check_update_timer.Stop()
            self.do_update_timer.Start(self.model.UPDATE_INTERVAL)
            self.view.icon.setStatus('idle')
            #If we have new stuff
            if len(self.model.alert_tickets) > 0:
                logger.info("we got new stuff, save cache, blink, start do_update")
                ids = list()
                tooltip = list()
                tooltip.append('Ultimo aggiornamento')
                for ticketid, subject in self.model.alert_tickets:
                    tooltip.append("#%s: %s" % (ticketid, subject))
                    ids.append(ticketid)
                self.last_update_url = '%s%s%s' % (self.model.rturl, '/Search/Simple.html?q=',"+".join(ids))
                asd = "\n".join(tooltip)
                self.last_tooltip = asd
                #self.last_tooltip = u'Iñtërnâtiônàlizætiøn На берегу пустынных волн'
                self.view.icon.tooltip = self.last_tooltip
                self.icon_blink_timer.Start(self.model.BLINK_INTERVAL)


    #Bound event methods
    def left_click(self, event):
        logger.debug("left click")
        if self.last_update_url != '':
            self.open_rt_url(self.last_update_url)
        if self.view.icon.current_status in ('blink_on', 'blink_off'):
            self.view.icon.setStatus('idle')
            self.icon_blink_timer.Stop()

    def right_click(self, event):
        logger.debug("right click")
        self.view.icon.click(event)

    def menu_click(self, event):
        logger.debug("menu click")
        item = self.view.icon.menu.FindItemById(event.GetId())
        text = item.GetText()
        if text == 'force check':
            if self.model.loggedin:
                self.update_ticketinfo('asd')
                logger.debug("force update")
        elif text == 'about':
            self.view.about_dlg('asd')
        elif text == 'exit':
            logger.debug("exit")
            self.close()

    def login_click(self, event):
        UserText = self.authWindow.text_ctrl_user.GetValue()
        PasswordText = self.authWindow.text_ctrl_pass.GetValue()
        self.model.login(UserText, PasswordText)
        if self.model.loggedin:
            self.authWindow.Close()
            self.update_ticketinfo('asd')
        else:
            wx.MessageBox("username/pass not valid")

    def open_rt_url(self, url):
        #http://stackoverflow.com/questions/4216985/python-call-to-operating-system-to-open-url
        logger.info("Open [%s]" % url)
        if sys.platform=='win32':
            os.startfile(url)
        elif sys.platform=='darwin':
            subprocess.Popen(['open', url])
        else:
            try:
                subprocess.Popen(['xdg-open', url])
            except OSError:
                print 'Please open a browser on: '+url

    def close(self):
        logger.info("destroy view, save cache, logout")
        self.view.icon.Destroy()
        self.view.Close()
        self.model.logout()
        logger.info("finished")

if __name__ == '__main__':
    app = wx.App(False)
    controller = RtrayController()
    app.MainLoop()
