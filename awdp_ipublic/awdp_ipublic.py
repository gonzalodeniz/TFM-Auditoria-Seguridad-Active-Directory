#!/usr/bin/env python
# coding=utf-8

"""
    File:           awdp_ipublic.py
    Version:        1.0
    Date Version:   23/03/2017
    Author:         Gonzalo Déniz

    NAME
        awdp_ipublic - Returns the public ip of the current network.

    SYNOPSIS:

        python awdp_ipublic.py

    DESCRIPTION
        Returns the public ip of the current network. Use the url: https://api.ipify.org' to get the public ip.

    OPTIONS
        Nothing

    FILES
        awdp_ipublic.py          Executable and class file
"""

import urllib2
import sys

class IPublic(object):
    API_MY_IP = 'https://api.ipify.org'
    @staticmethod
    def my_ip():
        '''Consults on the internet public ip
        '''
        user_agent = 'Mozilla/5.0'
        hdr = {'User-Agent':user_agent,}
        req = urllib2.Request(IPublic.API_MY_IP, headers=hdr)
        ur = urllib2.urlopen(req)
        response = ur.read()
        ur.close()
        return response


def man():
    man = '''
    NAME
        awdp_ipublic - Returns the public ip of the current network.

    SYNOPSIS:

        python awdp_ipublic.py

    DESCRIPTION
        Returns the public ip of the current network. Use the url: https://api.ipify.org' to get the public ip.

    OPTIONS
        Nothing

    FILES
        awdp_ipublic.py          Executable and class file
    '''
    return man

def argument(argv):
    MIN_NARG = 1    # Minimum number of arguments
    argv_d = {}     # Arguments to pass to main()

    # Minimum number of arguments
    if len(sys.argv) < MIN_NARG:
        print('Error syntax. To view help: awdp_ipublic.py -h')
        sys.exit(1)

    # Optional arguments
    if '-h' in argv:
        print(man())            # Return help
        sys.exit(0)

    return argv_d


def main():

    arg_d = argument(sys.argv)

    try:
        my_ip = IPublic.my_ip()
    except urllib2.URLError:
        print('Error. Impossible to connect')
        sys.exit(1)

    print(my_ip)

if __name__ == '__main__':
    main()
