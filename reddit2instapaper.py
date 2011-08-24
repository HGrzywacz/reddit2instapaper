#!/usr/bin/env python2.7
''' Nifty script for adding submissions from reddit above certain upvotes number
to Instapaper.

In case of any questions: hgrzywacz@gmail.com , srsly, write ahead :)

Author: HGrzywacz
Mail: hgrzywacz@gmail.com
Version: 0.1beta
Licence: GPLv2

Testing version: DBG tag is my own way to... well, tagging places that I don't
wan't to run during testing. Probably DEBUG constant should be ommited in
master/stable(ish?) version entirely.
This is how I roll.

'''

import httplib
import urllib, urllib2
import sys, os
import json
import time, datetime
import re

from urlparse import urlparse, urlunparse, parse_qs

# my config module
import config

DEBUG = True

def insta_auth():
    params = urllib.urlencode({'username': config.username , 
        'password': config.password})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection("www.instapaper.com")
    conn.request("POST", "/api/authenticate", params, headers)
    
    response = conn.getresponse()
    
    if response.status == 201:
        pass
    elif response.status == 403:
        print("Instapaper: Invalid username or password")
        sys.exit()
    elif response.status == 500:
        print("Instapaper: The service encountered an error. Please try again"
                "later.")
        sys.exit()


def insta_add(url):

    params = urllib.urlencode({'username': config.username, 'password':
        config.password, 'url': url})

    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection("www.instapaper.com")
    conn.request("POST", "/api/add", params, headers)
    response = conn.getresponse()

    if response.status == 201:
        print ".",
    elif response.status == 403:
        print("Instapaper: Invalid username or password")
        sys.exit()
    elif response.status == 500:
        print("Instapaper: The service encountered an error. Please try again"
                "later.")
        sys.exit()



def red_get(url):
    
    scheme, host, path, params, query, fragment = urlparse(url)
    
    if query:
        parsed_params = parse_qs(query)
    else:
        parsed_params = query
    
    parsed_params['limit'] = [config.limit]

    fragment = None

    assert path.endswith('.json') or path.endswith('/')
    if path.endswith('/'):
        path = path + '.json'

    new_urltuple = (scheme, host, path, params,
                    urllib.urlencode(parsed_params, doseq = True), fragment)
    composed_sourceurl = urlunparse(new_urltuple)

    response = urllib.urlopen(composed_sourceurl)
    
    s = response.read()

    decoder = json.JSONDecoder()
    response = decoder.decode(s)

    return response # decoded json


def check_for_ignores(sub, domains_regexes):
    for regex in regexes:
        if regex.match(sub['data']['url']):
            return True

def make_regexes(ignore_domains):
    regexes = []
    for domain in ignore_domains:
        regexes.append(re.compile('.*' + domain + '.*'))
    return tuple(regexes)


if __name__ == "__main__":

    if not DEBUG:   #DBG
        insta_auth() # just for check
    
    submissions = []
    
    url = "http://www.reddit.com/r/" + config.subreddit + "/new.json?sort=new"
    response = red_get(url)

    found = False

    if os.path.exists('lasttime.txt'):
        f = open('lasttime.txt', 'r')
        last_time = float(f.read())
        f.close()
        date_for_print = datetime.date.fromtimestamp(last_time)
        print "Last time updated: " + date_for_print.__str__()
    else:
        print ("File lasttime.txt not found. Getting submits from last "
               + str(config.days) + " days.")
        last_time = float(time.time()) - config.days * 86400 #magic number - week in secs

    for res in response['data']['children']:
        if last_time >= res['data']['created_utc']:
            found = True
            break
        submissions.append(res)

    while not found:
        url = ("http://www.reddit.com/r/" + config.subreddit + "/new.json?sort=new" 
                + "&after=" + response['data']['after'])
        response = red_get(url)
        for res in response['data']['children']:
            if last_time >= res['data']['created_utc']:
                found = True
                break
            submissions.append(res)

    
    print str(len(submissions)) + " submissions downloaded."

    to_add = []

    for sub in submissions:
        if sub['data']['ups'] >= config.upvotes:
            to_add.append(sub)

    print (str(len(to_add)) + " submissions with more than " + str(config.upvotes)
            + " upvotes.")

    if len(to_add) > config.warning_above:

        print ('More than ' + str(config.warning_above) + ' ('
                + str(len(to_add)) + ')'
                + ' submissions to add. ' +
                'Would you like to proceed anyway? (y/n)')
        a = sys.stdin.read(1)
        if a != 'y':
            sys.exit()


    domains_regexes = make_regexes(config.ignore_domains)

    print "Adding:",
    for sub in to_add:
        if check_for_ignores(sub, domains_regexes):
            break
        if not DEBUG: #DBG
            insta_add(sub['data']['url'])
        else:
            print sub['data']['url']

    f = open('lasttime.txt','w')
    f.write(str(time.time()))
    f.close()


    


    sys.exit()

