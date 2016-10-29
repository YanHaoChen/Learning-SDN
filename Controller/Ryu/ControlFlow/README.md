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

要對 Switch 新增規則，是需要由 Controller（Ryu）透過傳送```OFPFlowMod```給 Switch，Switch 收到此訊息後，則加入對應的規則。在此建立一個 Function（```add_flow```），讓我們在加入規則時方便一些：

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