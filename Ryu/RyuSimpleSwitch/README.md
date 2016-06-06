# Ryu-Simple Switch with Openflow 1.3

 此程式的兩大主要功能:
 
 * 分派管轄網路內的封包流向
 * 處理不明封包

## 開頭宣告

```python
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
```

#### app_manager
實作Ryu應用程式，都需要繼承app_manager.RyuApp。

#### ryu.controller的事件類別名稱
* CONFIG_DISPATCHER：接收SwitchFeatures
* MAIN_DISPATCHER：一般狀態
* DEAD_DISPATCHER：連線中斷 //在此沒有用到
* HANDSHAKE_DISPATCHER：交換HELLO訊息 //在此沒有用到

#### set_ ev_cls
當裝飾器使用。因Ryu皆受到任何一個OpenFlow的訊息，都會需要產生一個對應的事件。為了達到這樣的目的，透過set_ev_cls當裝飾器，依接收到的參數（事件類別、Switch狀態），而進行反應。

#### ofproto_ v1_3
使用的OpenFlow版本1.3。

## 初始化
```python
class SimpleSwitch13(app_manager.RyuApp): 
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
 
    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
    # ...
```

#### class SimpleSwitch13(app_manager.RyuApp):
第一步就是繼承app_manager.RyuApp，讓App在Ryu的框架中。


#### OFP_ VERSIONS = [ofproto_ v1_ 3.OFP_VERSION]
設定OpenFlow的版本為1.3版。

#### super(SimpleSwit…
實體化父類別（app_manager.RyuApp），讓此app的RyuApp功能實體化（可以使用）。

#### self.mac_to_port = {}
建立參數mac_to_port，當作MAC位址表。

## 加入 Table-miss Flow Entry 事件處理

在OpenFlow Switch中，至少有一個```Flow Table```，每個```Flow Table```又會包含多個```Flow Entry```。這些```Flow Table```是有分優先權的，優先權的順序由0開始往上。```Flow Table```中存放的```Flow Entry```，裡面所包含的就是相對應的執行動作。當```Packet-in```的時候，就會去```Flow Table```中，找尋可以```match```的```Flow Entry```並執行其```Flow Entry```設定的執行的動作。

在這裡增加的```Table-miss Flow Entry```，就是要處裡「遇到沒辦法```match```的```Flow Entry```」該做的事。

```python
@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
def switch_features_handler(self, ev):
    datapath = ev.msg.datapath
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    #...
```

#### ev.msg
儲存OpenFlow的對應訊息。

#### datapath
處理OpenFlow訊息的類別。

#### ofproto
OpenFlow的常數模組，做為通訊協定中的常數設定使用。

#### parser
OpenFlow的解析模組，解析模組提供各個 OpenFlow 訊息的對應類別。

