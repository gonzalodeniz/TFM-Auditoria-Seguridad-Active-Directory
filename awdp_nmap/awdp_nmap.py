#!/usr/bin/env python
# coding=utf-8

"""
    File:           awdp_nmap.py
    Version:        1.1
    Date Version:   08/04/2017
    Author:         Gonzalo Déniz

    NAME
        awdp_nmap.py - Network discovery

    SYNOPSIS:

        python awdp_nmap.py -t target [-p ports]

    DESCRIPTION
        Using nmap, returns hosts address and open ports

    OPTIONS
        -t    If the target is only host, then write only the ip. Ex.: 10.0.0.1
              If the target is a network, then write the network address. Ex.192.168.1.0/24
        -p    The range of ports to be checked if they are open. Ex. 22-1024

    FILES
        awdp_nmap.py        Executable file

    PACKAGES
        python-nmap         Is a python library which helps in using nmap port scanner.
        pyroute2            Is a pure Python netlink and Linux network configuration library.
    
    EXAMPLE
        sudo python awdp_nmap.py -t 192.168.85.141 -p 1-1024
        sudo python awdp_nmap.py -t 192.168.85.0/24 -p 22
"""

import json
import os
import sys

import ipaddress
import nmap

try:
    from pyroute2 import IPRoute
except ImportError:
    pass

class NetInfo(object):


    def __get_ip_local_windows(self):
        """ Google Code"""
        from ctypes import Structure, windll, sizeof
        from ctypes import POINTER, byref
        from ctypes import c_ulong, c_uint, c_ubyte, c_char
        MAX_ADAPTER_DESCRIPTION_LENGTH = 128
        MAX_ADAPTER_NAME_LENGTH = 256
        MAX_ADAPTER_ADDRESS_LENGTH = 8

        class IP_ADDR_STRING(Structure):
            pass

        LP_IP_ADDR_STRING = POINTER(IP_ADDR_STRING)
        IP_ADDR_STRING._fields_ = [
            ("next", LP_IP_ADDR_STRING),
            ("ipAddress", c_char * 16),
            ("ipMask", c_char * 16),
            ("context", c_ulong)]

        class IP_ADAPTER_INFO(Structure):
            pass

        LP_IP_ADAPTER_INFO = POINTER(IP_ADAPTER_INFO)
        IP_ADAPTER_INFO._fields_ = [
            ("next", LP_IP_ADAPTER_INFO),
            ("comboIndex", c_ulong),
            ("adapterName", c_char * (MAX_ADAPTER_NAME_LENGTH + 4)),
            ("description", c_char * (MAX_ADAPTER_DESCRIPTION_LENGTH + 4)),
            ("addressLength", c_uint),
            ("address", c_ubyte * MAX_ADAPTER_ADDRESS_LENGTH),
            ("index", c_ulong),
            ("type", c_uint),
            ("dhcpEnabled", c_uint),
            ("currentIpAddress", LP_IP_ADDR_STRING),
            ("ipAddressList", IP_ADDR_STRING),
            ("gatewayList", IP_ADDR_STRING),
            ("dhcpServer", IP_ADDR_STRING),
            ("haveWins", c_uint),
            ("primaryWinsServer", IP_ADDR_STRING),
            ("secondaryWinsServer", IP_ADDR_STRING),
            ("leaseObtained", c_ulong),
            ("leaseExpires", c_ulong)]
        GetAdaptersInfo = windll.iphlpapi.GetAdaptersInfo
        GetAdaptersInfo.restype = c_ulong
        GetAdaptersInfo.argtypes = [LP_IP_ADAPTER_INFO, POINTER(c_ulong)]
        adapterList = (IP_ADAPTER_INFO * 10)()
        buflen = c_ulong(sizeof(adapterList))
        rc = GetAdaptersInfo(byref(adapterList[0]), byref(buflen))
        if rc == 0:
            for a in adapterList:
                adNode = a.ipAddressList
                while True:
                    ipAddr = adNode.ipAddress
                    if ipAddr:
                        yield ipAddr
                    adNode = adNode.next
                    if not adNode:
                            break

    def __get_all_ip_local_windows(self):
        ip_local = []
        for addr in self.__get_ip_local_windows():
            if addr <> '0.0.0.0':
                ip_local.append(addr)
        return ip_local

    def get_all_ip_local(self):
        try:
            """ Return list of IPv4 local except 127.0.0.1"""
            ip_list = []
            ip = IPRoute()
            for x in ip.get_addr():
                if not x.get_attr('IFA_ADDRESS') == '127.0.0.1' and x['prefixlen'] <= 32:
                    ip_list = [x.get_attr('IFA_ADDRESS') + '/' + str(x['prefixlen'])]
            ip.close()
        except NameError:
            ip_list = ['127.0.0.1']
        return ip_list

    def get_network(self, ip_mask):
        """ Return network address of a ip/mask"""
        ip, mask = ip_mask.split('/')
        alt_ip = ipaddress.ip_network((unicode(ip_mask)), strict=False)
        return alt_ip.network_address

