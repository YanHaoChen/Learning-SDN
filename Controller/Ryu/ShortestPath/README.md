# 最短路徑規劃

在封包轉送方面，最短路徑演算法是最基本的選擇，本文將透過 NetworkX 來計算各節點（主機跟主機）間的最短路徑，並以 Ryu 實作網路中的路由設定。

## 環境

#### OpenFlow

Version: 1.3

#### Mininet 拓樸
[mininet_env.py]()

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

###  Init

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
* self.net：初始化 NetworkX
* self.switch\_map：將連線的 Switch 實體儲存下來，供路徑配置使用。
* self.arp_table：處理 ARP 封包使用的實體位置（MAC）對應表。

### SwitchFeatures

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

2-5. 寫入處理的 ARP 用的預設規則（如目的地位置為`ff:ff:ff:ff:ff:ff`，則轉往 Controller 進行處理）   