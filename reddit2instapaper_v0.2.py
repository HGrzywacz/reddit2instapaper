#!/usr/bin/python -O
#/usr/bin/env python -O 
"""README GOES HERE

Version: 0.2beta
Licence: GPLv2

Copyright 2011 HGrzywacz <hgrzywacz@gmail.com>

"""

import sys
import os
import argparse
import datetime
import time
import urllib
import urllib2


def get_something():
    """ I'll think of this something later """
    pass


def authenticate():
    pass


funcs = {'get':get_something, 'auth':authenticate}
choices = funcs.keys()

def main():

    
    parser = argparse.ArgumentParser(description='Help text')
 

    parser.add_argument('actions', nargs='*', type=str, choices=choices,
            help='Select action.')

    parser.add_argument('-n','-num', dest='number', nargs=1, default=4,
                    type=int, help='Number of top articles to fetch')
    
    parser.add_argument('-t','-time', dest='time', nargs=1, default=['3d'],
                    type=str, help='Specifies time range from which latest articles'
                    ' will be fetched.')

    args = parser.parse_args(sys.argv[1:])


    print args.actions
    print args.number
    print args.time

    time_limit = parse_time(args.time[0])

    print time_limit
    print str(datetime.datetime.fromtimestamp(time_limit))

    parse_actions(args.actions)


def parse_actions(actions):
    for action in actions:
        if not action in funcs.keys():
            print action + " is not a valid action."
            sys.exit()
        funcs[action]()
        

class Instapaper(object):
    """ Instapaper API """
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.url_auth = "https://www.instapaper.com/api/authenticate"
        self.url_add = "https://www.instapaper.com/api/add"



    def auth(self):
        """ Method just for checking authentification. """
        params = urlib.urlencode({'username':self.user, 
                'password':self.password})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                    "Accept": "text/plain"}

        connection = httplib.HTTPConnection("www.instapaper.com")
        connection.request("POST", "/api/authenticate", params, headers)
    
        response = connection.getresponse()
    
        if response.status == 201:
            pass
        elif response.status == 403:
            print("Instapaper: Invalid username or password")
            sys.exit()
        elif response.status == 500:
            print("Instapaper: The service encountered"
                    " an error. Please try again later.")
            sys.exit()


 


class TimeException(Exception):
    '''Exception raised by parse_time.'''
    def __init__(self, bad_time):
        print "\nError: Time specified",
        print '(' + bad_time + ')',
        print "couldn't be processed."
        print("Try '3d', '2h', '120m'")
        sys.exit()

    
def parse_time(args_time):
    '''Parses time given after optional -t ... well, option.
    Time should be string in format 3d, 4m, 43s or even 0.829s.
    Message printed is constructed be grammaticaly correct.
    Returns date in past in unix format.
    Raises TimeException if this is too difficult to do.
    '''
    
    letter = args_time[-1]
    rest = args_time[0:-1]
    if rest is '':
        rest = "1"

    if __debug__:
        print letter + ' ' + rest

    seconds = 1
    minutes = 60 * seconds  # OCD-related
    hours = 60 * minutes
    days = hours * 24
    weeks = days * 7        # Careful!

    # pythonic as fuck
    mps = {'w':weeks, 'd':days, 'h':hours, 'm':minutes, 's':seconds}
    mps_words = {'w':'week', 'd':'day', 'h':'hour', 'm':'minute',
                's':'second'}

    # also pythonic
    try:
        multiplier = mps[letter]
    except KeyError:
        raise TimeException(args_time)

    try:
        diff = float(rest) * multiplier
    except ValueError:
        raise TimeException(args_time)

    print "Downloading submissions from",
    if float(rest) > 1:
        print "last " + rest + ' ' + str(mps_words[letter]) + 's.'
    elif float(rest) == 1:
        print "latest " + str(mps_words[letter]) + '.'
    elif float(rest) < 0:
        print("Negative time? What I am supposed to do? Get submissions"
              " from the FUTURE?!")
        sys.exit()
    else:
        print "last " + rest + " of a " + str(mps_words[letter]) + '.'

    return time.time() - diff


if __name__ == '__main__':
    main()
    sys.exit()
