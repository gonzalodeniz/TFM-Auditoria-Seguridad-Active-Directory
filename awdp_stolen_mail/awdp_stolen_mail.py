#!/usr/bin/env python
# coding=utf-8

"""
    File:           awdp_stolen_mail.py
    Version:        1.0
    Date Version:   21/03/2017
    Author:         Gonzalo Déniz

    NAME
        awdp_stolen_mail - Inform if an email account has been stolen.

    SYNOPSIS:

        python awdp_stolen_mail.py mail [ -a ]

    DESCRIPTION
        Stolen_mail uses the API of 'hesidohackeado.com' to check if the mail has been compromised
        in any security breach. The basic usage returns True or False.

    OPTIONS
        mail    The email address.
        -a      Show full information.

    FILES
        awdp_stolen_mail.py          Executable file
        awdp_lib_stolen_mail.py      Class StolenMail, used to connect to the API and show information about stolen mail.
"""
import sys
from awdp_lib_stolen_mail import *


MIN_NARG = 2    # Minimum number of arguments

def man():
    man = '''
        NAME
            awdp_stolen_mail - Inform if an email account has been stolen.

        SYNOPSIS:

            python awdp_stolen_mail.py mail [-a ]

        DESCRIPTION
            Stolen_mail uses the API of 'hesidohackeado.com' to check if the mail has been compromised
            in any security breach. The basic usage returns True or False.

        OPTIONS
            mail    The email address.
            -a      Show full information.

        FILES
            awdp_stolen_mail.py          Executable file
            awdp_lib_stolen_mail.py      Class StolenMail, used to connect to the API.
        '''
    return man

def argument(argv):
    argv_d = {'mail': None,
              'all': False}

    # Minimum number of arguments
    if len(sys.argv) < MIN_NARG:
        print('Error syntax. To view help: awdp_stolen_mail.py -h')
        sys.exit(1)

    # Mandatory arguments
    argv_d['mail'] = argv[1]

    # Optional arguments
    if '-h' in argv:
        print(man())            # Return help
        sys.exit(0)
    elif '-a' in argv:
        argv_d['all'] = True    # Show full information

    return argv_d


def main():

    arg_d = argument(sys.argv)
    try:
        sm = StolenMail(arg_d['mail'])
    except FormatMailError:
        print('Error. Wrong mail format: {0}'.format(arg_d['mail']))
        sys.exit(1)

    # output print
    print(sm.has_been_stolen())

    # if full information
    if (arg_d['all']):
        info_d = sm.info_dic()
        print('Your mail has been: {0}'.format(info_d['status']))
        print('{0} results'.format(info_d['results']))
        print('-' * 10)
        for result in info_d['data']:
            print('Title: {0}'.format(result['title'].encode('utf-8')))
            print('Author: {0}'.format(result['author'].encode('utf-8')))
            print('Leaked: {0}'.format(result['date_leaked'].encode('utf-8')))
            print('Network: {0}'.format(result['source_network'].encode('utf-8')))
            print('--')


if __name__ == '__main__':
    main()
