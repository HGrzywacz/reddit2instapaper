#!/usr/bin/python3
#/usr/bin/env python -O 
"""README GOES HERE

Version: 0.2beta
Licence: GPLv2

Copyright 2011 HGrzywacz <hgrzywacz@gmail.com>

progressbar by Anler Hernandez Peral (modified)
(https://github.com/ikame/progressbar)

"""

import sys
import os
import argparse
import datetime
import time
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import http.client
import getpass

# config file
import config

def main():

    # ACTIONS:

    def parse_actions(actions):
        for action in actions:
            if not action in list(funcs.keys()):
                print((action + " is not a valid action."))
                sys.exit()
            funcs[action]()

    def get_something():
        """ I'll think of this something later """
        print('Getting something.')

    def authenticate():
        instapaper.auth()
        print("Authentification to Instapaper successed.")

    def default_action():
        pass

    funcs = {'get':get_something, 'auth':authenticate, 
            'default':default_action}
    # dirty hack to prevent splitng string 'default' in chars
    choices = list(funcs.keys()).append(['default']) 

    # ARG-PARSER:
    
    class ParserHelp(object):
        '''Strings with help for argparser'''
        desc = 'Help text'
        actions = 'Select action'
        time = ('Specifies time range from which latest articles will be' 
                'fetched.')
        passw = ('Password to Instapaper account, in case'
                ' you don\'t want to store it in config file.')
        inter_pass = ('Ask for password'
                    ' interactively while running (will not be'
                    ' displayed).')
        subred = ('Specify subreddits other than'
                    ' those from config file.')

    parser = argparse.ArgumentParser(description=ParserHelp.desc)

    parser.add_argument('actions', nargs='*', type=str, choices=choices,
                    default=['default'], help=ParserHelp.actions)

#    parser.add_argument('-n','-num', dest='number', nargs=1, default=4,
#                    type=int, help='Number of top articles to fetch')
    
    parser.add_argument('-t','-time', dest='time', nargs=1, default=['3d'],
                    type=str, 
                    help=ParserHelp.time)

    parser.add_argument('-p','-pass','-password', dest='password',
                    nargs='?', default=config.password, type=str,
                    help=ParserHelp.passw)

    parser.add_argument('-P', dest='interactive_pass', 
                    action='store_true', help=ParserHelp.inter_pass)

    parser.add_argument('-s','-subreddits', dest='subreddits',
                    nargs='+', default=config.subreddit,
                    type=str, help=ParserHelp.subred)

    args = parser.parse_args(sys.argv[1:])

    print((args.actions))
#   print args.number
    print((args.time))

    def need_password():
        if args.interactive_pass:
            password = getpass.getpass('Instapaper password:')
        else:
            password = args.password
        return password

    password = need_password()

    time_limit = parse_time(args.time[0])

    print(time_limit)
    print((str(datetime.datetime.fromtimestamp(time_limit))))

    instapaper = Instapaper(config.username, password)
    
    parse_actions(args.actions)
    
    p = AnimatedProgressBar(end=100, width=100)
    while True:
        p + 5
        p.show_progress()
        time.sleep(0.01)
        if p.progress == 100:
            break
    print('')


class Instapaper(object):
    """ Instapaper API """
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.url_auth = "https://www.instapaper.com/api/authenticate"
        self.url_add = "https://www.instapaper.com/api/add"

    def auth(self):
        """ Method just for checking authentification. """
        params = urllib.parse.urlencode({'username':self.username, 
                'password':self.password})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                    "Accept": "text/plain"}

        connection = http.client.HTTPConnection("www.instapaper.com")
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
        print("\nError: Time specified", end=' ')
        print('(' + bad_time + ')', end=' ')
        print("couldn't be processed.")
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
        print((letter + ' ' + rest))

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

    print("Downloading submissions from", end=' ')
    if float(rest) > 1:
        print(("last " + rest + ' ' + str(mps_words[letter]) + 's.'))
    elif float(rest) == 1:
        print(("latest " + str(mps_words[letter]) + '.'))
    elif float(rest) < 0:
        print("Negative time? What I am supposed to do? Get submissions"
              " from the FUTURE?!")
        sys.exit()
    else:
        print(("last " + rest + " of a " + str(mps_words[letter]) + '.'))

    return time.time() - diff

# progressbar.py

class ProgressBar(object):
    """ProgressBar class holds the options of the progress bar.
    The options are:
        start   State from which start the progress. For example, if start is 
                5 and the end is 10, the progress of this state is 50%
        end     State in which the progress has terminated.
        width   --
        fill    String to use for "filled" used to represent the progress
        blank   String to use for "filled" used to represent remaining space.
        format  Format
        incremental
    """
    def __init__(self, start=0, end=10, width=12, fill='=', blank='.', format='[%(fill)s>%(blank)s] %(progress)s%%', incremental=True):
        super(ProgressBar, self).__init__()

        self.start = start
        self.end = end
        self.width = width
        self.fill = fill
        self.blank = blank
        self.format = format
        self.incremental = incremental
        self.step = 100 / float(width)
        self.reset()

    def __add__(self, increment):
        increment = self._get_progress(increment)
        if 100 > self.progress + increment:
            self.progress += increment
        else:
            self.progress = 100
        return self

    def __str__(self):
        progressed = int(self.progress/self.step)
        fill = progressed * self.fill
        blank = (self.width - progressed) * self.blank
        self.nrfills = progressed
        self.nrblanks =  (self.width - progressed) 
        return self.format % {'fill': fill, 'blank': blank, 'progress': int(self.progress)}

    __repr__ = __str__

    def _get_progress(self, increment):
        return float(increment * 100) / self.end

    def reset(self):
        """Resets the current progress to the start point"""
        self.progress = self._get_progress(self.start)
        return self


class AnimatedProgressBar(ProgressBar):
    """Extends ProgressBar to allow you to use it straighforward on a script.
    Accepts an extra keyword argument named `stdout` (by default use sys.stdout)
    and may be any file-object to which send the progress status.
    """
    def __init__(self, *args, **kwargs):
        super(AnimatedProgressBar, self).__init__(*args, **kwargs)
        self.stdout = kwargs.get('stdout', sys.stdout)

    def show_progress(self):
        if hasattr(self.stdout, 'isatty') and self.stdout.isatty():
            self.stdout.write('\r')
        else:
            self.stdout.write('\n')
        self.stdout.write(str(self))
        self.stdout.flush()


if __name__ == '__main__':
    main()
    sys.exit()
