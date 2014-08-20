#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RtrayModel.py: Model part of rtray."""

import logging
logger = logging.getLogger(__name__)
import re
from collections import defaultdict
import threading
import Queue
import datetime
import time
import urllib
import copy

#from wx.lib.pubsub import Publisher as pub
import wx
import pycurl
import yaml

__author__ = "Yann Melikoff"
__copyright__ = "Copyright 2011"
__credits__ = ["Yann Melikoff"]
__license__ = "GPL"
__version__ = "0.1.0"
__email__ = "yakemema@gmail.com"
__status__ = "Development"

class RtrayPycurl():
    """RtrayPycurl instance of Pycurl with a series of options already set."""
    def __init__(self, writecookies = False):
        """Pycurl instance with a series of options already set.

        Params:
        writecookie -- Pass True in order to have this instance write to the common cookie file

        """
        self.c = pycurl.Curl()
        self.c.setopt(pycurl.FOLLOWLOCATION,1)
        if writecookies:
            self.c.setopt(pycurl.COOKIEJAR,'rtraycookies.txt')
        self.c.setopt(pycurl.COOKIEFILE,'rtraycookies.txt')
        self.c.setopt(pycurl.USERAGENT,'RTray/0.1.0')
        self.c.setopt(pycurl.WRITEFUNCTION, self.fill_buffer)
        self.c.setopt(pycurl.HEADERFUNCTION, self.fill_headers)

        self.c.setopt(pycurl.SSL_VERIFYPEER, 0)

        #DEBUG if activated will put headers in output rendering them not parsable
        self.c.setopt(pycurl.HEADER,0)
        self.c.setopt(pycurl.VERBOSE,0)

        self.headersplit = re.compile(r': ')
        self.buffer = ''
        self.headers = list()

    def get_url(self, url, postdata = list()):
        logger.info("Grabbing [%s]" % (url,))
        #Added to avoid cross-site protection
        self.c.setopt(pycurl.HTTPHEADER, ["Referer: http://rt.easter-eggs.org/demos/4.2/REST/1.0/"])
        if len(postdata) > 0:
            self.c.setopt(pycurl.POST, 1)
            self.c.setopt(pycurl.POSTFIELDS, urllib.urlencode(postdata))
        else:
            self.c.setopt(pycurl.POST, 0)

        self.c.setopt(pycurl.URL, url)
        try:
            self.c.perform()
        except:
            self.buffer = ''
            logger.info("Unable to access [%s]" % (url,))

    def fill_buffer(self, buf):
        self.buffer = self.buffer + buf

    def fill_headers(self, buf):
        self.headers.append(buf)

    def pop_buffer(self):
        t = self.buffer
        self.buffer = ''
        return t

class ThreadCurl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, out_queue):
        logger.debug("Hi I am ThreadCurl being inited, I don't know who I am")
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue
        self.pycurl = RtrayPycurl()

    def run(self):
        logger.debug("[%s]" % (self,))
        while True:
            #logger.info("ThreadCurl:run() - While true [%s]" % (self,))
            #grabs host from queue
            try:
                search = self.queue.get_nowait()
                start = time.time()

                #grabs urls of hosts and then grabs chunk of webpage

                self.pycurl.get_url(search['url'])
                chunk = unicode(self.pycurl.pop_buffer(), 'utf8')
                #place chunk into out queue
                self.out_queue.put({'title': search['title'], 'data': chunk})
                logger.info("Grabbing [%s] in %s" % (search['url'],time.time() - start))
            except Queue.Empty:
                #logger.info("ATTAH! empty queue thread #[%s]" % (self,))
                continue


            #signals to queue job is done
            self.queue.task_done()

