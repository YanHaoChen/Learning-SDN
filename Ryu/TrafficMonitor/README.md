# Traffic Monitor

透過繼承```simple_switch_13```完成封包轉送的需求，並不斷發出```OFPFlowStatsRequest ```及```OFPPortStatsRequest ```，取得流通的封包資訊。

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

```
sorted(objects, key= attrgetter('Attribute_A'))
```

```objects```在排列時，就會針對```objects```的```Attribute_A```屬性，進行排序。

### ryu.controller的事件類別名稱

* MAIN_DISPATCHER：一般狀態
* DEAD_DISPATCHER：連線中斷

### set_ ev_cls

當裝飾器使用。因Ryu皆受到任何一個OpenFlow的訊息，都會需要產生一個對應的事件。為了達到這樣的目的，透過set_ev_cls當裝飾器，依接收到的參數（事件類別、Switch狀態），而進行反應。

### hub
在此，用來負責多執行緒的工作。Ryubook中有提到，其本質是使用```eventlet```進行。```eventlet```的```green threads```所擁有的特性，相當適用於網路架構所需的執行緒需求。（並沒有真正使用過，在此不多做介紹，以免誤導）

## 初始化

在此，繼承```simple_switch_13.SimpleSwitch13```，實現封包轉送的部分。

```python
class SimpleMonitor(simple_switch_13.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
#...
```

### self.datapaths = {}

用來存放監測中的datapath資訊。

### self.monitor_ thread = hub.spawn(self._monitor)

將```_monitor```方法放入執行緒中。不斷執行```取得統計狀況請求```。

## EventOFPStateChange 事件
在此事件中，我們可以接收到Datapath狀態改變的訊息，藉此修改```self.datapath```，讓```self.datapath```只存放正在監控中的Datapath。

```python
 # ...

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
 # ...
```
* 如果狀態是```MAIN_DISPATCHER```且不在```self.datapath```中，則放入```self.datapath```。

* 如果狀態是```DEAD_DISPATCHER```且在```self.datapath```中，則從```self.datapath```中移除。

## 參考
[Ryubook](https://osrg.github.io/ryu-book/zh_tw/html/traffic_monitor.html)

[Eventlet 0.19.0 documentation](http://eventlet.net/doc/basic_usage.html)