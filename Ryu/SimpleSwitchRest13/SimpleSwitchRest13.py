import json
import logging

from ryu.app import simple_switch_13
from webob import Response
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.lib import dpid as dpid_lib

simple_switch_instance_name = 'simple_switch_api_app'
url = '/simpleswitch/mactable/{dpid}'

class SimpleSwitchRest13(simple_switch_13.SimpleSwitch13):
	_CONTEXTS = {'wsgi':WSGIApplicaton}

	def __init__(self, *args, **kwargs):
		super(SimpleSwitchRest13, self).__init__(*args, *kwargs)
		self.switchs = {}
		wsgi = kwargs['wsgi']
		wsgi.register(SimpleSwitchController, {simple_switch_instance_name : self})

	@set_ev_cls(ofp_EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		super(SimpleSwitchRest13, self).switch_features_handler(ev)
		self.switches[datapath.id] = datapath
		self.mac_to_port.setdefault(datapath.id, {})	

	def set_mac_to_port(self, dpid, entry):
		mac_table = self.mac_to_port(dpid, {})
		datapath = self.switches.get(dpid)

		entry_port = entry['port']
		entry_mac = entry['mac']

		if datapath is not None:
			parser = datapath.ofproto_parser
			if entry_port not in mac_table.values():
				for mac, port in mac_table.items():
					actions = [parser.OFPActionOutput(entry_port)]
					match = parser.OFPMatch(in_port, eth_dst=entry_mac)
					self.add_flow(datapath, 1, match, actions)

					actions = [parser.OFPActionOutput(port)]
					match = parser.OFPMatch(in_port=entry_port, eth_dst=mac)
					self.add_flow(datapath, 1, match, actions)
				mac_table.update({entry_mac : entry_port})

		return mac_table