class RtrayModel():
    def __init__(self, conf_file):
        self.conf_file = conf_file
        confdata = open(self.conf_file).read()
        self.confparsed = yaml.load(confdata)
        #pycurl stuff
        self.pycurl = RtrayPycurl()

        #Configuration data
        #URLS
        self.rturl = self.confparsed['rturl']
        self.rtlogout = "%s%s" % (self.rturl, self.confparsed['logouturl'])
        self.loggedin = False
        try:
            self.username = self.confparsed['username']
        except:
            self.username = ""

        #Query params
        self.reststr = self.confparsed['reststr']
        self.format = self.confparsed['format']
        self.queries = copy.deepcopy(self.confparsed['searches'])
        self.queries_left = 0
        """
        for i in range(len(self.queries)):
            self.queries[i]['url'] = "%s%s?query=%s&format=%s" % (self.rturl, self.reststr, urllib.quote_plus(self.queries[i]['query']), self.format)
        """
        #Internal data structures and constants
        self.ticket_update = defaultdict(dict)
        self.alert_tickets = list()
        self.rest_rawdata = dict()
        self.url_queue = Queue.Queue()
        self.parsed_queue = Queue.Queue()
        self.RT_NOLOGIN = re.compile(r'Your username or password is incorrect')
        self.RT_REST_SPLIT = re.compile(r'(?:\n.+)+', re.MULTILINE)
        self.REST_FIND_SEP = re.compile(r'\n\n--(?:\n)*', re.MULTILINE | re.IGNORECASE)
        self.REST_TICKET_ID = re.compile(r'id: ticket/([0-9]+)$', re.MULTILINE | re.IGNORECASE)
        self.REST_TICKET_SUBJ = re.compile(r'Subject: (.*)$', re.MULTILINE | re.IGNORECASE)
        self.REST_TICKET_LASTUPDATED = re.compile(r'LastUpdated: (.*)$', re.MULTILINE | re.IGNORECASE)

        #Regexps for search and replace tags in queries
        self.QUERY_REPL_ME = re.compile(r'@ME@', re.MULTILINE | re.IGNORECASE)
        self.QUERY_REPL_TODAY = re.compile(r'@TODAY@', re.MULTILINE | re.IGNORECASE)
        self.QUERY_REPL_ONEMONTHAGO = re.compile(r'@ONE_MONTH_AGO@', re.MULTILINE | re.IGNORECASE)

        #Timer settings for controller in msecs
        self.UPDATE_INTERVAL = 60000
        self.BLINK_INTERVAL = 600
        self.CHECK_UPDATE_INTERVAL = 1000

        #spawn a pool of threads, and pass them queue instance
        self.threadpool = list()
        for i in range(len(self.queries)):
            t = ThreadCurl(self.url_queue, self.parsed_queue)
            t.setDaemon(True)
            t.start()
            self.threadpool.append(t)

        self._load_cache()

    def _load_cache(self):
        cache_ok = True
        logger.debug("Loading cache")
        try:
            cachefile = open('rtray-cache.yaml')
            #In case of corrupted yaml
            try:
                tmp_cache = yaml.load(cachefile.read())
                cachefile.close()

                #Lazy cache integrity check for existence of content or keys
                if type(tmp_cache) != type(None):
                    for search in self.queries:
                        if not tmp_cache.has_key(search['title']):
                            cache_ok = False
                else:
                    cache_ok = False
            except:
                cache_ok = False

            if cache_ok:
                logger.debug("Cache lazy check ok")
                self.ticket_cache = tmp_cache
            else:
                logger.debug("Cache file invalid, resetting")
                self.ticket_cache = defaultdict(dict)

        except IOError as e:
            self.ticket_cache = defaultdict(dict)

    def _update_cache(self, new_cache_vals):
        self.alert_tickets = list()
        for title, ticketid, timestamp, subject in new_cache_vals:
            #If ticket is already in cache
            if self.ticket_cache[title].has_key(ticketid):
                if not self.ticket_cache[title][ticketid] == timestamp:
                    logger.debug("UPDATE VAL (%s, %s, %s, %s)" % (title, ticketid, timestamp, subject))
                    self.ticket_cache[title][ticketid] = timestamp
                    #Will insert only unique items
                    try:
                        self.alert_tickets.index((ticketid, subject))
                    except:
                        self.alert_tickets.append((ticketid, subject))
            else:
                logger.debug("NEW VAL (%s, %s, %s, %s)" % (title, ticketid, timestamp, subject))
                self.ticket_cache[title][ticketid] = timestamp
                try:
                    self.alert_tickets.index((ticketid, subject))
                except:
                    self.alert_tickets.append((ticketid, subject))

        if len(self.alert_tickets) > 0:
            self._save_cache()

    def _save_cache(self):
        logger.debug("Saving cache in rtray-cache.yaml")
        cachefile = open('rtray-cache.yaml', "w")
        cachefile.write(yaml.dump(self.ticket_cache))
        cachefile.close()

    def _update_configuration(self):
        logger.debug("Saving configuration file")
        conffile = open(self.conf_file, "w")
        conffile.write(yaml.dump(self.confparsed))
        conffile.close()

    def login(self, username, password):
        logger.info("Logging in")
        logindata = {'user': username, 'pass': password}
        login_pycurl = RtrayPycurl(True)

        try:
            login_pycurl.get_url(self.rturl, logindata)
            logger.debug("Login with pycurl ok")
        except IOError, e:
            logger.debug("Login with pycurl had problems [%s]" % (e[0], ))
            return
        tmpres = login_pycurl.pop_buffer()
        login_pycurl.c.close()

        #if contains "Your username or password is incorrect" then login has failed
        tmpres = re.findall(self.RT_NOLOGIN, tmpres)
        if len(tmpres) > 0:
            logger.info("username/pass not valid")
            self.loggedin = False
        else:
            logger.info("login ok")
            self.loggedin = True
            self.confparsed['username'] = username
            self.username = username
            self._update_configuration()
            onemontago = datetime.date.today() - datetime.timedelta(days=30)
            today = datetime.date.today()
            for i in range(len(self.queries)):
                tmpquery = self.queries[i]['query']
                tmpquery = re.sub(self.QUERY_REPL_ME, self.username, tmpquery)
                tmpquery = re.sub(self.QUERY_REPL_TODAY, today.isoformat(), tmpquery)
                tmpquery = re.sub(self.QUERY_REPL_ONEMONTHAGO, onemontago.isoformat(), tmpquery)
                self.queries[i]['url'] = "%s%s?query=%s&format=%s" % (self.rturl, self.reststr, urllib.quote_plus(tmpquery), self.format)

    def logout(self):
        logger.info("Doing logout")
        try:
            self.pycurl.get_url(self.rtlogout)
            logger.info("successful")
        except:
            logger.info("did not work")

        try:
            os.remove('rtraycookies.txt')
            logger.info("delete cookie file")
        except:
            pass

    def _parse_ticket(self, ticket_raw):
        """Parses one ticket block at a time and returns ID, LASTUPDATE and SUBJECT
           or false, false, false in case nothing is found
        """
        match_ticket_id = re.findall(self.REST_TICKET_ID, ticket_raw)
        if len (match_ticket_id) > 0:
            ticketid = re.findall(self.REST_TICKET_ID, ticket_raw)[0]
            ticketlastupdated = re.findall(self.REST_TICKET_LASTUPDATED, ticket_raw)[0]
            ticketsubject = re.findall(self.REST_TICKET_SUBJ, ticket_raw)[0]
            return ticketid, ticketlastupdated, ticketsubject
        else:
            return False, False, False

    def _parse_searches(self):
        logger.info("Parse search results")
        new_cache_vals = list()
        for search in self.queries:
            #rest_answer is a list of lines containing the requested data
            rest_answer = self.rest_rawdata[search['title']].splitlines(True)
            if rest_answer[0][-7:-1] == '200 Ok':
                logger.debug("'200 Ok' found in answer - parsing")
                rest_answer = "".join(rest_answer[2:])
                tickets = re.finditer(self.REST_FIND_SEP, rest_answer)
                start = 0
                for ticket in tickets:
                    end = ticket.start()
                    ticket_raw = rest_answer[start:end]
                    ticketid, ticketlastupdated, ticketsubj = self._parse_ticket(ticket_raw)
                    if ticketid:
                        new_cache_vals.append((search['title'], ticketid, ticketlastupdated, ticketsubj))
                    start = ticket.end()

                #last item
                ticket_raw = rest_answer[start:]
                ticketid, ticketlastupdated, ticketsubj = self._parse_ticket(ticket_raw)
                if ticketid:
                    new_cache_vals.append((search['title'], ticketid, ticketlastupdated, ticketsubj))
            else:
                logger.debug("'200 Ok' NOT found in answer")
                logger.debug("".join(rest_answer))

        self._update_cache(new_cache_vals)

    def get_searches(self):
        logger.info("Querying RT")
        for search in self.queries:
            logger.debug("getting %s %s" % (search['title'], search['url'],) )
            try:
                self.pycurl.get_url(search['url'])
                self.rest_rawdata[search['title']] = self.pycurl.pop_buffer()
            except:
                logger.debug("pycurl error")

    def get_searches_threaded(self):
        logger.debug("Filling queue")
        self.queries_left = len(self.queries)
        #populate queue with data
        for search in self.queries:
            self.url_queue.put({'title': search['title'], 'url': search['url']})

    def check_update_completed(self):
        #Try to poll remaining items
        for i in range(self.queries_left):
            try:
                res = self.parsed_queue.get_nowait()
                self.rest_rawdata[res['title']] = res['data']
                self.queries_left -= 1
            except Queue.Empty:
                continue
        if self.queries_left > 0:
            return False
        else:
            self._parse_searches()
            self._save_cache()
            return True

if __name__ == '__main__':
    #logging.basicConfig(level = logging.INFO)
    import objgraph
    model = RtrayModel('rtray-test.yaml')
    model.login('john.foo', 'john.foo')
    start = time.time()

    while True:
        if True:
            model.get_searches_threaded()
            while model.queries_left > 0:
                model.check_update_completed()

        else:
            model.get_searches()
            model.logout()
        print "Elapsed Time: %s" % (time.time() - start)
        objgraph.show_most_common_types()
        #objgraph.show_growth()