MIN_NARG = 2


def man():
    man = '''NAME
    awdp_nmap.py - Network discovery

    SYNOPSIS:

        python awdp_nmap.py -t target [-p ports]

    DESCRIPTION
        Using nmap, returns hosts address and open ports

    OPTIONS
        -t    If the target is only host, then write only the ip. Ex.: 10.0.0.1
              If the target is a network, then write the network address. Ex.192.168.1.0/24
        -p    The range of ports to be checked if they are open. Ex. 22-1024

    FILES
        awdp_nmap.py        Executable file

    PACKAGES
        python-nmap         Is a python library which helps in using nmap port scanner.
        pyroute2            Is a pure Python netlink and Linux network configuration library.
    
    EXAMPLE
        sudo python awdp_nmap.py -t 192.168.85.141 -p 1-1024
        sudo python awdp_nmap.py -t 192.168.85.0/24 -p 22
    '''
    return man


def argument(argv):
    argv_d = {'target': '127.0.0.1',
              'port': '1-1023',
              'json': False}

    # Minimum number of arguments
    if len(sys.argv) < MIN_NARG:
        print('Error syntax. To view help: awdp_nmap.py -h')
        sys.exit(1)

    # Optional arguments
    # Return help
    if '-h' in argv:
        print(man())
        sys.exit(0)

    # Current net
    if '-c' in argv:
        argv_d['target'] = 'current_net'

    # Target (host or net)
    if '-t' in argv:
        pos = argv.index('-t')
        argv_d['target'] = argv[pos+1]

    # Port
    if '-p' in argv:
        pos = argv.index('-p')
        argv_d['port'] = argv[pos+1]

    if '-j' in argv:
        argv_d['json'] = True


    return argv_d

def main():
    try:
        argv = argument(sys.argv)
        nm = nmap.PortScanner()
        target = None

        if argv['target'] == 'current_net':
            ni = NetInfo()
            argv['target'] = ni.get_all_ip_local()
        target = argv['target']
        port = argv['port']

        if target is not list:
            target = [target]

        for ip_mask in target:
            nm.scan(ip_mask, port, '-O -sV')

            result_json = {'nmap': {'command': nm.command_line(),
                                    'hosts': []}}
            print(nm.command_line())

            # All Hosts
            for host in nm.all_hosts():
                print('----------------------------------------------------')
                print('Host : %s (%s)' % (host, nm[host].hostname()))
                print('State : %s' % nm[host].state())

                # Operating System Information
                so_info = ''
                try:
                    osclass = nm[host]['osmatch'][0]['osclass'][0]
                    so_info += str(osclass['osfamily']) + ' '
                    so_info += str(osclass['osgen']) + '; '
                    so_info += str(osclass['cpe'][0])
                    print(so_info)
                except IndexError:
                    print('No operating system information')


                host_json = {   'host': host,
                                'state':nm[host].state(),
                                'so': so_info,
                                'protocols': []}

                # Protocol Information
                for proto in nm[host].all_protocols():
                    print('----------')
                    print('Protocol : %s' % proto)

                    proto_json = {'protocol': proto,
                                  'ports': []}
                    # Ports Information
                    lport = nm[host][proto].keys()
                    lport.sort()
                    for port in lport:
                        print ('port : %s\tstate : %s\tservice : %s' % (port,
                                                                        nm[host][proto][port]['state'],
                                                                        nm[host][proto][port]['name'] + ' ' + nm[host][proto][port]['version']))
                        port_json = {'port':    port,
                                     'state':   nm[host][proto][port]['state'],
                                     'name':    nm[host][proto][port]['name'],
                                     'version': nm[host][proto][port]['version']}

                        # Making json dictionary
                        proto_json['ports'].append(port_json)
                    host_json['protocols'].append(proto_json)
                result_json['nmap']['hosts'].append(host_json)

            # Writing json file
            if argv['json']:
                with open('awdp_nmap_results.json', 'w') as outfile:
                    json.dump(result_json, outfile)
                    print('Json file created in: ' + os.path.realpath(outfile.name))

    except nmap.nmap.PortScannerError as e:
        print('Nmap program was not found in path.')
        print(e.value)

if __name__ == '__main__':
    main()