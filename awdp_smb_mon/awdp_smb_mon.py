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
        -s hostname_remote      Remot computer name

    FILES
        awdp_smb.py          Executable file

    PREREQUISITE
       Install PySMB
    EXAMPLE:
        awdp_smb_mon.py -r 192.168.85.141 -s uocpc -sr tmp -path \\ -u Administrator -p password

"""


from smb.SMBConnection import SMBConnection
import smb
import sys
import socket
import tempfile
import json
import os
import awdp_lib_smb_mon as alsm


MIN_NARG = 5    # Minimum number of arguments

def man():
    man = '''
    NAME
        awdp_smb_mon - Discover shared network folders

    SYNOPSIS:

        python awdp_smb_mon.py -r ip_remote -s hostname_remote -sr shared_resource -path path [ -u user] [ -p password] [ -j ]

    DESCRIPTION
        For a computer with windows determine if it shares some network folder.

    OPTIONS
        -r ip_remote            Ip windows server.
        -s hostname_remote      Remote computer name
        -u user                 User in remote
        -p password             User's password
        -sr shared_resource
        -path path              Path in resource
        -j                      Json output

    FILES
        awdp_smb.py          Executable file

    PREREQUISITE
       Install PySMB
    
    EXAMPLE:
        awdp_smb_mon.py -r 192.168.85.141 -s uocpc -sr tmp -path \\ -u Administrator -p password
        '''
    return man

def argument(argv):
    argv_d = {'ip_remote': None,
              'hostname': False,
              'user': '',
              'pwd': '',
              'resource':'',
              'path':'',
              'json': False}

    # Help
    if '-h' in argv:
        print(man())            # Return help
        sys.exit(0)

    # Minimum number of arguments
    if len(sys.argv) < MIN_NARG:
        print('Error syntax. To view help: awdp_smb_mon.py -h')
        sys.exit(1)

    # Mandatory arguments
    try:
        pos = argv.index('-r')
        argv_d['ip_remote'] = argv[pos + 1]

        pos = argv.index('-s')
        argv_d['hostname'] = argv[pos + 1]

        pos = argv.index('-sr')
        argv_d['resource'] = argv[pos + 1]

        pos = argv.index('-path')
        argv_d['path'] = argv[pos + 1]

    except ValueError:
        print('Error syntax. To view help: awdp_smb.py -h')
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


def write_json(ip_remote, files_dict):
    '''write in register file'''
    f = open('awdp_smb_mon_register/' + ip_remote + '.json', 'w')
    json.dump(files_dict, f)
    f.close()

def read_json(ip_remote):
    try:
        '''Read json register in file'''
        f = open('awdp_smb_mon_register/' + ip_remote + '.json', 'r')
        dict = json.load(f)
        return dict
    except IOError:
        return {}

def new_files(ip_remote, files_dct):
    ''' return the new files in remote machine'''
    old_files_dct = read_json(ip_remote)
    shared_resource = files_dct[ip_remote].keys()[0]
    if old_files_dct == {}:
        return files_dct[ip_remote][shared_resource]
    else:
        files_old_lst = old_files_dct[ip_remote][shared_resource]
        files_new_lst = files_dct[ip_remote][shared_resource]
        return list(set(files_new_lst) - set(files_old_lst))

def main():
    try:
        arg_d = argument(sys.argv)

        s = alsm.SmbMon(arg_d['ip_remote'], arg_d['hostname'], arg_d['user'], arg_d['pwd'])
        files_dict = s.get_files_dict(arg_d['resource'], arg_d['path'])
        new_files_lst = new_files(arg_d['ip_remote'], files_dict)
        write_json(arg_d['ip_remote'], files_dict)
        if arg_d['json']:
            print(str(s.make_json(arg_d['resource'], arg_d['path'])))

        print('\nFiles new: ' + str(new_files_lst))


    except socket.error as e:
        print('Error:' + e.strerror)
        sys.exit(1)
    except smb.base.NotConnectedError:
        print('Error: hostname {0} unknow'.format(arg_d['user']))
        sys.exit(1)
    except smb.base.NotReadyError:
        print('Authentication is required')
        raise
        sys.exit()

if __name__ == '__main__':
    main()
