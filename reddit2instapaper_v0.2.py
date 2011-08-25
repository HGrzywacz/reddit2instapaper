#!/usr/bin/env python2.7

import sys
import os
import argparse
import datetime
import time


def main(argv):
    parser = argparse.ArgumentParser(description='My learning parser')
    parser.add_argument('action', nargs='*', type=str, help='Select action')
    parser.add_argument('-n','-num', dest='number', nargs=1, default=4,
            type=int, help='Number of top articles to fetch')
    parser.add_argument('-t','-time', dest='time', nargs=1, default='3d',
            type=str, help='Specifies time range from which latest articles'
            ' will be fetched.')

    args = parser.parse_args(argv)
    print args.action
    print args.number
    print args.time
    time_limit = parse_time(args.time[0])
    print time_limit
    print str(datetime.datetime.fromtimestamp(time_limit))


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
    main(sys.argv)
    sys.exit()
