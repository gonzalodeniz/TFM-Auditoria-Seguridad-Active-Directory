from awdp_nmap.pyroute2 import Marshal
from awdp_nmap.pyroute2 import fibmsg
from awdp_nmap.pyroute2 import ifaddrmsg
from awdp_nmap.pyroute2 import ifinfmsg
from awdp_nmap.pyroute2 import ndmsg
from awdp_nmap.pyroute2 import ndtmsg
from awdp_nmap.pyroute2 import rtmsg
from awdp_nmap.pyroute2 import rtnl
from awdp_nmap.pyroute2 import tcmsg


class MarshalRtnl(Marshal):
    msg_map = {rtnl.RTM_NEWLINK: ifinfmsg,
               rtnl.RTM_DELLINK: ifinfmsg,
               rtnl.RTM_GETLINK: ifinfmsg,
               rtnl.RTM_SETLINK: ifinfmsg,
               rtnl.RTM_NEWADDR: ifaddrmsg,
               rtnl.RTM_DELADDR: ifaddrmsg,
               rtnl.RTM_GETADDR: ifaddrmsg,
               rtnl.RTM_NEWROUTE: rtmsg,
               rtnl.RTM_DELROUTE: rtmsg,
               rtnl.RTM_GETROUTE: rtmsg,
               rtnl.RTM_NEWRULE: fibmsg,
               rtnl.RTM_DELRULE: fibmsg,
               rtnl.RTM_GETRULE: fibmsg,
               rtnl.RTM_NEWNEIGH: ndmsg,
               rtnl.RTM_DELNEIGH: ndmsg,
               rtnl.RTM_GETNEIGH: ndmsg,
               rtnl.RTM_NEWQDISC: tcmsg,
               rtnl.RTM_DELQDISC: tcmsg,
               rtnl.RTM_GETQDISC: tcmsg,
               rtnl.RTM_NEWTCLASS: tcmsg,
               rtnl.RTM_DELTCLASS: tcmsg,
               rtnl.RTM_GETTCLASS: tcmsg,
               rtnl.RTM_NEWTFILTER: tcmsg,
               rtnl.RTM_DELTFILTER: tcmsg,
               rtnl.RTM_GETTFILTER: tcmsg,
               rtnl.RTM_NEWNEIGHTBL: ndtmsg,
               rtnl.RTM_GETNEIGHTBL: ndtmsg,
               rtnl.RTM_SETNEIGHTBL: ndtmsg}

    def fix_message(self, msg):
        # FIXME: pls do something with it
        try:
            msg['event'] = rtnl.RTM_VALUES[msg['header']['type']]
        except:
            pass
