from awdp_nmap.pyroute2 import TC_H_INGRESS
from awdp_nmap.pyroute2 import nla

parent = TC_H_INGRESS


def fix_msg(msg, kwarg):
    msg['handle'] = 0xffff0000


class options(nla):
        fields = (('value', 'I'), )
