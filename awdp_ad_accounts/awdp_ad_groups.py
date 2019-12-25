#!/usr/bin/env python
# coding=utf-8

"""
    File:           awdp_ad_group.py
    Version:        1.0
    Date Version:   07/05/2017
    Author:         Gonzalo Déniz

    NAME
        awdp_ad_groups - Shows details of groups from a directory in an active directory.

    SYNOPSIS:

        python awdp_ad_groups.py [-h] [-v] [-c file] [-b BASEDN] [-j]


    OPTIONS
        -h, --help                  Show this help message and exit
        -v, --version               Show program's version number and exit
        -c file, --config file      Configuration file
        -b BASEDN, --basedn BASEDN  Define base DN. ej: -b ou=user,dc=uoc,dc=local. If
                                    it's not defined, is used basedn of file .ini
        -j                          Json export format

    FILES
        awdp_ad_groups.py             Executable file
        awdp_ad_lib.py              Class to handle active directory

    PREREQUISITE
       Install Python-Ldap

    EXAMPLE
       python awdp_ad_groups.py -c ad.ini -b ou=uoc,dc=uoc,dc=local

"""

import sys
import awdp_ad_lib as adlib
import ldap
import ConfigParser
import argparse

VERSION = '1.0'

def to_json(ad_groups):
    json = {'groups': []}
    for ad_group in ad_groups:
        json['groups'].append({'dn'  :                  ad_group.dn,
                              'sAMAccountName':         ad_group.sAMAccountName,
                              'adminCount':             ad_group.adminCount,
                              'isCriticalSystemObject': ad_group.isCriticalSystemObject,
                              'description':            ad_group.description,
                              'member':                 ad_group.member,
                              'member_of':              ad_group.memberOf})

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
                basedn = cfg.get('LDAP', 'basedn')
            else:
                basedn = args.b
        except Exception as e:
            print('Incorrect configuration file: ' + e.message)
            sys.exit(1)

    # Connect LDAP
    try:
        ad = adlib.ADLib(ldap_server, user_admin, pass_admin)
        group_raw = ad.load_groups(basedn)
        ad_groups = ad.to_adgroups(group_raw)

        # Output
        if args.j:
            print(to_json(ad_groups))
        else:
            for ad_group in ad_groups:
                print('DN:          {0} \n'
                      'NAME:        {1} \n'
                      'ADMIN COUNT: {2} \n'
                      'IS CRITICAL: {3} \n'
                      'DESCRIPTION: {4} \n'
                      'MEMBER:      {5} \n'
                      'MEMBER OF:   {6} \n'
                      .format(ad_group.dn,
                              ad_group.sAMAccountName,
                              ad_group.adminCount,
                              ad_group.isCriticalSystemObject,
                              ad_group.description,
                              ad_group.member,
                              ad_group.memberOf
                              ))

    except ldap.LDAPError as e:
        print(e)
        sys.exit(1)



if __name__ == "__main__":
    main()