> ofprotor及parser的資料[參考來源](https://osrg.github.io/ryu-book/zh_tw/html/ofproto_lib.html)。

```python
def switch_features_handler(self, ev):
 
    #...
 
    match = parser.OFPMatch()
    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,ofproto.OFPCML_NO_BUFFER)]
    self.add_flow(datapath, 0, match, actions) 
```

#### match = parser.OFPMatch()
產生一個新的match。

#### actions = [parser.OFPActio…
產生一個OFPActionOutput類別action，並指定他是要傳送至Controller的（ofproto.OFPP_ CONTROLLER），且並不使用Buffer（ofproto.OFPCML_ NO_BUFFER）。

#### self.add_flow(dat…
夾帶datapath、優先權（0）、match、actions，到我們自行寫的add_flow func中（等一下文中會進行介紹），並觸發Packet-In事件（封包並沒有match到任何Flow Entry的情況下，就會觸發）。

> Table-miss Flow Entry的優先權規定為0，也就是最低的優先權。

## 加入 Packet-In 事件處理
```python
@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def _packet_in_handler(self, ev):
    msg = ev.msg
    datapath = msg.datapath
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
 
    #...
```
在Packet-In事件處理中，一開始的參數設定跟剛剛所提到的是一樣的，所以不再贅述囉！接下來直接進入```更新MAC位址表```的部分。

```python
def _packet_in_handler(self, ev):
    #...
 
    in_port = msg.match['in_port']
 
    pkt = packet.Packet(msg.data)
    eth = pkt.get_protocols(ethernet.ethernet)[0]
 
    dst = eth.dst
    src = eth.src
 
    dpid = datapath.id
    self.mac_to_port.setdefault(dpid, {})
 
    self.logger.info(&amp;amp;amp;quot;packet in %s %s %s %s&amp;amp;amp;quot;, dpid, src, dst, in_port)
 
    self.mac_to_port[dpid][src] = in_port
    #...   
```

#### 解析訊息，並存放至參數中

in_port、pkt、eth、dst、src、dpid。以上都是等一下，運作中會用到的參數。

#### 設定更新MAC表
self.mac_ to_ port.setdefault(dpid, {})及self.mac_ to_ port[dpid][src] = in_port的作用，都是用來將來源主機放入MAC表中。

> 會使用dpid當mac_ to_port的第一識別參數，是因為當有多個OpenFlow交換器時，可以使用它來識別

```
def _packet_in_handler(self, ev):
 
    #...
 
    if dst in self.mac_to_port[dpid]:
        out_port = self.mac_to_port[dpid][dst]
    else:
        out_port = ofproto.OFPP_FLODD
 
    actions = [parser.OFPActionOutput(out_port)]
 
    if out_port != ofproto.OFPP_FLOOD:
        match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
        self.add_flow(datapath, 1, match, actions)
    #...
```
#### if dst in self.ma…
判斷目的位址是否已經在MAC表中，如果有，則直接將對應的位址放入```out_port```。如果沒有，則放入```ofproto.OFPP_FLODD```。

#### actions = [par…
在此先準備好一個OFPActionOutput的actions，其對應的位址是剛剛經過判斷式設定的```out_port```。

#### if out_port != ofpro…
判斷如果目的位止已經在MAC表中，則將建立此Flow Entry（建立方式如判斷式成立後的執行動作）。值得注意的是，建立Flow Entry的優先權為1哦！

> add_flow已經都出現完了，以下就先介紹它的用途。介紹完後，再回到Packet-In。

## 新增 Flow Entry 的處理（add_flow）

```python
def add_flow(self, datapath, priority, match, actions):
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
 
    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
 
    mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instruction=inst)
    datapath.send_msg(mod)
```
#### inst = [parser.OFPInstruct…
用來定義封包所需要執行的動作。ofproto.OFPIT_APPLY_ACTIONS對Switch來說，就是需要立即執行的action。

> Instruction 是用來定義當封包滿足所規範的 Match 條件時，需要執行的動作。[參考來源](https://osrg.github.io/ryu-book/zh_tw/html/openflow_protocol.html?highlight=instruction)

#### mod = parser.OFPF…
產生一個```OFPFlowMod```類別（為將要傳出的資料類別）。```OFPFlowMod```可帶的參數很多，如想進一步了解，可以看看Ryubook中的補充（第12頁）。

#### datapath.send_msg(mod)
將訊息送出。

> 接下來，回到Packet-In

```
def _packet_in_handler(self, ev):
    #...
 
    data = None
    if msg.buffer_id == ofproto.OFP_NO_BUFFER:
        data = msg.data
 
    out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
    datapath.send_msg(out)
```

#### if msg.buffer_id == ofpr…
檢查一下Buffer，然後把msg.data放入data。

#### out = parser.OFPPacketOut(datapa…
將要傳送的類別，依需要的參數建立起來。

#### datapath.send_msg(out)
最後，送出！

## 總結

雖然只是實現一個簡單Switch的功能，但裡面包含了許多OpenFlow Switch的基本知識。如對OpenFlow Switch的概念還不清楚，可以透過這隻app，初步認識OpenFlow Switch。


