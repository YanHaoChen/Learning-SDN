from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import lacplib
from ryu.lib.dpid import str_to_dpid
from ryu.lib.packet import packet, ethernet

class SimpleSwitchLACP13(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
	_CONTEXTS = {'lacplib': lacplib.LacpLib}

	def __init__(self, *args, **kwargs):
		super(SimpleSwitchLACP13, self).__init__(*args, **kwargs)
		self.mac_to_port = {}
		self._lacp = kwargs['lacplib']
		self._lacp.add(dpid=str_to_dpid('0000000000000001'),ports=[1, 2])

	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		datapath = ev.msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		match = parser.OFPMatch()
		actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,ofproto.OFPCML_NO_BUFFER)]
		self.add_flow(datapath, 0, match, actions)

	def add_flow(self, datapath, priority, match, actions):
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
		mod = parser.OFPFlowMod(datapath=datapath, priority=priority,match=match,instructions=inst)
		datapath.send_msg(mod)

	def del_flow(self, datapath, match):
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		mod = parser.OFPFlowMod(datapath = datapath,
								command = ofproto.OFPFC_DELETE,
								out_port = ofproto.OFPP_ANY,
								out_group = ofproto.OFPG_ANY,
								match = match)
		datapath.send_msg(mod)

	@set_ev_cls(lacplib.EventPacketIn, MAIN_DISPATCHER)
	def _packet_in_handler(self, ev):
		msg = ev.msg
		datapath = msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		in_port = msg.match['in_port']

		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocols(ethernet.ethernet)[0]

		dst = eth.dst
		src = eth.src

		dpid = datapath.id
		self.mac_to_port.setdefault(dpid, {})
		self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
		
		self.mac_to_port[dpid][src] = in_port

		if dst in self.mac_to_port[dpid]:
			out_port = self.mac_to_port[dpid][dst]
		else:
			out_port = ofproto.OFPP_FLOOD

		actions = [parser.OFPActionOutput(out_port)]

		if out_port != ofproto.OFPP_FLOOD:
			match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
			self.add_flow(datapath, 1, match, actions)

		data = None
		if msg.buffer_id == ofproto.OFP_NO_BUFFER:
			data = msg.data

		out = parser.OFPPacketOut(datapath = datapath,
									buffer_id = msg.buffer_id,
									in_port = in_port,
									actions = actions,
									data = data )
		datapath.send_msg(out)

	@set_ev_cls(lacplib.EventSlaveStateChanged, MAIN_DISPATCHER)
	def _slave_state_changed_handler(self, ev):
		datapath = ev.datapath
		dpid = datapath.id
		port_no = ev.port
		enabled = ev.enabled
		self.logger.info("slave state changed port: %d enabled: %s", port_no, enabled)
		if dpid in self.mac_to_port:
			for mac in self.mac_to_port[dpid]:
				match = datapath.ofproto_parser.OFPMatch(eth_dst=mac)
				self.del_flow(datapath, match)
			del self.mac_to_port[dpid]
		self.mac_to_port.setdefault(dpid, {})
