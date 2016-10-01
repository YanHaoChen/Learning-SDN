# OpenFlow

基本上在學習 SDN 時，第一個遇到的協定就是 OpenFlow 協定。OpenFlow 的內部架構是由多個單元所組成，並不是一下就可以融會貫通的。但如果是要實作 SDN，其實只需要瞭解實作上最直接會遇到的部分，即可好好使用它。以下也將介紹這一部分：

 
### Flow Table

封包進入 Switch 後，第一個遇到的就是 Flow Table。在 Flow Table 中，存放著封包轉送的規則（Flow Entry）。規則和 Flow Table 的數量，端看管理者的管理邏輯而定，並未強烈規範。如果封包的條件，有對應（Match）到其中一條規則，則依此規則的動作（Action）對此封包進行操作、轉送。

### Flow Entry

Flow Entry 也就是所謂的規則。在規則中，最重要的就是符合條件（Match）及符合後要進行的動作（Action）。在這裡舉個例子：

```python
packet(src=00:00:00:00:00:01,dst=00:00:00:00:00:02)

packet -> flow_table
	1.Flow Entry(match=(src=00:00:00:00:00:01),priority=0,action(output=port_1))
	2.Flow Entry(match=(src=00:00:00:00:00:02),priority=0,action(output=port_2))
	3.Flow Entry(match=(src=00:00:00:00:00:03),priority=0,action(output=port_3))
	4.Flow Entry(match=(src=00:00:00:00:00:01),priority=50,action(output=port_4))

-> port_4
```

在這些 Flow Entry 中，只有 1 跟 4 符合 Match 條件，但又因 4 的優先權（priority）較高，最後選擇 4 這條規則，將封包轉往 port 4。

規則中，還有很多的 Match 條件及 Action 可以使用，但在此就不多作介紹，如想知道更多 Match 條件，可以[點此連結](http://flowgrammable.org/sdn/openflow/classifiers/)，Action則可以[點此連結](http://flowgrammable.org/sdn/openflow/message-layer/action/)，再做進一步的瞭解。
### FlowMod

Controller 向 Switch 下達規則的訊息。在學習使用 Ryu 的時候（在其他種類的 Controller 下，應該也是一樣），一開始就會使用到它，因為要靠它，才能將我們的規則下達至 Switch。以下是在 Ryu 下的例子：

```python
# OpenFlow 1.3
mod = datapath.ofproto_parser.OFPFlowMod(
			datapath=datapath, cookie=0, cookie_mask=0, table_id=table,
			command=datapath.ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
			priority=priority, buffer_id=buffer_id,
			out_port=datapath.ofproto.OFPP_ANY, out_group=datapath.ofproto.OFPG_ANY,
			flags=0, match=match, instructions=inst)

datapath.send_msg(mod)
```

可以發現，要生成一個```OFPFlowMod```（也就是 FlowMod），需要大量的參數，其中也包含了這條規則的 Match 條件及 Action。

> 在 OpenFlow 1.1 後，就將 Action 這個欄位改成 Instruction。但都是用來給定，規則要執行的動作為何。詳細內容，可以參考[此連結](http://flowgrammable.org/sdn/openflow/message-layer/instruction/)。

### FeatureReq - FeatureRes

Switch 與 Controller 之間的通訊。Controller 可以透過此訊息得知道有 Switch 與他連結、取得 Switch 的資訊。在實際的運用上，可以用在**初始化** Switch 的設定。

### PacketIn

有兩種情況會觸發此事件，並將封包轉送至 Controller：

* 封包沒有對應到任何規則
* 封包的 TTL 錯誤

也就是說，當 Switch 遇到不知道怎麼處理的封包，就會轉送 Controller。在實際的運用上，可以利用此事件，進行未知封包的學習。

### PacketOut

可以直接進行封包轉送。以這種方式送出的封包，會直接進行設定的動作（Action）。在實際用途上，遇到未知封包時，最後處理的方式，可能會透過它來進行封包轉送，例如進行 Flooding，或是將封包導向指定的 port 上。

## 進階

[使用 OpenFlow 的 Switch 內部運作方式](https://github.com/imac-cloud/SDN-tutorial/tree/master/Protocols/OpenFlow/OpenFlowInSwitch)

## 參考

[SDN / OpenFlow | Flowgrammable](http://flowgrammable.org/sdn/openflow/)