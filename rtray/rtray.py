#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""rtray.py: Launcher script for rtray."""

import logging, logging.config

import wx

import RtrayController as controller

#Uncomment to show debug and info
#logging.basicConfig(level=logging.INFO, filename='rtray.log')

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    #logging.getLogger().setLevel(level=logging.DEBUG)

    #logging.basicConfig(level = logging.DEBUG)
    logger.info("Starting rtray")
    app = wx.App(False)
    contr = controller.RtrayController('rtray.yaml')
    app.MainLoop()
    logger.info("Ending rtray")
