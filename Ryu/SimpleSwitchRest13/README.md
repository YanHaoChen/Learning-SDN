# Simple Switch with Restful

在 [Simple Switch](https://github.com/imac-cloud/SDN-tutorial/tree/master/Ryu/SimpleSwitch) 中，已經瞭解了在 Ryu 中，Switch 的基本運作模式。在此，將把這個基本的 Switch 進行擴充，讓它可以更實際、方便的運用。以下爲本章重點：

* 將 Switch 結合 Restful API 的機制。
* 本程式將會由兩個 class 完成。一個是 Switch 本身，另一個是 Controller 的部分。
* 分別使用到的 Restful 方法為```GET```（取得指定 Datapath 的 MAC TABLE 列表）及```PUT```（新增 Flow Entry）。

接下來，就從程式碼開始說明。

## 開頭宣告

```python
import json

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import dpid as dpid_lib
from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication, route

simple_switch_instance_name = 'simple_switch_api_app'
url = '/simpleswitch/mactable/{dpid}'

#...
```

### import json
將統計數據轉換成```json```格式，作為 API 輸出時的資料格式，方便使用者運用。

### simple\_switch\_13

Ryu 中 Switch 的雛形。在此專案中，藉由繼承，實現 Switch 的基本功能。 

### ofp_event

引入 Openflow Protocol 的事件。

### ryu.controller 的事件類別名稱

* CONFIG_DISPATCHER：接收 SwitchFeatures
* MAIN_DISPATCHER：一般狀態 //在此沒有用到
* DEAD_DISPATCHER：連線中斷 //在此沒有用到
* HANDSHAKE_DISPATCHER：交換 HELLO 訊息 //在此沒有用到

### set\_ev\_cls

當裝飾器使用。因 Ryu 接受到任何一個 OpenFlow 的訊息，都會需要產生一個對應的事件。為了達到這樣的目的，透過 set\_ev\_cls 當裝飾器，依接收到的參數（事件類別、 Switch 狀態），而進行反應。

### dpid as dpid_lib

在此運用其中對 Datapath ID 的規範```DPID_PATTERN```。當接收到 Restful 請求時，過濾 Datapath ID 是否符合格式。

### Response

回傳 Restful 請求。

### ryu.app.wsgi
WSGI 本身為 Python 中 Web Application 的框架。在 Ryu 中，透過它，建立 Web Service，提供 Restful API。

### simple\_switch\_instance\_name
以參數儲存程式中，字典用到的 ```key```。在這裡，用來代表專案中的 Switch。

### url

Restful API 對應的 URL。

## Switch Class
接下來說明，專案中 Switch 的部分。

### 初始化
繼承```simple_switch_13.SimpleSwitch13```，實現 Switch 的基本功能。

```python
class SimpleSwitchRest13(simple_switch_13.SimpleSwitch13):
	_CONTEXTS = {'wsgi':WSGIApplication}

	def __init__(self, *args, **kwargs):
		super(SimpleSwitchRest13, self).__init__(*args, **kwargs)
		self.switches = {}
		wsgi = kwargs['wsgi']
		wsgi.register(SimpleSwitchController, {simple_switch_instance_name : self})
#...
```
#### \_CONTEXTS = {'wsgi':WSGIApplication}
變數```_CONTEXTS```為類別變數。在此將 Ryu 中的 WSGI 所運用的模式，定義成```WSGIApplication```。

> 在執行此專案的時候，注意一下 console output。可以看見：
> 
> ```shell
> #...
> creating context wsgi
> #...
> ```
> wsgi 將在此時被建立。在初始化時（init），由```kwargs```接收。

#### self.switches = {}
建立字典，用來存放 Datapath。```key```為 Datapath 的 ID。

#### wsgi = kwargs['wsgi']
取出 wsgi，並將 Controller（```SimpleSwitchController```） 註冊其中。

```python
wsgi.register(SimpleSwitchController, {simple_switch_instance_name : self})
```

> ```register```的第二個參數是一個字典，用意就是把 Switch 本身傳給 Controller。讓 Controller 可以自由取用 Switch。 

### SwitchFeatures 事件
覆寫```switch_features_handler```，目的是將接收到的 Datapath 存入 ```self.switches``` 供後續使用。
```python
@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		super(SimpleSwitchRest13, self).switch_features_handler(ev)
		datapath = ev.msg.datapath
		self.switches[datapath.id] = datapath
		self.mac_to_port.setdefault(datapath.id, {})
```

### 加入 新增 Flow Entry 函式
接收到新的設備資訊（```entry```）後，將 Entry 新增入 MAC TABLE 中。
> 接收到 Restful ```PUT```時，控制函式將會呼叫此函式，並給予設備資訊（```entry```）和 Datapath ID，供此函式新增 Flow Entry 入指定的 Datapath 中。

```python
#...
def set_mac_to_port(self, dpid, entry):
		mac_table = self.mac_to_port.setdefault(dpid, {})
		datapath = self.switches.get(dpid)

		entry_port = entry['port']
		entry_mac = entry['mac']
		if datapath is not None:
			parser = datapath.ofproto_parser
			if entry_port not in mac_table.values():
				for mac, port in mac_table.items():
					actions = [parser.OFPActionOutput(entry_port)]
					match = parser.OFPMatch(in_port=port, eth_dst=entry_mac)
					self.add_flow(datapath, 1, match, actions)
					
					actions = [parser.OFPActionOutput(port)]
					match = parser.OFPMatch(in_port=entry_port, eth_dst=mac)
					self.add_flow(datapath, 1, match, actions)
				mac_table.update({entry_mac : entry_port})

		return mac_table
#...
```
#### 取得 MAC TABLE 及指定 Datapath 資訊
```python
mac_table = self.mac_to_port.setdefault(dpid, {})
datapath = self.switches.get(dpid)
```

#### 如果指定的 Datapath 存在，且此筆設備資訊（```entry```）是新的。則將它加入 MAC TABLE 中
加入新的設備資訊（```entry```）及原先 MAC TABLE 中的設備資訊之間的 Flow Entry。

```python
# from known device to new device
actions = [parser.OFPActionOutput(entry_port)]
match = parser.OFPMatch(in_port=port, eth_dst=entry_mac)
self.add_flow(datapath, 1, match, actions)

# from new device to known device
actions = [parser.OFPActionOutput(port)]
match = parser.OFPMatch(in_port=entry_port, eth_dst=mac)
self.add_flow(datapath, 1, match, actions)
```
#### 更新 MAC TABLE 並回傳
```python
    mac_table.update({entry_mac : entry_port})
return mac_table
```
## Controller Class
接下來說明，專案中 Controller 的部分。

### 初始化
繼承 WSGI 中的 ```ControllerBase```，並取出 Switch，放入```self.simple_switch_app```中。

```python
#...
class SimpleSwitchController(ControllerBase):

	def __init__(self, req, link, data, **config):
		super(SimpleSwitchController, self).__init__(req, link, data, **config)
		self.simple_switch_app = data[simple_switch_instance_name]
#...
```

### 取得指定 Datapath 的 MAC TABLE 資訊（GET）
透過裝飾器```route```，實現 Restful 機制。讓使用者可以使用```GET```，取得指定 Datapath 的 MAC TABLE 資訊。

```python
	@route('simpleswitch', url, methods=['GET'], requirements={'dpid':dpid_lib.DPID_PATTERN})
	def list_mac_table(self, req, **kwargs):
		simple_switch = self.simple_switch_app
		dpid = dpid_lib.str_to_dpid(kwargs['dpid'])

		if dpid not in simple_switch.mac_to_port:
			return Response(status=404)

		mac_table = simple_switch.mac_to_port.get(dpid, {})
		body = json.dumps(mac_table)

		return Response(content_type='application/json', body=body)
```
#### route 裝飾器

藉由收到不同的 Restful method（```method```）及參數（```requirements```），執行對應的動作。

參數意義如下：

1. ```name```：名稱（可任意輸入）
2. ```path```：此函式對應的 URL
3. ```method```：Restful 對應的方法（預設為```None```）
4. ```requirements```：指定的 URL 參數格式（預設為```None```）

> 在此函式中，```requirements```所接受到的參數為```{'dpid':dpid_lib.DPID_PATTERN}```。其中```dpid_lib.DPID_PATTERN```是參數格式的定義。

#### 取出 Switch 及取出透過```GET```傳入的```dpid```

```python
simple_switch = self.simple_switch_app
dpid = dpid_lib.str_to_dpid(kwargs['dpid'])
```

#### 回傳訊息邏輯
如果指定的 Datapath 不在 Switch 的紀錄中（```mac_to_port```），則回傳 ```http 404```。
如果存在，則將指定的 Datapath 的 MAC TABLE 轉換成```json```格式，並透過```Response```函式回傳。

```python
if dpid not in simple_switch.mac_to_port:
    return Response(status=404)

mac_table = simple_switch.mac_to_port.get(dpid, {})
body = json.dumps(mac_table)

return Response(content_type='application/json', body=body)
```

### 對指定的 Datapath 新增 Flow Entry（PUT）
讓使用者可以使用```PUT```，傳入將設備資訊，並對指定的 Datapath，新增與此設備連接的 Flow Entry。

```python
	@route('simpleswitch', url, methods=['PUT'], requirements={'dpid': dpid_lib.DPID_PATTERN})
	def put_mac_table(self, req, **kwargs):

		simple_switch = self.simple_switch_app
		dpid = dpid_lib.str_to_dpid(kwargs['dpid'])
		new_entry = eval(req.body)

		if dpid not in simple_switch.mac_to_port:
			return Response(status=404)

		try:
			mac_table = simple_switch.set_mac_to_port(dpid, new_entry)
			body = json.dumps(mac_table)
			return Response(content_type='application/json', body=body)
		except Exception as e:
			print(e)
			return Response(status=500)
```

#### 取出```PUT```進入函式的參數
```python
new_entry = eval(req.body)
```
#### 回傳訊息邏輯
如果指定的 Datapath 不在 Switch 的紀錄中（```mac_to_port```），則回傳 ```http 404```。
如果存在，則執行 Switch 中的```set_mac_to_port```函式，將設備資訊新增至指定的 Datapath 中。新增成功後，回傳更新後的 MAC TABLE。

## 與設備連接前的準備

* 將要連接的 Bridge 的 protocols 設定為 Openflow 1.3

> 可透過指令```$ ovs-ofctl -O OpenFlow13 dump-flows <Bridge>```進行確認。

## 啟動
```shell
ryu-manager --verbose ./SimpleSwitchRest13.py
```
執行後：

```shell
$ ryu-manager --verbose SimpleSwitchRest13.py
loading app SimpleSwitchRest13.py
loading app ryu.controller.ofp_handler
creating context wsgi
instantiating app SimpleSwitchRest13.py of SimpleSwitchRest13
instantiating app ryu.controller.ofp_handler of OFPHandler
BRICK SimpleSwitchRest13
  CONSUMES EventOFPSwitchFeatures
  CONSUMES EventOFPPacketIn
BRICK ofp_event
  PROVIDES EventOFPSwitchFeatures TO {'SimpleSwitchRest13': set(['config'])}
  PROVIDES EventOFPPacketIn TO {'SimpleSwitchRest13': set(['main'])}
  CONSUMES EventOFPPortDescStatsReply
  CONSUMES EventOFPHello
  CONSUMES EventOFPErrorMsg
  CONSUMES EventOFPEchoRequest
  CONSUMES EventOFPEchoReply
  CONSUMES EventOFPSwitchFeatures
(1225) wsgi starting up on http://0.0.0.0:8080
connected socket:<eventlet.greenio.base.GreenSocket object at 0x7fecd441a110> address:('192.168.99.100', 50609)
hello ev <ryu.controller.ofp_event.EventOFPHello object at 0x7fecd441ab90>
move onto config mode
EVENT ofp_event->SimpleSwitchRest13 EventOFPSwitchFeatures
switch features ev version=0x4,msg_type=0x6,msg_len=0x20,xid=0xa0209c3,OFPSwitchFeatures(auxiliary_id=0,capabilities=71,datapath_id=1,n_buffers=256,n_tables=254)
move onto main mode
```
其中，可以見到```(1225) wsgi starting up on http://0.0.0.0:8080```。代表已經在 local 端的 8080 port 上開啟服務，Restful 也就是透過這個 port 提供。

## 提供的 API
* 取得指定 Datapath 的 MAC TABLE 資訊（GET）
* 對指定的 Datapath 新增 Flow Entry（PUT）

這兩隻 API 回傳的資料格式皆為```json```。

### 取得指定 Datapath 的 MAC TABLE 資訊（GET）
```
http://<server>:8080/simpleswitch/mactable/<Datapath ID>
```
> 可透過 curl 取得，方法如下：
> ```
> $ curl -X GET http://127.0.0.1:8080/simpleswitch/mactable/<Datapath ID>
> ```

### 對指定的 Datapath 新增 Flow Entry（PUT）
```
http://<server>:8080/simpleswitch/mactable/<Datapath ID>
```


> 可透過 curl 執行，方法如下：
> ```
> $ curl -X PUT -d '{"mac" : <mac address>, "port" : <port number>}' http://<server>:8080/simpleswitch/mactable/<Datapath ID>
> ```

## 參考

[Ryubook](https://osrg.github.io/ryu-book/zh_tw/html/)
