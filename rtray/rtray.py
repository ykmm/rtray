#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""rtray.py: Launcher script for rtray."""

import logging

import wx

import RtrayController as controller

__author__ = "Yann Melikoff"
__copyright__ = "Copyright 2011"
__credits__ = ["Yann Melikoff"]
__license__ = "GPL"
__version__ = "0.1"
__email__ = "yann punto cappa emme emme chiocciola gmail punto com"
__status__ = "Development"

#Uncomment to show debug and info
#logging.basicConfig(level=logging.INFO, filename='rtray.log')

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    logging.info("Starting rtray")
    app = wx.App(False)
    contr = controller.RtrayController('rtray.yaml', {'user' : 'john.foo', 'pass': 'john.foo'})
    app.MainLoop()
    logging.info("Ending rtray")
