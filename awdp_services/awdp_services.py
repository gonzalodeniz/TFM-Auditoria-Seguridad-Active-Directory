#!/usr/bin/env python
# coding=utf-8
"""
    File:           awdp_services.py
    Version:        1.0
    Date Version:   01/04/2017
    Author:         Gonzalo Déniz

    NAME
        awdp_services.py - List the services of a machine local or remote

    SYNOPSIS:

        python awdp_services.py -r ip_remote -u user -p pass [-j ]

    DESCRIPTION
        Return list of services en local machine or remote machine. This software use WMI.

    OPTIONS
        -r    Return services remote machine. Remote is an IP address
        -u    User
        -p    Password
        -j    Output in json

    FILES
        awdp_services.py        Executable file
"""
import wmi_client_wrapper as wmi
import sys
import json

class Services(object):
    def __init__(self, ip_remote = None, user = None, password = None):
        self.ip_remote = ip_remote
        self.user = user
        self.password = password


    def print_services(self, services):
        """ Print a summary of services"""
        for s in services:
            try:
                print('Services: {0}'.format(s['Caption']))
                print('Description: {0}'.format(s['Description']))
                print('PathName: {0}'.format(s['PathName']))
                print('State: {0}'.format(s['State']))
                print('--')
            except UnicodeEncodeError:
                pass

    def dic_services(self, services):
        """ Returns a summary of the services. The structure is a dictionary."""
        result = []
        for s in services:
            result.append({'servicio':s['Caption'],
                      'description':s['Description'],
                      'pathname':s['PathName'],
                      'state':s['State']})

        return result

    def json_services(self, services):
        """ Returns a summary of the services. The structure is a json text."""
        result_dict = self.dic_services(services)
        result_json = json.dumps(result_dict, ensure_ascii=False)
        return result_json

    def list_services(self):
        # Local Machine or Remote
        try:
            wmic = wmi.WmiClientWrapper(
                username = self.user,
                password = self.password,
                host = self.ip_remote,
            )
            return wmic.query("SELECT * FROM Win32_Service")

        except AssertionError:
            print('Error: Incorrect param.')
            sys.exit(1)

MIN_ARG = 4

def man():
    man = '''
    NAME
        awdp_services.py - List the services of a machine local or remote

    SYNOPSIS:

        python awdp_services.py -r ip_remote -u user -p pass [-j ]
'''
    return man

def argument(argv):
    argv_d = {'remoto': None,
              'json': False}

    # Return help
    if '-h' in argv:
        print(man())
        sys.exit(0)

    # Minimum number of arguments
    if len(sys.argv) < MIN_ARG:
        print('Error syntax. To view help: awdp_services.py -h')
        sys.exit(1)

    # Optional arguments


    # Mandatory
    if '-r' in argv:
        try:
            p = argv.index('-r')
            argv_d['remoto'] = argv[p+1]
        except IndexError:
            argv_d['remoto'] = None
    # User
    if '-u' in argv:
        try:
            p = argv.index('-u')
            argv_d['user'] = argv[p + 1]
        except IndexError:
            argv_d['user'] = None
    # Password
    if '-p' in argv:
        try:
            p = argv.index('-p')
            argv_d['password'] = argv[p + 1]
        except IndexError:
            argv_d['password'] = None

    # Optional
    # json output
    if '-j' in argv:
        argv_d['json'] = True

    return argv_d

def main():
    try:
        argv = argument(sys.argv)
        s = Services(argv['remoto'], argv['user'], argv['password'])
        result_services = s.list_services()
        # json output
        if argv['json']:
            print s.json_services(result_services)
        # text output
        else:
            s.print_services(result_services)

    except Exception:
        raise

if __name__ == '__main__':
    main()