# -*- coding: utf-8 -*-
'''
Generic netlink
===============

Describe
'''
import errno
import logging

from awdp_nmap.pyroute2 import CTRL_CMD_GETFAMILY
from awdp_nmap.pyroute2 import GENL_ID_CTRL
from awdp_nmap.pyroute2 import NETLINK_ADD_MEMBERSHIP
from awdp_nmap.pyroute2 import NETLINK_DROP_MEMBERSHIP
from awdp_nmap.pyroute2 import NLM_F_REQUEST
from awdp_nmap.pyroute2 import NetlinkSocket
from awdp_nmap.pyroute2 import SOL_NETLINK
from awdp_nmap.pyroute2 import ctrlmsg


class GenericNetlinkSocket(NetlinkSocket):
    '''
    Low-level socket interface. Provides all the
    usual socket does, can be used in poll/select,
    doesn't create any implicit threads.
    '''

    mcast_groups = {}

    def bind(self, proto, msg_class, groups=0, pid=None, async=False):
        '''
        Bind the socket and performs generic netlink
        proto lookup. The `proto` parameter is a string,
        like "TASKSTATS", `msg_class` is a class to
        parse messages with.
        '''
        NetlinkSocket.bind(self, groups, pid, async)
        self.marshal.msg_map[GENL_ID_CTRL] = ctrlmsg
        msg = self.discovery(proto)
        self.prid = msg.get_attr('CTRL_ATTR_FAMILY_ID')
        self.mcast_groups = \
            dict([(x.get_attr('CTRL_ATTR_MCAST_GRP_NAME'),
                   x.get_attr('CTRL_ATTR_MCAST_GRP_ID')) for x
                  in msg.get_attr('CTRL_ATTR_MCAST_GROUPS', [])])
        self.marshal.msg_map[self.prid] = msg_class

    def add_membership(self, group):
        self.setsockopt(SOL_NETLINK,
                        NETLINK_ADD_MEMBERSHIP,
                        self.mcast_groups[group])

    def drop_membership(self, group):
        self.setsockopt(SOL_NETLINK,
                        NETLINK_DROP_MEMBERSHIP,
                        self.mcast_groups[group])

    def discovery(self, proto):
        '''
        Resolve generic netlink protocol -- takes a string
        as the only parameter, return protocol description
        '''
        msg = ctrlmsg()
        msg['cmd'] = CTRL_CMD_GETFAMILY
        msg['version'] = 1
        msg['attrs'].append(['CTRL_ATTR_FAMILY_NAME', proto])
        msg['header']['type'] = GENL_ID_CTRL
        msg['header']['flags'] = NLM_F_REQUEST
        msg['header']['pid'] = self.pid
        msg.encode()
        self.sendto(msg.data, (0, 0))
        msg = self.get()[0]
        err = msg['header'].get('error', None)
        if err is not None:
            if hasattr(err, 'code') and err.code == errno.ENOENT:
                logging.error('Generic netlink protocol %s not found' % proto)
                logging.error('Please check if the protocol module is loaded')
            raise err
        return msg
