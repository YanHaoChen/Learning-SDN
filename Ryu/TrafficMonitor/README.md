# Traffic Monitor

透過繼承```simple_switch_13```完成封包轉送的需求，並不斷發出```OFPFlowStatsRequest ```及```OFPPortStatsRequest ```，取得流通的封包資訊。

## 宣告
```
from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
```

## 參考
[Ryubook](https://osrg.github.io/ryu-book/zh_tw/html/traffic_monitor.html)