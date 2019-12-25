from awdp_nmap.pyroute2 import nlmsg


class errmsg(nlmsg):
    '''
    Custom message type

    Error ersatz-message
    '''
    fields = (('code', 'i'), )
