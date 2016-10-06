# 撰寫 Ryu 簡易入門

此篇會以撰寫 Ryu 所需要的基本的架構進行探討，希望能讓初學者，能在短時間內學會如何撰寫 Ryu 程式，並瞭解其中架構。教學方式會以一個簡單的範本作為主軸，以邊實作、一邊學習的方式進行。

### Ryu 最基本的樣子

現在我們進行程式的初始化。 首先，導入 Ryu 最主要的一個部分```app_manager```。Ryu 都是需要繼承它，當作一切的開端：

```python
from ryu.base import app_manager
```

初始化它：

```python
from ryu.base import app_manager

class L2Switch(app_manager.RyuApp):
	def __init__(self, *args, **kwargs):
		super(L2Switch, self).__init__(*args, **kwargs)
```

在這裡使用```super```，是為了執行父類別（```app_manager.RyuApp```）初始化時，會執行的程式。

試著執行這隻程式：

```shell
$ ryu-manager l2.py
loading app l2.py
instantiating app l2.py of L2Switch
```

現在，已經完成了最基本的 Ryu 程式了。目前沒有控管任何事件，像是一個空殼。

如果要當一個稱職的 Controller，需要瞭解目前管理的環境是用什麼協定，以及他需要控管哪裡事件，並透過那些事件，執行預期的管理邏輯。

現在讓我們把這隻 Ryu 變得稱職。首先，告訴他管理的環境是用什麼協定：

```python
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_0

class L2Switch(ryu_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
	
	def __init__(self, *args, **kwargs):
	...
```
在此，我們透過```OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]```，來設定此 Ryu 程式所使用的協定為 OpenFlow 1.0 版。

接下來，加入一個常用的事件```packet-in```，並透過此事件，對管理的環境加入我們需求的管理邏輯：

```python
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_0

from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls


class L2Switch (app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
	def __init__(self, *args, **kwargs):
		super(L2Switch, self).__init__(*args, **kwargs)

	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def packet_in_handler(self, ev):
		msg = ev.msg
		dp = msg.datapath
		ofp = dp.ofproto
		ofp_parser = dp.ofproto_parser
		
		actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
		out = ofp_parser.OFPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port, actions=actions)
		dp.send_msg(out)
```

可以發現在事件上，多了一個```set_ev_cls```的裝飾器。此裝飾器是用來辨別所裝飾的副程式的兩個狀態：

* 參數一：負責事件
* 參數二：在何種溝通狀況下執行（Ryu 與 Switch 間的溝通狀況）

以目前的狀況為例，```set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)```，所代表的意思就是：

* 負責 Packet-In 事件
* 在 Switch 與 Ryu 完成交握的狀況下執行

也代表著，只要更換參數，就能管理 OpenFlow 所提供的事件，也因此可以將管理邏輯，由事件帶入整體管理環境中。

接下來，我們看看事件內部的運作該怎麼規劃。首先，介紹透過事件提取出來的參數：

* ev.msg：代表 Packet-In 傳入的資訊（包含 switch、in\_port\_number 等...）
* msg.datapath：在 OpenFlow 中，datapath 代表的就是 Switch
* dp.ofproto、dp.ofproto_parser：取出此 Switch 中，使用的 OpenFlow 協定及Switch 與 Ryu 之間的溝通管道。

接下來，介紹執行的部分。在接收到 Packet-In 的事件時，我們規劃的動作（Action）是將此封包進行 Flooding，也就是傳往除了 in_port 外的所有 port 上。我們透過```ofp_parser```建立此動作：

```python
actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
```

這裡使用到的```OFPActionOutput```，會依給定的參數而將封包傳往指定 port 上。例如：```ofp_parser.OFPActionOutput(1)```，則代表將封包傳往 port 1。因此在這裡我們使用```ofp.OFPP_FLOOD```，規劃封包轉送到除了 in_port 以外的所有 port 上。

再透過產生一個 Packet-Out 事件，將我們要傳出的訊息建立好：

```python
out = ofp_parser.OFPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port, actions=actions)
```
最後使用```dp.send_msg```將此封包傳送至 Switch，Switch 會依此訊息， 進行封包轉送、分配：

```python
dp.send_msg(out)
```

現在嘗試執行它：

```shell
$ ryu-manager l2.py
loading app l2.py
loading app ryu.controller.ofp_handler
instantiating app l2.py of L2Switch
instantiating app ryu.controller.ofp_handler of OFPHandler
```

可以發現與一開始的空殼相比，多了一行回應：

```shell
instantiating app ryu.controller.ofp_handler of OFPHandler
```

回應代表著此 Ryu 程式已經變得稱職，正在控管事件囉！

以上，其實就是以 Ryu 在 SDN 的架構上，實現出一個 Hub 設備的方式，也透過它，來讓初學者瞭解，怎麼編寫一個 Ryu 程式。

## 參考

[ryu readthedocs](http://ryu.readthedocs.io/en/latest/getting_started.html)