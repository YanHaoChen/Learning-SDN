# Traffic Monitor

透過繼承```simple_switch_13```完成封包轉送的需求，並不斷發出```OFPFlowStatsRequest ```及```OFPPortStatsRequest ```，取得網路狀況統計資訊。

## 宣告
```python
from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
```
### attrgetter

在此，為對輸出的資訊進行排序所需的函式。利用此函式，在使用```sorted```（排序）時，可以簡化給參數```key```的方式。使用方式如下：

```python
sorted(objects, key= attrgetter('Attribute_A'))
```

objects 在排序時，就會針對 objects 的```Attribute_A```屬性，進行排序。

### Switch 與 Controller 之間的溝通狀況

* MAIN_DISPATCHER：一般狀態（完成交握）
* DEAD_DISPATCHER：連線中斷

### set\_ev\_cls

透過 set\_ev\_cls 裝飾器，依接收到的參數（事件類別、Switch 狀態），而進行反應。

### hub
在此，用來負責執行緒的工作。Ryubook 中有提到，其本質是使用```eventlet```進行。```eventlet```的```green threads```所擁有的特性，相當適用於網路架構所需的執行緒需求。（並沒有真正使用過，在此不多做介紹，以免誤導）

## 初始化

繼承```simple_switch_13.SimpleSwitch13```，實現封包轉送的部分。

```python
class SimpleMonitor(simple_switch_13.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
#...
```

### self.datapaths = {}

用來存放監測中的 Switch 資訊。

### self.monitor\_thread = hub.spawn(self.\_monitor)

將```_monitor```方法放入執行緒中。不斷執行```取得統計狀況請求```。

## EventOFPStateChange 事件
在此事件中，我們可以接收到 Switch 狀態改變的訊息，藉此修改```self.datapath```，讓```self.datapath```只存放正在運行中的 Switch。

```python
#...

@set_ev_cls(ofp_event.EventOFPStateChange,
            [MAIN_DISPATCHER, DEAD_DISPATCHER])
def _state_change_handler(self, ev):
    datapath = ev.datapath
    if ev.state == MAIN_DISPATCHER:
        if not datapath.id in self.datapaths:
            self.logger.debug('register datapath: %016x', datapath.id)
            self.datapaths[datapath.id] = datapath
    elif ev.state == DEAD_DISPATCHER:
        if datapath.id in self.datapaths:
            self.logger.debug('unregister datapath: %016x', datapath.id)
            del self.datapaths[datapath.id]
#...
```
* 如果狀態是```MAIN_DISPATCHER```且不在```self.datapath```中，則放入```self.datapath```。（Switch 連接中）

* 如果狀態是```DEAD_DISPATCHER```且在```self.datapath```中，則從```self.datapath```中移除。（Switch 中斷連結）

## def \_monitor(self):

每間隔10秒，向監測中的 Switch 發出```取得統計狀況請求```。

```python
#...
def _monitor(self):
    while True:
        for dp in self.datapaths.values():
            self._request_stats(dp)
        hub.sleep(10)

#...
```

## def \_request\_stats(self, datapath):
在此分別製作```OFPFlowStatsRequest```、```OFPPortStatsRequest ```請求訊息並發送。

```python
#...

def _request_stats(self, datapath):
    self.logger.debug('send stats request: %016x', datapath.id)
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser

    req = parser.OFPFlowStatsRequest(datapath)
    datapath.send_msg(req)

    req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
    datapath.send_msg(req)

#...
```
* OFPFlowStatsRequest：取得 Switch 中的規則資訊。
* OFPPortStatsRequest：取得 Switch 中每個 Port 的相關資訊以及統計數據。 

> OFPPortStatsRequest 取的指定 Port 的訊息，這邊使用```ofproto.OFPP_ANY```，代表指定所有的 Port。

## FlowStatsReply 事件

處理接收到的規則資訊，並顯示出來。

```python
#...
@set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
def _flow_stats_reply_handler(self, ev):
    body = ev.msg.body

    self.logger.info('datapath         '
                     'in-port  eth-dst           '
                     'out-port packets  bytes')
    self.logger.info('---------------- '
                     '-------- ----------------- '
                     '-------- -------- --------')
    for stat in sorted([flow for flow in body if flow.priority == 1],
                       key=lambda flow: (flow.match['in_port'],
                                         flow.match['eth_dst'])):
        self.logger.info('%016x %8x %17s %8x %8d %8d',
                         ev.msg.datapath.id,
                         stat.match['in_port'], stat.match['eth_dst'],
                         stat.instructions[0].actions[0].port,
                         stat.packet_count, stat.byte_count)
#...
```
### stat 排序的方式

透過```sorted```函式，進行排序。

```python
[flow for flow in body if flow.priority == 1]
```
以上程式碼用來產生，將被排序的物件。找尋```body```(為 OFPFlowStats 的列表）內的所有資料，將資料中的 ```flow.priority == 1```的資料納入將要排序的物件中（排除轉往 Controller 的規則）。

```python
lambda flow: (flow.match['in_port'],flow.match['eth_dst'])
```
以上程式碼用來產生排序條件。因```key```的參數型態為函式，所以透過```lambda```來建立排序條件，並依```in_port```跟 ```eth_dst```進行排序。

> Ryubook 中也有提到，將資料轉換成```json```格式的方式：
> 
> ```python
> import json

> self.logger.info('%s', json.dumps(ev.msg.to_jsondict(), ensure_ascii=True,indent=3, sort_keys=True))
> ```
> 
> 如要進行分析，將資料轉成```json```是個不錯的選擇。

## PortStatsReply 事件

處理接收到的 Port 的資訊，並顯示出來。

```python
#...

@set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
def _port_stats_reply_handler(self, ev):
    body = ev.msg.body

    self.logger.info('datapath         port     '
                     'rx-pkts  rx-bytes rx-error '
                     'tx-pkts  tx-bytes tx-error')
    self.logger.info('---------------- -------- '
                     '-------- -------- -------- '
                     '-------- -------- --------')
    for stat in sorted(body, key=attrgetter('port_no')):
        self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                         ev.msg.datapath.id, stat.port_no,
                         stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                         stat.tx_packets, stat.tx_bytes, stat.tx_errors)

```
### stat 排序的方式
在此```body```指的是 OFPPortStats 的資料列表。利用```attrgetter```函式，將```port_no```當成排序條件。

## 執行
可以用在 [Mininet 連結 Ryu](https://github.com/imac-cloud/SDN-tutorial/tree/master/MininetConnectRyu) 中的 Mininet 設定方式，將 Mininet 連結 Monitor 連結，並透過操作 Mininet 檢視監控成果。

```shell
$ ryu-manager --verbose ./SimpleMonitor.py
```

## 參考
[Ryubook](https://osrg.github.io/ryu-book/zh_tw/html/traffic_monitor.html)

[Eventlet 0.19.0 documentation](http://eventlet.net/doc/basic_usage.html)
