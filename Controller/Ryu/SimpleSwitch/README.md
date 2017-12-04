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

#### app\_manager
實作 Ryu 應用程式，都需要繼承 app\_manager.RyuApp。

#### Switch 與 Controller 之間的溝通狀況
* CONFIG\_DISPATCHER：接收 SwitchFeatures
* MAIN\_DISPATCHER：一般狀態（交握完畢）
* DEAD\_DISPATCHER：連線中斷 //在此沒有用到
* HANDSHAKE\_DISPATCHER：交換 HELLO 訊息 //在此沒有用到

#### set\_ev\_cls
透過 set\_ev\_cls 裝飾器，依接收到的參數（事件類別、 Switch 狀態），而進行反應。

#### ofproto\_v1\_3
使用的 OpenFlow 版本1.3。

## 初始化
```python
class SimpleSwitch13(app_manager.RyuApp): 
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
 
    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
    # ...
```

#### class SimpleSwitch13(app\_manager.RyuApp):
第一步就是繼承 app\_manager.RyuApp，讓 App 在 Ryu 的框架中。


#### OFP\_VERSIONS = [ofproto\_v1\_3.OFP\_VERSION]
設定 OpenFlow 的版本為1.3版。

#### super(SimpleSwit…
實體化父類別（app\_manager.RyuApp），讓此 app 的 RyuApp 功能實體化（可以使用）。

#### self.mac\_to\_port = {}
建立參數 mac\_to\_port，當作 MAC 位址表。

## 加入封包轉送至 Controller 的規則

> 其實並不用特別加入此規則，因為當 Switch 沒有 Match 到任何規則時，就會自動的將封包傳往 Controller，因此可以省略此部分的設定。

在 Swtich 與 Controller 連結時，對 Table 0（也就是封包第一個會到達的 Table）加入規則，將封包直接轉往 Controller。

```python
def switch_features_handler(self, ev):
 
    #...
 
    match = parser.OFPMatch()
    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,ofproto.OFPCML_NO_BUFFER)]
    self.add_flow(datapath, 0, match, actions) 
```

#### match = parser.OFPMatch()
產生 Match 條件，且不帶任何 Match 條件。不帶任何 Match 條件，其實就代表著所有的封包都會 match 到此規則。

#### actions = [parser.OFPActio…
產生 Action，其動作為將封包傳送至 Controller，且並不使用 Buffer。

> 不使用 Buffer 的意思為：不將封包暫存在 Switch 的 Buffer 上，而是將整個封包直接傳往 Controller 進行處理。

#### self.add\_flow(dat…
夾帶 datapath、規則的優先權、match、actions，到我們自行撰寫的 add\_flow func 中（等一下文中會進行介紹），將規則加入 Table 0 中。


## 控管 Packet-In 事件

也因為在 Table 0 建立的規則（將封包轉往 Controller），所以當封包沒有對應到任何規則時，將會觸發 Packet-In 事件，也因此我們需要在 Packet-In 事件中，執行我們的管理邏輯。此 Ryu 程式的目的在於實現一個 Switch，因此我們會需要在此事件中，建立、更新 MAC address Table（```self.mac_to_port```）。以下為，建立及更新的實作過程：

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
 
    self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
 
    self.mac_to_port[dpid][src] = in_port
    #...   
```

#### 解析訊息，並存放至參數中

in_port、pkt、eth、dst、src、dpid。以上都是等一下，運作中會用到的參數。

#### 更新 MAC 表

初始化 MAC address Table。

```python
self.mac_to_port.setdefault(dpid, {})
``` 

將來源主機的 port number 記錄下來：

```python
self.mac_to_port[dpid][src] = in_port
```

> 會使用 dpid（Switch ID） 當 mac\_to\_port 的第一識別參數，是因為當有多個 Switch 時，可以使用它來識別。

接下來，決定將封包轉往目的地主機並加入規則，或進行 Flooding 找尋目的地主機：

```python
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
判斷目的主機是否已經在 MAC 表中，如果有，則轉往對應主機，沒有則進行 Flooding。

#### actions = [par…
建立輸出 Action，其動作為，將封包依上述判斷轉往指定 port 上。

#### if out\_port != ofpro…
判斷如果目的主機已經在 MAC 表中，則建立此規則。在此會將優先權設為 1，是因為在進行規則對應時，會依規則優先權的高低而由高的對應到低的。所以這樣的設定也代表，當封包沒有對應到任何轉送規則時，才會對應到**轉往 Controller** 這條規則。

> add_flow 已經都出現完了，以下就先介紹它的用途。介紹完後，再回到 Packet-In。

## 新增 Flow Entry 的處理（add\_flow）

```python
def add_flow(self, datapath, priority, match, actions):
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
 
    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
 
    mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instruction=inst)
    datapath.send_msg(mod)
```
#### inst = [parser.OFPInstruct…
用來定義符合規則後，所需要執行的動作（Action）。ofproto.OFPIT\_APPLY\_ACTIONS 對 Switch 來說，是指如 Table 中已有同樣的規則（Match 條件相同），則保留舊的動作，不覆寫。

#### mod = parser.OFPF…
產生一個```OFPFlowMod```類別（為將要傳出的資料類別）。```OFPFlowMod```可帶的參數很多，如想進一步了解，可以看看 Ryubook 中的補充（第12頁）。

#### datapath.send\_msg(mod)
將訊息送出。

> 接下來，回到Packet-In。

最後是封包在 Packet-In 的後續處理，也就是由 Controller 進行封包分配：

```python
def _packet_in_handler(self, ev):
    #...
 
    data = None
    if msg.buffer_id == ofproto.OFP_NO_BUFFER:
        data = msg.data
 
    out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
    datapath.send_msg(out)
```

#### if msg.buffer\_id == ofpr…
檢查一下 Buffer，然後把 msg.data 放入 data。

#### out = parser.OFPPacketOut(datapa…
產生 Packet-Out 事件。

#### datapath.send\_msg(out)
最後，送出！

## 參考
[Ryubook](https://osrg.github.io/ryu-book/zh_tw/Ryubook.pdf)
