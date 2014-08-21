#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RtrayController.py: Controller part of rtray."""

import wx
import RtrayModel as model
import RtrayView as view
#from wx.lib.pubsub import Publisher as pub
import logging
import sys, os
import subprocess
from collections import defaultdict

__author__ = "Yann Melikoff"
__copyright__ = "Copyright 2011"
__credits__ = ["Yann Melikoff"]
__license__ = "GPL"
__version__ = "0.1"
__email__ = "yann punto cappa emme emme chiocciola gmail punto com"
__status__ = "Development"

class RtrayController():
    def __init__(self, conffile = 'rtray-test.yaml', authdata = {'user' : 'john.foo', 'pass': 'john.foo'}):
        #Instantiate model and view
        logging.info("RtrayController:__init__():model and view instantiation")
        self.model = model.RtrayModel(conffile)
        
        #Invisible main frame
        self.view = view.RtrayView(None, -1, title='RTray Notifier', pos=(300, 300), size=(600, 400))

        #Auth frame
        self.authWindow = view.RtrayAuth(None, -1, title='RTray Notifier', pos=(300, 300), size=(600, 400))
        self.authWindow.label_url.SetLabel(self.model.rturl)
        self.authWindow.text_ctrl_user.SetValue(self.model.username)
        self.authWindow.Show()
        
        #Bind View Events to own events
        #logging.info("RtrayController:__init__():Bind View Events to own events")
        #Bind Icon events
        self.view.icon.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.left_click)
        self.view.icon.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.right_click)
        self.view.icon.Bind(wx.EVT_MENU, self.menu_click)
        #Bind auth window button event
        self.authWindow.button_login.Bind(wx.EVT_BUTTON, self.login_click)
        
        #TODO usare
        #self.view.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
        #Subscribe to model events messages binding to own events
        logging.info("RtrayController:__init__():Subscribe to model events messages binding to own events")
        #pub.subscribe(self.check_update_completed, "TICKETS UPDATED")

        #self.model.login(authdata['user'], authdata['pass'])
        
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
        logging.info("RtrayController:update_ticketinfo() - change icon, stop do_update timer, launch searches, start check_update timer")
        self.view.icon.setStatus('load')
        self.do_update_timer.Stop()
        #self.model.get_searches()
        self.model.get_searches_threaded()
        self.check_update_timer.Start(self.model.CHECK_UPDATE_INTERVAL)
        
    def check_update_completed(self, event):
        #logging.info("RtrayController:check_update_completed() remaining items: %s" % (self.model.queries_left, ))
        if self.model.check_update_completed():
            self.check_update_timer.Stop()
            self.do_update_timer.Start(self.model.UPDATE_INTERVAL)
            self.view.icon.setStatus('idle')
            #If we have new stuff
            if len(self.model.alert_tickets) > 0:
                logging.info("RtrayController:check_update_completed() - we got new stuff, save cache, blink, start do_update")
                ids = list()
                tooltip = list()
                tooltip.append('Ultimo aggiornamento')
                for ticketid, subject in self.model.alert_tickets:
                    tooltip.append("#%s: %s" % (ticketid, subject))
                    ids.append(ticketid)
                self.last_update_url = '%s%s%s' % (self.model.rturl, '/Search/Simple.html?q=',"+".join(ids))
                asd = "\n".join(tooltip)
                #print type(asd)
                self.last_tooltip = asd
                #self.last_tooltip = u'Iñtërnâtiônàlizætiøn На берегу пустынных волн'
                self.view.icon.tooltip = self.last_tooltip
                self.icon_blink_timer.Start(self.model.BLINK_INTERVAL)
            
        
    #Bound event methods
    def left_click(self, event):
        logging.info("RtrayController:left_click()")
        if self.last_update_url != '':
            self.open_rt_url(self.last_update_url)
        if self.view.icon.current_status in ('blink_on', 'blink_off'):
            #http://rt.easter-eggs.org/demos/stable /Search/Simple.html?q=506+576
            self.view.icon.setStatus('idle')
            self.icon_blink_timer.Stop()

    def right_click(self, event):
        logging.info("RtrayController:right_click()")
        self.view.icon.click(event)
        
    def menu_click(self, event):
        logging.info("RtrayController:menu_click()")
        item = self.view.icon.menu.FindItemById(event.GetId()) 
        text = item.GetText()
        if text == 'force check':
            if self.model.loggedin:
                self.update_ticketinfo('asd')
                logging.info("RtrayController:menu_click() - force update")
        elif text == 'about':
            self.view.about_dlg('asd')
        elif text == 'exit':
            logging.info("RtrayController:menu_click() - exit")
            self.close()
    
    def login_click(self, event):
        UserText = self.authWindow.text_ctrl_user.GetValue()
        PasswordText = self.authWindow.text_ctrl_pass.GetValue()
        self.model.login(UserText, PasswordText)
        if self.model.loggedin:
            self.authWindow.Close()
            #self.authWindow.Destroy()
            self.update_ticketinfo('asd')
            #self.do_update_timer.Start(self.model.UPDATE_INTERVAL)
        else:
            wx.MessageBox("username/pass not valid")
        
    #http://stackoverflow.com/questions/4216985/python-call-to-operating-system-to-open-url
    def open_rt_url(self, url):
        logging.info("RtrayController:open_rt_url() [%s]", (url, ))
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
        logging.info("RtrayController:close() - destroy view, save cache, logout")
        #frame.Show()
        #self.authWindow.Destroy()
        self.view.icon.Destroy()
        self.view.Close()
        #self.view.Destroy()
        self.model.logout()

        logging.info("RtrayController:close() - finished")
                
if __name__ == '__main__':
    app = wx.App(False)
    controller = RtrayController()
    app.MainLoop()
