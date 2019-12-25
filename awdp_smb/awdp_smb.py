#!/usr/bin/env python
# coding=utf-8
"""
    File:           awdp_smb.py
    Version:        1.0
    Date Version:   21/03/2017
    Author:         Gonzalo Déniz

    NAME
        awdp_smb - Discover shared network folders

    SYNOPSIS:
        python awdp_smb.py -r ip_remote -s hostname_remote [ -u user] [ -p password] [ -j ]

    DESCRIPTION
        For a computer with windows determine if it shares some network folder.

    OPTIONS
        -r ip_remote            Ip windows server.
        -s hostname_remote      Remote computer name
        -u user                 User of remote machine
        -p password

    FILES
        awdp_smb.py          Executable file

    PREREQUISITE
       Install PySMB

    EXAMPLE
        python awdp_smb.py -r 192.168.85.141 -s SRVDELTA1 -u administrador -p password -j

"""
from smb.SMBConnection import SMBConnection
import smb
import sys
import socket
import json
import os

MIN_NARG = 5    # Minimum number of arguments


def man():
    man_txt = '''
    NAME
        awdp_smb - Discover shared network folders

    SYNOPSIS:
        python awdp_smb.py -r ip_remote -s hostname_remote [ -u user] [ -p password] [ -j ]

    DESCRIPTION
        For a computer with windows determine if it shares some network folder.

    OPTIONS
        -r ip_remote            Ip windows server.
        -s hostname_remote      Remote computer name
        -u user                 User in remote
        -p password             User's password
        -j                      Json output

    FILES
        awdp_smb.py          Executable file

    PREREQUISITE
       Install PySMB

    EXAMPLE
        python awdp_smb.py -r 192.168.85.141 -s SRVDELTA1 -u administrador -p password -j
        '''
    return man_txt


def argument(argv):
    ''' Arguments management'''
    argv_d = {'ip_remote': None,
              'hostname': False,
              'user': '',
              'pwd': '',
              'json': False}

    # Optional arguments
    if '-h' in argv:
        print(man())  # Return help
        sys.exit(0)

    # Minimum number of arguments
    if len(sys.argv) < MIN_NARG:
        print('Error syntax. To view help: awdp_smb.py -h')
        sys.exit(1)

    # Mandatory arguments
    if '-r' in argv:
        pos = argv.index('-r')
        argv_d['ip_remote'] = argv[pos + 1]
    else:
        print('Error syntax. To view help: awdp_smb.py -h')
        sys.exit(1)

    # Remote machine
    if '-s' in argv:
        pos = argv.index('-s')
        argv_d['hostname'] = argv[pos + 1]
    else:
        print('Error syntax. To view help: awdp_smb.py -h')
        sys.exit(1)

    # Optional arguments
    # Username
    if '-u' in argv:
        pos = argv.index('-u')
        argv_d['user'] = argv[pos + 1]
    # Password
    if '-p' in argv:
        pos = argv.index('-p')
        argv_d['pwd'] = argv[pos + 1]
    # Json output
    if '-j' in argv:
        argv_d['json'] = True

    return argv_d


def get_shared_folders(arg_d):
    ''' Return the shared folders. '''
    try:
        # Search type authenticated or not
        if arg_d['user'] == '':
            authenticated = False
        else:
            authenticated = True

        # Connection
        s = SMBConnection(arg_d['user'],
                          arg_d['pwd'],
                          '',
                          arg_d['hostname'],
                          use_ntlm_v2=True)
        s.connect(arg_d['ip_remote'], 139)

        # Output
        result_json = {'shared': []}
        for s_i in s.listShares():
            result_json['shared'].append({'name': s_i.name,
                                         'authenticated':authenticated})
        return result_json
    except smb.base.NotReadyError:
        raise


def main():

    try:
        arg_d = argument(sys.argv)
        result_json = get_shared_folders(arg_d)

        # Output
        for rj in result_json['shared']:
            print('Folder: {0:<15}\tAuthenticated:{1}'.format(rj['name'], rj['authenticated']))

        # Writing json file
        if arg_d['json']:
            with open('awdp_smp_results.json', 'w') as outfile:
                json.dump(result_json, outfile)
                print('Json file created in: ' + os.path.realpath(outfile.name))

    except socket.error as e:
        print('Error:' + e.strerror)
        sys.exit(1)
    except smb.base.NotConnectedError:
        print('Error: hostname {0} unknow'.format(arg_d['user']))
        sys.exit(1)
    except smb.base.NotReadyError:
        print('Authentication is required')
        sys.exit()

if __name__ == '__main__':
    main()
