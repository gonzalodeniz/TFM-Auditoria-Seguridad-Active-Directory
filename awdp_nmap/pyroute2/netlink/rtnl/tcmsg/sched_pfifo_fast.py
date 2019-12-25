from awdp_nmap.pyroute2 import TC_H_ROOT
from awdp_nmap.pyroute2 import nla

parent = TC_H_ROOT


class options(nla):
        fields = (('bands', 'i'),
                  ('priomap', '16B'))
