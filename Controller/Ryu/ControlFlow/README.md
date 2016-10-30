# 控制規則

接下來所提的是在規劃轉送路徑最重要的部分，也就是__控制規則__。實作的方式，將透過一個例子，來說明。首先，說明一下這個例子需求：

* 讓 Switch 中的主機可以在學習後，互相溝通
* 主機脫離時，刪除有關此主機的規則

## 環境

#### 設備
* Switch：1 台
* Host：3 台

#### 連線狀況

```shell
Host 1 < h1-eth0)---(s1-eth1 > Switch
Host 2 < h2-eth0)---(s1-eth2 > Switch
Host 3 < h3-eth0)---(s1-eth3 > Switch
```


## 程式說明

在這此程式中，能學習到兩個重點，分別為：

* 新增、刪除規則
* EventOFPPortStateChange 事件

新增、刪除本來就是本節的重點，EventOFPPortStateChange 事件則是因為配合刪除的情境一並介紹。以下將介紹新增、刪除的程式碼編寫方式，及整體編寫邏輯。

> 以下將以局部做介紹。完整程式：[control_flow.py](https://github.com/imac-cloud/SDN-tutorial/blob/master/Controller/Ryu/ControlFlow/control_flow.py)

### 新增

要對 Switch 新增規則，是需要由 Controller（Ryu）透過傳送```OFPFlowMod```給 Switch，Switch 收到此訊息後，則將對應的規則加入。在此建立一個 Function（```add_flow```），讓我們在加入規則時方便一些：

```python
def add_flow(self, dp, match=None, inst=[], table=0, priority=32768):
	ofp = dp.ofproto
	ofp_parser = dp.ofproto_parser

	buffer_id = ofp.OFP_NO_BUFFER

	mod = ofp_parser.OFPFlowMod(
		datapath=dp, cookie=0, cookie_mask=0, table_id=table,
		command=ofp.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
		priority=priority, buffer_id=buffer_id,
		out_port=ofp.OFPP_ANY, out_group=ofp.OFPG_ANY,
		flags=0, match=match, instructions=inst)

	dp.send_msg(mod)
```

可以發現 OFPFlowMod 可以使用參數很多，但常需要更動的不多，也因此將常需要更動的參數當作```add_flow```的參數。分別為：

* dp：指定的 Switch
* match：此規則的 Match 條件
* inst：Match 規則後，將執行的動作
* table：規則要放在哪一個 table 中
* priority：此規則的優先權

### 刪除

刪除跟新增的方式其實是很像的，最大的差別就在於```command```此參數的給定。在刪除中，給定的是```ofp.OFPFC_DELETE```，新增則是```ofp.OFPFC_ADD```。也因為只是刪除，所以需要的參數也會比較少。在此我們可以透過指定 Match 條件及所在的 Table 進行刪除：

```python
def del_flow(self, dp, match, table):
	ofp = dp.ofproto
	ofp_parser = dp.ofproto_parser

	mod = ofp_parser.OFPFlowMod(datapath=dp,
		command=ofp.OFPFC_DELETE,
		out_port=ofp.OFPP_ANY,
		out_group=ofp.OFPG_ANY,
		match=match,
		table_id=table)

	dp.send_msg(mod)
```

### 學習（Packet In）

學習也就是開始新增規則的部分。

```python
@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def packet_in_handler(self, ev):
	msg = ev.msg
	dp = msg.datapath
	ofp = dp.ofproto
	ofp_parser = dp.ofproto_parser

	port = msg.match['in_port']

	## Get the packet and parses it
	pkt = packet.Packet(data=msg.data)
	# ethernet
	pkt_ethernet = pkt.get_protocol(ethernet.ethernet)

	if not pkt_ethernet:
		return

	# Filters LLDP packet
	if pkt_ethernet.ethertype == 35020:
		return		
	
	match = ofp_parser.OFPMatch(eth_dst=pkt_ethernet.src)
	intstruction_action =
		ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,
			[ofp_parser.OFPActionOutput(port)])
	inst = [intstruction_action]
	self.add_flow(dp, match=match, inst=inst, table=0)
	self.switch_table[dp.id][pkt_ethernet.src] = port

	actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
	out =ofp_parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=port, actions=actions)
		
	dp.send_msg(out)
```

在此第一步就是把封包的資訊（```msg.data```）解析出來，才能知道該怎麼下規則。

```python
	pkt = packet.Packet(data=msg.data)
	pkt_ethernet = pkt.get_protocol(ethernet.ethernet)
```

建立規則的 Match 條件及 Action。所建立的規則為：

* Match：封包的 MAC Destination 為，現在接收到的封包的 MAC Source
* Action：傳往此封包的來源 port 上

```python
	match = ofp_parser.OFPMatch(eth_dst=pkt_ethernet.src)
	intstruction_action =
		ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,
			[ofp_parser.OFPActionOutput(port)])
	inst = [intstruction_action]
```

此目的在於，讓我們對現有的主機狀況進行學習，往後如果有要傳往此主機的封包，會有規則可以直接對應。

接下來透過我們寫好的```add_flow```將規則加入，並將主機資訊記錄在 Controller 的```self.switch_table```，供之後規劃規則使用：

```python
self.add_flow(dp, match=match, inst=inst, table=0)
self.switch_table[dp.id][pkt_ethernet.src] = port
```

也因為會引起 Packet In 事件的封包，都是沒有對應到規則的封包，所以我們用最傳統的方式去處理，也就是 Flood：

```python
	actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
	out =ofp_parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=port, actions=actions)
		
	dp.send_msg(out)
```

### 刪除脫離主機（Port State Change）

如果主機已經脫離 Switch 了，相關的規則勢必要進行刪除，要偵測主機是否脫離，可以透過```EventOFPPortStateChange```此事件進行。它將會回傳對應的 Datapath（Switch）及狀態改變的 port，使用這兩個資訊，我們將可以把脫離主機的規則進行刪除。

```python
@set_ev_cls(ofp_event.EventOFPPortStateChange, MAIN_DISPATCHER)
def port_state_change_handler(self, ev):
	dp = ev.datapath
	ofp = dp.ofproto
	ofp_parser = dp.ofproto_parser
	change_port = ev.port_no

	del_mac = None

	for host in self.switch_table[dp.id]:
		if self.switch_table[dp.id][host] == change_port:
			del_match = ofp_parser.OFPMatch(eth_dst=host)
			self.del_flow(dp=dp, match=del_match, table=0)
			break

	if del_mac != None:
		del self.switch_table[dp.id][del_mac]
```
首先，取得對應的 Datapath 及 port：

```python
	dp = ev.datapath
	ofp = dp.ofproto
	ofp_parser = dp.ofproto_parser
	change_port = ev.port_no
```

接下來，搜尋在學習時記錄下來的 Switch 資訊（self.switch_table），查看此 port 上是否有對應的主機，如果有則使用```del_flow```將對應的規則刪除：

```python
	del_mac = None

	for host in self.switch_table[dp.id]:
		if self.switch_table[dp.id][host] == change_port:
			del_match = ofp_parser.OFPMatch(eth_dst=host)
			self.del_flow(dp=dp, match=del_match, table=0)
			break

	if del_mac != None:
		del self.switch_table[dp.id][del_mac]
```

## 總結

瞭解以上運作模式後，就可以知道如何新增、刪除。但要控制規則，另一個關鍵其實在於事件的搭配，如「在什麼情況下，要做什麼事」。有了以上的基本知識後，就可以試著實作自己的轉送邏輯囉！

> 補充資訊：[事件列表](http://ryu.readthedocs.io/en/latest/ryu_app_api.html#event-classes)