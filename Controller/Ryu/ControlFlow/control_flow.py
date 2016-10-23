from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_0

from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls


class control_flow (app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
	def __init__(self, *args, **kwargs):
		super(control_flow, self).__init__(*args, **kwargs)

	def add_flow(self, dp, match=None, inst=[], table=0, priority=32768):
		ofp = dp.ofproto
		ofp_parser = dp.ofproto_parser

		buffer_id = ofproto.OFP_NO_BUFFER

		mod = ofp_parser.OFPFlowMod(
			datapath=dp, cookie=0, cookie_mask=0, table_id,
			command=ofp.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
			priority=priority, buffer_id=buffer_id,
			out_port=ofp.OFPP_ANY, out_group=ofp.OFPG_ANY,
			flags=0, match=match, intstructions=inst)

		dp.send_msg(mod)

	def del_flow(self, dp, match, table):
		ofp = dp.ofproto
		ofp_parser = dp.ofp_parser

		mod = ofp_parser.OFPFlowMod(datapath=dp,
									command=ofp.OFPFC_DELETE,
									out_port=ofp.OFPP_ANY,
									out_group=ofp.OFPG_ANY,
									match=match)
		
		dp.send_msg(mod)

	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def packet_in_handler(self, ev):
		msg = ev.msg
		dp = msg.datapath
		ofp = dp.ofproto
		ofp_parser = dp.ofproto_parser
		
		actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
		out = ofp_parser.OFPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port, actions=actions)
		dp.send_msg(out)
