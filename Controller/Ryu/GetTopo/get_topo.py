from ryu.base import app_manager

from ryu.ofproto import ofproto_v1_3

from ryu.controller.handler import set_ev_cls

from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link

class get_topo(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
	def __init__(self, *args, **kwargs):
		super(get_topo, self).__init__(*args, **kwargs)
		self.topology_api_app = self

	@set_ev_cls(event.EventSwitchEnter)
	def get_topology(self, ev):
		switch_list = get_switch(self.topology_api_app, None)
		switches=[switch.dp.id for switch in switch_list]
		links_list = get_link(self.topology_api_app, None)
		links=[(link.src.dpid,link.dst.dpid,{'port':link.src.port_no}) for link in links_list]

		print "switches:%s" % switches
		print "links:%s" % links
