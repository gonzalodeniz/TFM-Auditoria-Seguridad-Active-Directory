#!/usr/bin/env python
# coding=utf-8

"""
    File:           awdp_ad_computers.py
    Version:        1.0
    Date Version:   03/05/2017
    Author:         Gonzalo Déniz

    NAME
        awdp_ad_computers - Shows details of user accounts from a directory in an active directory.

    SYNOPSIS:

        python awdp_ad_computers.py [-h] [-v] [-c file] [-b BASEDN] [-j]


    OPTIONS
        -h, --help                  Show this help message and exit
        -v, --version               Show program's version number and exit
        -c file, --config file      Configuration file. Default = '.\ad.ini'
        -b BASEDN, --basedn BASEDN  Define base DN. ej: -b ou=user,dc=uoc,dc=local. If
                                    it's not defined, is used basedn of file .ini
        -j                          Json export format

    FILES
        awdp_ad_computers.py        Executable file
        awdp_ad_lib.py              Class to handle active directory

    PREREQUISITE
       Install Python-Ldap

    EXAMPLE
       python awdp_ad_computers.py -c ad.ini -b ou=uoc,dc=uoc,dc=local

"""

import sys
import awdp_ad_lib as adlib
import ldap
import ConfigParser
import argparse

VERSION = '1.0'

def to_json(ad_computers):
    json = {'computers': []}
    for ad_computer in ad_computers:
        json['computers'].append({'dn'  :        ad_computer.dn,
                              'name':            ad_computer.name,
                              'date_last_logon': ad_computer.date_last_logon(),
                              'enabled':         ad_computer.is_enabled(),
                              'pwd_required':    ad_computer.is_password_required(),
                              'pwd_expire':      ad_computer.is_password_expire(),
                              'last_bad_logon':  ad_computer.date_last_bad_logon(),
                              'count_bad_logon': ad_computer.count_bad_logon(),
                              'member_of':       ad_computer.memberOf})
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
    argp.add_argument('-j', action='store_true', help='Json export format')
    args = argp.parse_args()

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
                basdn = cfg.get('LDAP', 'basedn')
            else:
                basdn = args.b
        except Exception as e:
            print('Incorrect configuration file: ' + e.message)
            sys.exit(1)

    # Connect LDAP
    try:
        ad = adlib.ADLib(ldap_server, user_admin, pass_admin)
        computers_raw = ad.load_computer(basdn)
        ad_computers = ad.to_adcomputers(computers_raw)

        # Output
        if args.j:
            print(to_json(ad_computers))
        else:
            print('DN' + ' '*44 + 'NAME' + ' '*15 + 'LASTLOGON' + ' '*5 + 'ENABLED'
                  + ' '*5 + 'PASS_REQUIRED' + ' '*3 + 'PASS_EXPIRE' + ' '*3 + 'LAST_BAD_LOGON'
                  + ' '*5 + 'COUNT_BAD_LOGON' + ' '*5 + 'MEMBER_OF')
            for ad_computer in ad_computers:
                print('{0:<45s} {1:<18s} {2:<15s} {3:<15b} {4:<15b} {5:<15b} {6:<16s} {7:<13s} {8:<11s} '.format(ad_computer.dn,
                                                          ad_computer.name,
                                                          ad_computer.date_last_logon(),
                                                          ad_computer.is_enabled(),
                                                          ad_computer.is_password_required(),
                                                          ad_computer.is_password_expire(),
                                                          ad_computer.date_last_bad_logon(),
                                                          ad_computer.count_bad_logon(),
                                                          ad_computer.memberOf))

    except ldap.LDAPError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()