# 最短路徑規劃

在封包轉送方面，最短路徑演算法是最基本的選擇，本文將透過 NetworkX 來計算各節點（主機跟主機）間的最短路徑，並以 Ryu 實作網路中的路由設定。

## 環境

#### OpenFlow

Version: 1.3

#### Mininet 拓樸
[mininet_env.py](https://github.com/OSE-Lab/Learning-SDN/blob/master/Controller/Ryu/ShortestPath/mininet_env.py)

```
 h1            h2
   \          /
    s1 ---- s2
     \      /
      \    /
        s3
        |
        h3
```

## 邏輯

以下，將以一個概略的流程圖呈現 Ryu 程式的運作流程，並講解其中編寫方式：

```python
Init:
	初始化需要的全域變數
SwitchFeatures:
	取的連結的 Switch 資訊，並寫入預設規則（用來處理 ARP 封包）
PacketIn:
	依 NetworkX 產生的最短路徑，配置路由方式
SwitchEnter:
	取得拓樸，並將節點及連線加入 NetworkX 中
```

> 其中有部分程式碼並未介紹，請參照檔案：[shortest\_path\_with\_networkx.py](https://github.com/OSE-Lab/Learning-SDN/blob/master/Controller/Ryu/ShortestPath/shortest_path_with_networkx.py) 

###  Init

初始化需要的全域變數。

```python
def __init__(self, *args, **kwargs):
		super(shortest_path, self).__init__(*args, **kwargs)
		self.topology_api_app = self
		self.net = nx.DiGraph()
		self.switch_map = {}
		self.arp_table = {'10.0.0.1':'00:00:00:00:00:01',
							'10.0.0.2':'00:00:00:00:00:02',
							'10.0.0.3':'00:00:00:00:00:03'}
```

* self.topology\_api\_app：供拓樸搜尋用。
* self.net：初始化 NetworkX。
* self.switch\_map：將連線的 Switch 實體儲存下來，供路徑配置使用。
* self.arp_table：處理 ARP 封包使用的實體位置（MAC）對應表。

### SwitchFeatures

取的連結的 Switch 資訊，並寫入預設規則（用來處理 ARP 封包）。

```python
@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		dp = ev.msg.datapath
		ofp = dp.ofproto
		ofp_parser =dp.ofproto_parser
		# 1
		self.switch_map.update({dp.id: dp})
		# 2 
		match = ofp_parser.OFPMatch(eth_dst='ff:ff:ff:ff:ff:ff')
		# 3
		action = ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, [ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER)])
		# 4
		inst=[action]
		# 5
		self.add_flow(dp=dp, match=match, inst=inst, table=0, priority=100)
```

1. 將連線到的 Switch 實體以`key-value`的方式加入`self.switch_map`中。

2-5. 寫入處理的 ARP 用的預設規則（如目的地位置為`ff:ff:ff:ff:ff:ff`，則轉往 Controller 進行處理）。

### PacketIn

此部分屬於整體的核心，也就是最短路徑的規劃。在此透過收到未知封包（代表主機尚未加入`NetworkX`中），將新加入拓樸環境的主機加入`NetworkX`中。

```python
@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def packet_in_handler(self, ev):
	msg= ev.msg
	dp = msg.datapath
	ofp = dp.ofproto
	ofp_parser = dp.ofproto_parser

	port = msg.match['in_port']
		
	## parses the packet
	pkt = packet.Packet(data=msg.data)
	# ethernet
	pkt_ethernet = pkt.get_protocol(ethernet.ethernet)
		
	if not pkt_ethernet:
		return

	# filters LLDP packet
	if pkt_ethernet.ethertype == 35020:
		return
		
	# arp
	pkt_arp = pkt.get_protocol(arp.arp)
	if pkt_ethernet.ethertype == 2054:
		print "arp"
		self.handle_arp(dp, port, pkt_ethernet, pkt_arp)
		return
	# forwarded by shortest path
	if not self.net.has_node(pkt_ethernet.src):
		print "add %s in self.net" % pkt_ethernet.src
		self.net.add_node(pkt_ethernet.src)
		self.net.add_edge(pkt_ethernet.src, dp.id)
		self.net.add_edge(dp.id, pkt_ethernet.src, {'port':port})
		print self.net.node

	if self.net.has_node(pkt_ethernet.dst):
		print "%s in self.net" % pkt_ethernet.dst
		path = nx.shortest_path(self.net, pkt_ethernet.src, pkt_ethernet.dst)
		next_match = ofp_parser.OFPMatch(eth_dst=pkt_ethernet.dst)
		back_match = ofp_parser.OFPMatch(eth_dst=pkt_ethernet.src)
		print path
		for on_path_switch in range(1, len(path)-1):
			now_switch = path[on_path_switch]
			next_switch = path[on_path_switch+1]
			back_switch = path[on_path_switch-1]
			next_port = self.net[now_switch][next_switch]['port']
			back_port = self.net[now_switch][back_switch]['port']
			action = ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, [ofp_parser.OFPActionOutput(next_port)])
			inst = [action]
			self.add_flow(dp=self.switch_map[now_switch], match=next_match, inst=inst, table=0)
				
			action = ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, [ofp_parser.OFPActionOutput(back_port)])
				inst = [action]
				self.add_flow(dp=self.switch_map[now_switch], match=back_match, inst=inst, table=0)
				print "now switch:%s" % now_switch
	else:
		return
```

#### Parses the packet

解析分封包後，過濾出需要進一步規劃的封包。例如 ARP 封包處理及規劃路徑封包。

#### Forwarded by shortest path

在此部分，有兩主要邏輯：

```python
if 來源主機不在 NetworkX 中:
	加入 NetworkX 中

if 目的地主機在 NetworkX 中：
	使用 NetworkX 計算最短路徑，並在沿線 Switch 上，加入雙向轉送規則
else:
	return
```

### SwitchEnter

在 Ryu 中，取得整體拓樸的方式。在取得後，把拓樸加入 NetworkX 中。

```python
@set_ev_cls(event.EventSwitchEnter)
def get_topology_data(self, ev):
	switch_list = get_switch(self.topology_api_app, None)
	switches =[switch.dp.id for switch in switch_list]
	links_list = get_link(self.topology_api_app, None)
	links=[(link.src.dpid,link.dst.dpid,{'port':link.src.port_no}) for link in links_list]
	print links		
	self.net.add_nodes_from(switches)
	self.net.add_edges_from(links)
```

## 測試

在 Mininet 中執行`pingall`後，主機跟主機的最短路徑就會配置完畢。

> 第一次執行的`pingall`會有不通的主機是正常的。因為再循序`ping`的過程中，有些主機因尚未打封包而未被加入 NetworkX 中。在第二次`pingall`時，就能完全互通。
