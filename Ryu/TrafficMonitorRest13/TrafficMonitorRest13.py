from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

from ryu.lib import dpid as dpid_lib
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from webob import Response
import json
import logging

traffic_monitor_instance_name = 'traffic_monitor_api_app'

portStatUrl = '/trafficmonitor/portstat'
flowStatUrl = '/trafficmonitor/flowstat'

class TrafficMonitorRest13(simple_switch_13.SimpleSwitch13):
	_CONTEXTS = {'wsgi':WSGIApplication}
	def __init__(self, *args, **kwargs):
		super(TrafficMonitorRest13, self).__init__(*args, **kwargs)
		self.datapaths = {}
		self.flowStat = None
		self.portStat = None
		self.monitor_thread = hub.spawn(self._monitor)
		wsgi = kwargs['wsgi']
		wsgi.register(TrafficMonitorController,{traffic_monitor_instance_name: self})

	@set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
	def _state_change_handler(self, ev):
		datapath = ev.datapath
		if ev.state == MAIN_DISPATCHER:
			if not datapath.id in self.datapaths:
				self.logger.debug('register datapath: %016x', datapath.id)
				self.datapaths[datapath.id] = datapath
		elif ev.state == DEAD_DISPATCHER:
			if datapath.id in self.datapaths:
				self.logger.debug('unregister datapath: %016x',datapath.id)
				del self.datapaths[datapath.id]
	
	def _monitor(self):
		while True:
			for dp in self.datapaths.values():
				self._request_stats(dp)
			hub.sleep(10)
	
	def _request_stats(self, datapath):
		self.logger.debug('send stats request: %016x',datapath.id)
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		req = parser.OFPFlowStatsRequest(datapath)
		datapath.send_msg(req)
		
		req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
		datapath.send_msg(req)

	@set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
	def _flow_stats_reply_handler(self, ev):
		body = ev.msg.body
		self.flowStat = json.dumps(ev.msg.to_jsondict(), ensure_ascii=True, indent=3, sort_keys=True)	
	@set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
	def _port_stats_reply_handler(self,ev):
		body = ev.msg.body
		self.portStat = json.dumps(ev.msg.to_jsondict(), ensure_ascii=True, indent=3, sort_keys=True)	

class TrafficMonitorController(ControllerBase):

	def __init__(self, req, link, data, **config):
		super(TrafficMonitorController, self).__init__(req, link, data, **config)
		self.simple_switch_app = data[traffic_monitor_instance_name]

	@route('trafficmonitor', portStatUrl, methods=['GET'])
	def list_Port_Stat(self, req, **kwargs):
		return Response(content_type='application/json', body = self.simple_switch_app.portStat)
	
	@route('trafficmonitor', flowStatUrl, methods=['GET'])
	def list_Flow_Stat(self, req, **kwargs):
		return Response(content_type='application/json', body = self.simple_switch_app.flowStat)
