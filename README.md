RTray
===========

**This is alpha software, for the love of your family and pets, be careful!**

A desktop client that stays in the system tray and periodically checks the
[RT request tracker](https://www.bestpractical.com/) for new tickets.

Usage
-----

Just run it, it will periodically execute the queries in the config files,
each execution's result is compared with the previous result for the same
query, if there is any difference, the tray icon will start blinking.

Clicking on the icon will open a browser window with a list of all the
tickets that have changed from the last update.

Icon meaning:

* ![image of idle icon](rtray/assets/rtray_idle.ico "Title") Idle
* ![image of checking icon](rtray/assets/rtray_load.ico "Title") Checking
* ![image of blink on icon](rtray/assets/rtray_blink_on.ico "Title") Blink on
* ![image of alert icon](rtray/assets/rtray_alert.ico "Title") Alert
* ![image of alert icon](rtray/assets/rtray_error.ico "Title") Error

Install
-------
Clone the project, edit the rtray.yaml configuration file.

install the following packages:
sudo apt-get install python-yaml python-wxtools python-pycurl

for ubuntu unity, launch gsettings and set com.canonical.Unity.Panel
systray-whitelist "['all']"

Configuration file
------------------

    format: l
    reststr: /REST/1.0/search/ticket
    rturl: http://rt.easter-eggs.org/demos/4.2
    searches:
    - {query: Queue = '1454 Client Project' AND (  Status = 'new' OR Status = 'open' OR
        Status = 'stalled' ), title: Observed queue}
    - {query: (  Status = 'new' OR Status = 'open' OR Status = 'stalled' ), title: New
        or open queue}
    - {query: Status = 'open' OR Status = 'new' OR Status = 'resolved', title: Long query}

Queries are defined in the following way, under the "searches" section, add
an item that looks like this:

    - {query: the text of your RT query, title: the title of your search}

A query to extract all the open and unassigned ticket created by the current
user:

    - {query: Creator= '@ME@' AND Owner= 'Nobody', title: Opened by me and unassigned}

The query syntax is exactly the same that is used in RT, inside the queries
the following kewords can be used, they will be substituted before executing
the query:

* @ME@ : the username used for authentication
* @TODAY@ : today's date in iso format
* @ONE_MONTH_AGO@: one month's ago date in iso format

Other query examples:

    - {query: Owner= 'Nobody' AND ( Status = 'new' OR Status = 'open' OR Status = 'stalled'), title: Unassigned Tickets}
    - {query: Creator = '__CurrentUser__' AND (  Status = 'resolved' OR Status = 'rejected'), title: Opened by me, closed or rejected}
    - {query: Creator= '@ME@' AND Owner= 'Nobody', title: Opened by me and unassigned}

When a new query is added, the first time that rtray checks it, it will find
ALL the tickets matching the query, so the tray icon will blink, just dismiss
it by clicking on it.

To reset the application cache cancel the file rtray-cache.yaml
