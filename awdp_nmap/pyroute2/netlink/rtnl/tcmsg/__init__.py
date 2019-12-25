import types

from awdp_nmap.pyroute2 import cls_fw
from awdp_nmap.pyroute2 import cls_u32
from awdp_nmap.pyroute2 import nla
from awdp_nmap.pyroute2 import nlmsg
from awdp_nmap.pyroute2 import sched_bpf
from awdp_nmap.pyroute2 import sched_choke
from awdp_nmap.pyroute2 import sched_clsact
from awdp_nmap.pyroute2 import sched_codel
from awdp_nmap.pyroute2 import sched_drr
from awdp_nmap.pyroute2 import sched_fq_codel
from awdp_nmap.pyroute2 import sched_hfsc
from awdp_nmap.pyroute2 import sched_htb
from awdp_nmap.pyroute2 import sched_ingress
from awdp_nmap.pyroute2 import sched_netem
from awdp_nmap.pyroute2 import sched_pfifo_fast
from awdp_nmap.pyroute2 import sched_plug
from awdp_nmap.pyroute2 import sched_sfq
from awdp_nmap.pyroute2 import sched_tbf
from awdp_nmap.pyroute2 import sched_template

plugins = {'plug': sched_plug,
           'sfq': sched_sfq,
           'clsact': sched_clsact,
           'codel': sched_codel,
           'fq_codel': sched_fq_codel,
           'hfsc': sched_hfsc,
           'htb': sched_htb,
           'bpf': sched_bpf,
           'tbf': sched_tbf,
           'netem': sched_netem,
           'fw': cls_fw,
           'u32': cls_u32,
           'ingress': sched_ingress,
           'pfifo_fast': sched_pfifo_fast,
           'choke': sched_choke,
           'drr': sched_drr}


class tcmsg(nlmsg):

    prefix = 'TCA_'

    fields = (('family', 'B'),
              ('pad1', 'B'),
              ('pad2', 'H'),
              ('index', 'i'),
              ('handle', 'I'),
              ('parent', 'I'),
              ('info', 'I'))

    nla_map = (('TCA_UNSPEC', 'none'),
               ('TCA_KIND', 'asciiz'),
               ('TCA_OPTIONS', 'get_options'),
               ('TCA_STATS', 'stats'),
               ('TCA_XSTATS', 'get_xstats'),
               ('TCA_RATE', 'hex'),
               ('TCA_FCNT', 'hex'),
               ('TCA_STATS2', 'get_stats2'),
               ('TCA_STAB', 'hex'))

    class stats(nla):
        fields = (('bytes', 'Q'),
                  ('packets', 'I'),
                  ('drop', 'I'),
                  ('overlimits', 'I'),
                  ('bps', 'I'),
                  ('pps', 'I'),
                  ('qlen', 'I'),
                  ('backlog', 'I'))

    def get_plugin(self, plug, *argv, **kwarg):
        # get the plugin name
        kind = self.get_attr('TCA_KIND')
        # get the plugin implementation or the default one
        p = plugins.get(kind, sched_template)
        # get the interface
        interface = getattr(p,
                            plug,
                            getattr(sched_template, plug))
        # if it is a method, run and return the result
        if isinstance(interface, types.FunctionType):
            return interface(self, *argv, **kwarg)
        else:
            return interface

    @staticmethod
    def get_stats2(self, *argv, **kwarg):
        return self.get_plugin('stats2', *argv, **kwarg)

    @staticmethod
    def get_xstats(self, *argv, **kwarg):
        return self.get_plugin('stats', *argv, **kwarg)

    @staticmethod
    def get_options(self, *argv, **kwarg):
        return self.get_plugin('options', *argv, **kwarg)
