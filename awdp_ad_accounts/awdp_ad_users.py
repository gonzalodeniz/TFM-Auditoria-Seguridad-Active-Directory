#!/usr/bin/env python
# coding=utf-8

"""
    File:           awdp_ad_users.py
    Version:        1.0
    Date Version:   03/05/2017
    Author:         Gonzalo Déniz

    NAME
        awdp_ad_users - Shows details of user accounts from a directory in an active directory.

    SYNOPSIS:

        python awdp_ad_users.py [-h] [-v] [-c file] [-b BASEDN] [-j]


    OPTIONS
        -h, --help                  Show this help message and exit
        -v, --version               Show program's version number and exit
        -c file, --config file      Configuration file
        -b BASEDN, --basedn BASEDN  Define base DN. ej: -b ou=user,dc=uoc,dc=local. If
                                    it's not defined, is used basedn of file .ini
        -j                          Json export format

    FILES
        awdp_ad_user.py             Executable file
        awdp_ad_lib.py              Class to handle active directory

    PREREQUISITE
       Install Python-Ldap

    EXAMPLE
       python awdp_ad_users.py -c ad.ini -b ou=uoc,dc=uoc,dc=local

"""

import ConfigParser
import argparse
import ldap
import sys

import awdp_ad_lib as adlib
import logeasy

VERSION = '1.0'

def to_json(ad_users):
    json = {'users': []}
    for ad_user in ad_users:
        json['users'].append({'dn'  :            ad_user.dn,
                              'name':            ad_user.name,
                              'date_expires':    ad_user.date_expires(),
                              'date_last_logon': ad_user.date_last_logon(),
                              'enabled':         ad_user.is_enabled(),
                              'pwd_required':    ad_user.is_password_required(),
                              'pwd_expire':      ad_user.is_password_expire(),
                              'last_bad_logon':  ad_user.date_last_bad_logon(),
                              'count_bad_logon': ad_user.count_bad_logon(),
                              'member_of': ad_user.memberOf})

    return json


def main():

    # Arguments
    argp = argparse.ArgumentParser(
        version = VERSION,
        description = 'Active Directory Audit Help Tool'
    )
    argp.add_argument('-c', '--config', type=str, metavar='file', default='ad.ini', help='Configuration file')
    argp.add_argument('-b', '--basedn', type=str, metavar='BASEDN',
                      dest='b', action='store',
                      help='Define base DN. ej: -b ou=user,dc=uoc,dc=local. '
                           'If it\'s not defined, is used basedn of file .ini')
    argp.add_argument('-j',     action='store_true', help='Json export format')
    argp.add_argument('-d', action='store_true', help='Debug mode')
    args = argp.parse_args()

    # Debug mode
    flog = None
    if args.d:
        flog = logeasy.file_log(filename='awdp_debug.log',
                                name='awdp_debug',
                                filemode='w',
                                level=logeasy.logging.DEBUG,
                                format=logeasy.F_DEBUG)
        flog.debug('Starting debug')
        flog.debug('Arguments: \n' + str(sys.argv) + '\n' +str(args) + '\n')


    # File Configuration
    cfg = ConfigParser.ConfigParser()
    if not cfg.read([args.config]):
        print('Configuration file no found')
        sys.exit(1)
    else:
        try:
            user_admin   = cfg.get('LDAP', 'user_admin')
            pass_admin   = cfg.get('LDAP', 'pass_admin')
            ldap_server  = cfg.get('LDAP', 'ldap_server')
            if args.b is None:
                basedn_user = cfg.get('LDAP', 'basedn')
            else:
                basedn_user = args.b

            # Debug mode
            if args.d:
                fconf = open(args.config, 'r')
                flog.debug('File ' + args.config + ':\n' + fconf.read() + '\n')
                fconf.close()
        except Exception as e:
            print('Incorrect configuration file: ' + e.message)
            if args.d:
                flog.exception('Incorrect configuration file: ' + e.message)
            sys.exit(1)

    # Connect LDAP
    try:
        ad = adlib.ADLib(ldap_server, user_admin, pass_admin, flog)
        users_raw = ad.load_users(basedn_user)
        ad_users = ad.to_adusers(users_raw)

        # Output
        if args.j:
            json_txt = to_json(ad_users)
            print(json_txt)
            # Debug mode
            if args.d:
                flog.debug('Printing JSON: \n' + str(json_txt))
        else:
            print('DN' + ' '*44 + 'NAME' + ' '*7 + 'EXPIRE' + ' '*15 + 'LASTLOGON' + ' '*5 + 'ENABLED'
                  + ' '*5 + 'PASS_REQUIRED' + ' '*3 + 'PASS_EXPIRE' + ' '*3 + 'LAST_BAD_LOGON'
                  + ' '*5 + 'COUNT_BAD_LOGON' + ' '*5 + 'MEMBERS OF')
            for ad_user in ad_users:
                print('{0:<45s} {1:<10s} {2:<20s} {3:<15s} {4:<15b} {5:<14b} {6:<11b} {7:<23s} {8:<10s} {9:<10s}'
                      .format(ad_user.dn, ad_user.name,
                              ad_user.date_expires(),
                              ad_user.date_last_logon(),
                              ad_user.is_enabled(),
                              ad_user.is_password_required(),
                              ad_user.is_password_expire(),
                              ad_user.date_last_bad_logon(),
                              ad_user.count_bad_logon(),
                              ad_user.memberOf))
                # Debug mode
                if args.d:
                    flog.debug('Printing: ' + ad_user.dn)

    except ldap.LDAPError as e:
        if args.d:
            flog.exception('LDAP Error: ' + str(e.message))
        print(e)
        sys.exit(1)



if __name__ == "__main__":
    main()