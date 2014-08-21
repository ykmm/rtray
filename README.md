RTray
===========

A desktop client that stays in the system tray and periodically checks the
[RT request tracker](https://www.bestpractical.com/) for new tickets.

*This is alpha software, for the love of your family and pets, be careful!*

Install
-------

You can install it with:

    pip install git+https://github.com/ykmm/rtray.git

Note: you will need wxpython to be already installed because pip cannot install it.

In unity it could be necessary to set com.canonical.Unity.Panel
systray-whitelist "['all']" with gsettings
    
To run it execute:

    rtray

A login form will appear, the username is already filled, use john.foo as password.

The default installation connects to a demo installation at
http://rt.easter-eggs.org/demos/4.2


What does it do?
----------------
Rtray will periodically execute the queries read from the configuration file,
each execution's result is compared with the previous result for the same
query, if there is any difference, the tray icon will start blinking.

Clicking on the icon will open a browser window with a list of all the
tickets that have changed from the last update.

At first run the icon will blink, click on it to dismiss it (it will open
a browser window with a list of all the tickets from your different queries).

Icon meaning:

* ![image of idle icon](rtray/assets/rtray_idle.ico "Idle") Idle
* ![image of checking icon](rtray/assets/rtray_load.ico "Checking") Checking
* ![image of blink on icon](rtray/assets/rtray_blink_on.ico "Blink on") Blink on
* ![image of alert icon](rtray/assets/rtray_alert.ico "Alert") Alert
* ![image of alert icon](rtray/assets/rtray_error.ico "Error") Error

Configuration file 
------------------ 

You can change the configuration file
to connect to your ticketing system, here is the default configuration file
shipped with rtray.

    format: l
    logouturl: /REST/1.0/logout
    reststr: /REST/1.0/search/ticket
    rturl: http://rt.easter-eggs.org/demos/4.2
    searches:
        - {query: Creator= '@ME@' AND (Status = 'new' OR Status = 'open' OR Status = 'stalled'),
            title: Opened by me}
        - {query: Creator = '__CurrentUser__' AND (  Status = 'resolved' OR Status = 'rejected'),
            title: Opened by me and closed/rejected}
    username: !!python/unicode 'john.foo'

    
Queries are defined under the "searches" section, add an item that looks like
this:

    - {query: the text of your RT query, title: the title of your search}

The query syntax is the one used by RT, you can create the query in RT's
query builder and copy paste it in the configuration file

A query to extract all the open and unassigned ticket created by the current
user:

    - {query: Creator= '@ME@' AND Owner= 'Nobody', title: Opened by me and unassigned}


The following kewords can be used, they will be substituted before executing
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
