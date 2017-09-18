# 熟悉如何使用 Open vSwitch

為了更瞭解 Open vSwitch 的運作模式，所以照著 [官方的 Tutorial](https://github.com/openvswitch/ovs/blob/master/Documentation/tutorials/ovs-advanced.rst) 做一遍，進而熟悉 Open vSwitch。在官方文件的開始，提到可以使用```ovs-sandbox```進行學習，但感覺上，開一個虛擬機，直接安裝 Open vSwitch 感覺簡單許多，所以在這個部分並沒有照他的方式做，希望將重點集中在對整體的瞭解及指令的操作上。以下將會介紹官方的教學動機，及實際操作過程。

## 動機（官方文件翻譯）

這份教學是為了展示 Open vSwitch flow tables 的能耐。教學將會實作 VLAN 及 MAC-learning。除了 Open vSwitch 本身的功能外，我們還會在此探討由 OpenFlow 所提供的兩種實現 Switch 功能的方式：

1. 用一種被動的方式，讓 OpenFlow 的 Controller 實現 MAC learning。每當有新的 MAC 加入 switch 中，或者 MAC 所使用的 switch port 有所搬移，則交由 Controller 對 flow table 進行調整。
> 使用 OpenFlow 協定。

2. 使用 "normal" 行為。OpenFlow 將這個行為定義成將封包當做在 "傳統沒有使用 OpenFlow 的 switch" 中傳送。如果一個 flow 使用的是這種行為（normal），其中的封包仍可以在並沒有設定 OpenFlow 的 Switch 中傳送。
> 當一般的 Switch 使用。


每一個方式，都有它的缺陷存在。例如第一種，因為所有的控制都是由 Controller 負責，所以網路的頻寬及延遲成了很需要考量的成本，進一步可以想像 Controller 在控制大量的 switch 時，是相當吃力。也因為全部的控制都仰賴 Controller，所以一旦 Controller 本身出現問題，連帶影響的就是所有被控管的網路。

第二種方式的問題則跟第一種不同。"normal" 行為是被定義的標準，所以在不同廠商的 switch 下，也會產生各自的特性跟如何設定這些特性的差異性問題。另外，第二點，"normal" 行為在 OpenFlow 中運行的效果並不好，因為變成 OpenFlow 需要額外承擔調整自己的行為以符合個別的特性的成本。

## 環境假設條件

為了透過此篇教學，瞭解 Open vSwitch 中的 VLAN-capable 及 MAC-learning。我們建立 4 個代表不同情境的 port 進行實際演練，分別為：

* p1：所有 VLAN 的主幹，配置在 OpenFlow port 1。

* p2：VLAN 20 的 access port，配置在 OpenFlow port 2。

* p3、p4：皆為 VLAN 30 的 access port，分別配置在 OpenFlow 的
port 3 及 port 4 上。

學習、實作的階段又分別為以下五個：

1. Table 0：Admission control.

2. Table 1：VLAN input processing.

3. Table 2：Learn source MAC and VLAN for ingress port.

4. Table 3：Look up learning port for destination MAC and VLAN.

5. Table 4：Output processing.


## Setup

首先開啟安裝好 Open vSwitch 的虛擬機，並下達以下指令：

```bash
$ sudo ovs-vsctl add-br br0 -- set Bridge br0 fail-mode=secure
```

以上指令的意思為：創建一個新的 bridge ```br0```並將```br0```設定為模式 fail-secure。用意是讓 switch 在沒有連接到 controller 的情況下，也不會直接進入 normal 模式。

> 如果我們不這麼設定，switch 就會在一開始時，加入一個 flow，並以 normal 模式運行（運作方式如動機所提）。指令如下：
> ```
> ovs-ofctl add-flow <br> action=NORMAL
> ```

這時候我們可以使用以下指令，確認是否已經將 bridge 建立好了：

```bash
$ sudo ovs-vsctl show
0d257140-0705-4c03-b592-065baf7291c6
    Bridge "br0"
        fail_mode: secure
        Port "br0"
            Interface "br0"
                type: internal
    ovs_version: "2.0.2"
```

現在這個新的 bridge 只有一個 port 也就是```br0```。接下來我們利用 bash script 幫它加入其他 4 個 port 並分別命名```p1```、```p2```、```p3```還有```p4```。首先創一個腳本檔```add4port.sh```：

```bash
#! /bin/bash

for i in 1 2 3 4;
do
        ovs-vsctl add-port br0 p$i -- set Interface p$i ofport_request=$i type=internal
        ovs-ofctl mod-port br0 p$i up
done
```

> 上面的腳本與官方的有一處差異，也就是多了```type=internal```。官方的方式是用 ovs-sandbox，所以沒有使用```type=internal```。而本篇是直接使用，並不是用 ovs-sandbox，所以需要添加。


在完成腳本後，記得開啟執行權限：

```bash
$ sudo chmod 700 add4port.sh
$ sudo ./add4port.sh
```

執行完後，可以再透過```sudo ovs-vsctl show```，確定目前```br0```的狀況：

```bash
$ sudo ovs-vsctl show
0d257140-0705-4c03-b592-065baf7291c6
    Bridge "br0"
        fail_mode: secure
        Port "p1"
            Interface "p1"
                type: internal
        Port "p2"
            Interface "p2"
                type: internal
        Port "p4"
            Interface "p4"
                type: internal
        Port "p3"
            Interface "p3"
                type: internal
        Port "br0"
            Interface "br0"
                type: internal
    ovs_version: "2.0.2"
```

在加入 port 的時候，我們是使用指令```ovs-vsctl```。其中設定的```ofport_request```是為了指定各個 port 在 OpenFlow 中對應的 port。

> 設定```ofport_request```是可以忽略的動作，因為可以交由 Open vSwitch 幫我們自動配對 OpenFlow 中對應的 port。

指令```ovs-ofctl```在此負責幫忙開啟各 port 的網路介面，就像是使用```ifconfig up```一樣。（網路介面一開始預設是關閉的）

現在可以利用指令```ovs-ofctl show <bridge>```，來確定是否設定成功：

```bash
$ sudo ovs-ofctl show br0
OFPT_FEATURES_REPLY (xid=0x2): dpid:0000021e35fa4e4a
n_tables:254, n_buffers:256
capabilities: FLOW_STATS TABLE_STATS PORT_STATS QUEUE_STATS ARP_MATCH_IP
actions: OUTPUT SET_VLAN_VID SET_VLAN_PCP STRIP_VLAN SET_DL_SRC SET_DL_DST SET_NW_SRC SET_NW_DST SET_NW_TOS SET_TP_SRC SET_TP_DST ENQUEUE
 1(p1): addr:3a:96:bd:20:9d:e3
     config:     0
     state:      0
     speed: 0 Mbps now, 0 Mbps max
 2(p2): addr:72:6b:3a:2b:02:ba
     config:     0
     state:      0
     speed: 0 Mbps now, 0 Mbps max
 3(p3): addr:ce:d0:4c:da:e1:2b
     config:     0
     state:      0
     speed: 0 Mbps now, 0 Mbps max
 4(p4): addr:e2:33:98:b9:5c:47
     config:     0
     state:      0
     speed: 0 Mbps now, 0 Mbps max
 LOCAL(br0): addr:02:1e:35:fa:4e:4a
     config:     0
     state:      0
     speed: 0 Mbps now, 0 Mbps max
OFPT_GET_CONFIG_REPLY (xid=0x4): frags=normal miss_send_len=0
```

目前我們並未做任何有關 VLANs 或者 MAC learning 的相關設定。因為我們將親自執行這些有關於 flow table 的操作。

## Implementing Table 0: Admission control

Table 0 為封包進入 switch 的第一站。在此，我們就可以加入一些條件，進行封包過濾。以下例子為過濾所有的群播封包的範例：

```bash
$ sudo ovs-ofctl add-flow br0 \
"table=0, dl_src=01:00:00:00:00:00/01:00:00:00:00:00, actions=drop"
```
再來另個例子，過濾生成樹協定（STP）的群播封包：

```bash
$ sudo ovs-ofctl add-flow br0 \
"table=0, dl_dst=01:80:c2:00:00:00/ff:ff:ff:ff:ff:f0, actions=drop"
```
> 其他協定的封包，也可以透過此方式，進行過濾。

接下來，我們需要利用一個優先權比預設值低的 flow。如此，如果進來的封包都不符合過濾的條件，封包就會符合此 flow 的條件，並將封包往下轉送到 OpenFlow 的 table 1，進行下一步的處理：

```bash
$ sudo ovs-ofctl add-flow br0 "table=0, priority=0, actions=resubmit(,1)"
```

透過指令```sudo ovs-ofctl dump-flows <bridge>```來確定是否將 flow 加入成功：

```bash
$ sudo ovs-ofctl dump-flows br0
NXST_FLOW reply (xid=0x4):
 cookie=0x0, duration=21.807s, table=0, n_packets=0, n_bytes=0, idle_age=21, priority=0 actions=resubmit(,1)
 cookie=0x0, duration=96.88s, table=0, n_packets=0, n_bytes=0, idle_age=96, dl_src=01:00:00:00:00:00/01:00:00:00:00:00 actions=drop
 cookie=0x0, duration=62.599s, table=0, n_packets=0, n_bytes=0, idle_age=62, dl_dst=01:80:c2:00:00:00/ff:ff:ff:ff:ff:f0 actions=drop
```

### Testing Table 0

如果我們利用 Open vSwitch 建立一個實體或虛擬的 switch，我們很自然的會想要測試它是否可以正常工作。可以測試網路狀況的工具有很多，像是```ping```、```tcpdump```，甚至是```Scapy```。但這些工具並沒有辦法明確的測試出 Open vSwitch 的狀況是否符合預期。

這時候，如果要想要測試 switch 的狀況，有一個更好的選擇，那就是```ofproto/trace```。接下來將展示這套工具的使用方式：

### EXAMPLE 1

先直接跑一下這項指令看看：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=1,dl_dst=01:80:c2:00:00:10
```
跑完後，預計你可以看到這樣的輸出：

```bash
Flow: metadata=0,in_port=1,vlan_tci=0x0000,dl_src=00:00:00:00:00:00,dl_dst=01:80:c2:00:00:05,dl_type=0x0000
Rule: table=0 cookie=0 dl_dst=01:80:c2:00:00:00/ff:ff:ff:ff:ff:f0
OpenFlow actions=drop

Final flow: unchanged
Relevant fields: skb_priority=0,in_port=1,dl_src=00:00:00:00:00:00/01:00:00:00:00:00,dl_dst=01:80:c2:00:00:00/ff:ff:ff:ff:ff:f0,dl_type=0x0000,nw_frag=no
Datapath actions: drop
```
輸出的意義如下：

* 第一行：為傳入的封包狀況。
* 第二行：對應到的規則。
* 第三行：執行的動作。

### EXAMPLE 2

接下來試試看其他封包條件：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=1,dl_dst=01:80:c2:00:00:10
```

預期可以看到的輸出：

```bash
Flow: metadata=0,in_port=1,vlan_tci=0x0000,dl_src=00:00:00:00:00:00,dl_dst=01:80:c2:00:00:10,dl_type=0x0000
Rule: table=0 cookie=0 priority=0
OpenFlow actions=resubmit(,1)

       	Resubmitted flow: unchanged
       	Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       	Resubmitted  odp: drop
       	No match

Final flow: unchanged
Relevant fields: skb_priority=0,in_port=1,dl_src=00:00:00:00:00:00/01:00:00:00:00:00,dl_dst=01:80:c2:00:00:10/ff:ff:ff:ff:ff:f0,dl_type=0x0000,nw_frag=no
Datapath actions: drop
```

我們可以發現此封包並未 match 到任何我們設定要過濾的情況，因此對應的條件轉向較低優先權的 flow，並對應到```table=0 cookie=0 priority=0```這條規則，將封包```resubmit```至 table 1。但因為我們並未加入 table 1，所以到最後，我們還是將此封包進行```drop```動作。

## Implementing Table 1: VLAN Input Processing

當封包可以到達```Table 1```時，代表此封包已經通過```Table 0```的過濾。```Table 1```的目的就在於過濾已包含 VLAN header 的封包，及幫未包含 VLAN header 的封包標註上我們將要賦予它的 VLAN number，並往下一個階段轉送。

首先，我們先加入最低優先權的 flow。此 flow 的用意就在於「如果沒有符合過濾標準，則將封包丟棄」，也可以說是「預設處理封包的方式為丟棄」：

```bash
ovs-ofctl add-flow br0 "table=1, priority=0, actions=drop"
```

因為要將```port p1```當作 VLAN 的主幹，所以不管流入的封包是否有 VLAN hander 或者他是屬於那個 VLAN ，都會將收到的封包往下一階段轉送。因此，我們加入規則：

```bash
$ sudo ovs-ofctl add-flow br0 \
"table=1, proirity=99, in_port=1, actions=resubmit(,2)"
```

其他的 port 我們則是希望將沒有標明 VLAN header 的封包，進行標注 VLAN number，再讓此封包往下一階段轉送：

```bash
$ sudo ovs-ofctl add-flows br0 - << 'EOF'
table=1, priority=99, in_port=2, vlan_tci=0, actions=mod_vlan_vid:20, resubmit(,2)
table=1, priority=99, in_port=3, vlan_tci=0, actions=mod_vlan_vid:30, resubmit(,2)
table=1, priority=99, in_port=4, vlan_tci=0, actions=mod_vlan_vid:30, resubmit(,2)
EOF
```

在這個階段我們並未寫任何關於 match 802.1Q （VLAN）的對應規則，所以只要在這個階段收到含有 VLAN header 資訊的封包，我們則會進行```drop```（除了```port 1```）。

> 設定過濾規則時，也可以使用```vlan_tci=0/0xfff```替換```vlan_tci=0```。

### Testing Table 1

再次利用```ofproto/trace```，測試以上的設定。

### EXAMPLE 1: Packect on Trunk Port

首先，測試主幹```port 1```：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=1,vlan_tci=5
Flow: metadata=0,in_port=1,vlan_tci=0x0005,dl_src=00:00:00:00:00:00,dl_dst=00:00:00:00:00:00,dl_type=0x0000
Rule: table=0 cookie=0 priority=0
OpenFlow actions=resubmit(,1)

       	Resubmitted flow: unchanged
       	Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       	Resubmitted  odp: drop
       	Rule: table=1 cookie=0 priority=99,in_port=1
       	OpenFlow actions=resubmit(,2)

       		Resubmitted flow: unchanged
       		Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       		Resubmitted  odp: drop
       		No match

Final flow: unchanged
Relevant fields: skb_priority=0,in_port=1,dl_src=00:00:00:00:00:00/01:00:00:00:00:00,dl_dst=00:00:00:00:00:00/ff:ff:ff:ff:ff:f0,dl_type=0x0000,nw_frag=no
Datapath actions: drop
```

封包就如預期，很順暢的一路從```table 0```轉送到```table 2```（即使包含 VLAN header），但也因為```table 2```尚無規則，所以最後還是被```drop```。 


### EXAMPLE 2: Valid Packet on Access Port

接下來，我們將傳送一個預計可以通過過濾的封包（不包含 VLAN header）進入```port 2```進行測試：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=2
Flow: metadata=0,in_port=2,vlan_tci=0x0000,dl_src=00:00:00:00:00:00,dl_dst=00:00:00:00:00:00,dl_type=0x0000
Rule: table=0 cookie=0 priority=0
OpenFlow actions=resubmit(,1)

       	Resubmitted flow: unchanged
       	Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       	Resubmitted  odp: drop
       	Rule: table=1 cookie=0 priority=99,in_port=2,vlan_tci=0x0000
       	OpenFlow actions=mod_vlan_vid:20,resubmit(,2)

       		Resubmitted flow: metadata=0,in_port=2,dl_vlan=20,dl_vlan_pcp=0,dl_src=00:00:00:00:00:00,dl_dst=00:00:00:00:00:00,dl_type=0x0000
       		Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       		Resubmitted  odp: drop
       		No match

Final flow: unchanged
Relevant fields: skb_priority=0,in_port=2,vlan_tci=0x0000,dl_src=00:00:00:00:00:00/01:00:00:00:00:00,dl_dst=00:00:00:00:00:00/ff:ff:ff:ff:ff:f0,dl_type=0x0000,nw_frag=no
Datapath actions: drop
```

是照著我們預想的沒錯。從第二個```Resubmitted flow```中，可以觀察到我們已經將封包標註成```VLAN 20```。

### EXAMPLE 3: Invalid Packet on Access Port

接下來，我們將傳送一個預計無法通過過濾的封包（包含 VLAN header）進入```port 2```進行測試：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=2,vlan_tci=5
Flow: metadata=0,in_port=2,vlan_tci=0x0005,dl_src=00:00:00:00:00:00,dl_dst=00:00:00:00:00:00,dl_type=0x0000
Rule: table=0 cookie=0 priority=0
OpenFlow actions=resubmit(,1)

       	Resubmitted flow: unchanged
       	Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       	Resubmitted  odp: drop
       	Rule: table=1 cookie=0 priority=0
       	OpenFlow actions=drop

Final flow: unchanged
Relevant fields: skb_priority=0,in_port=2,vlan_tci=0x0005,dl_src=00:00:00:00:00:00/01:00:00:00:00:00,dl_dst=00:00:00:00:00:00/ff:ff:ff:ff:ff:f0,dl_type=0x0000,nw_frag=no
Datapath actions: drop
```

此封包也在我們的預想範圍內被```drop```了。其對應到的規則```Rule: table=1 cookie=0 priority=0```，也就是我們在```table 1```中，設定的「預設處理方式」(```drop```)。

## Implementing Table 2: MAC+VLAN Learning for Ingress Port

在此階段，我們將實作在 Open vSwitch 中，VLAN 的 MAC address 學習，是怎運作的。要完成這件事，其實只需要加入一個規則：

```bash
sudo ovs-ofctl add-flow br0 \
"table=2 actions=learn(table=10,NXM_OF_VLAN_TCI[0..11], \
NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[], \
load:NXM_OF_IN_PORT[]->NXM_NX_REG0[0..15]), \
resubmit(,3)"
```

使用```learn```action，可以指定 table 來記錄進行學習後，所產生的規則。在此，我們利用```learn```讓```table 10```學習 VLAN 所需要的 MAC learning 規則。以下將介紹各參數的意義：

```bash
table=10

    將 table 10 設定為給 VLAN 進行 MAC learning 的 table。

NXM_OF_VLAN_TCI[0..11]

   將 VLAN ID 視為其中一個 match 條件，進而區分不同的 VLAN。

NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[]

   將得到的封包的來源位置，也當作一個 match 條件。但將項目從“來源”改成“目的地”。其目的，是要讓同一個 VLAN 內的其他主機，要將封包傳送給此主機時（屆時，封包的目的地位置，將是此封包的來源位置），能 match 到此規則。
   
load:NXM_OF_IN_PORT[]->NXM_NX_REG0[0..15]

   記錄下，如有封包 match 到此規則後，要轉送到的 port，並儲存在 resgister 0 中。
```

> 在現實狀況下使用```learn```actcion 基本上還需要另外兩項設定條件，分別為：
> 
> * hard_timeout：如果在合理的間隔時間內，都未有新的封包來至於特定的來源，則進行重新學習。
> * Flow_Table：對 flow table 設定使用量限制。


關於```table 2```的運作原因，如果沒辦法一下子會意過來，在學習```Table 3```的時候，會有很好的例子，解釋這件事。可以先保有一個觀念：```table 2```的運作，完全是為了讓同 VLAN 內的其他主機，找到目前發送封包供```table 2```進行學習的主機。 


### Testing Table 2

接下來，進行對這些規則的測試。

### EXAMPLE 1

首先，測試這條指令：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=1,vlan_tci=20,dl_src=50:00:00:00:00:01 -generate
Flow: metadata=0,in_port=1,vlan_tci=0x0014,dl_src=50:00:00:00:00:01,dl_dst=00:00:00:00:00:00,dl_type=0x0000
Rule: table=0 cookie=0 priority=0
OpenFlow actions=resubmit(,1)

       	Resubmitted flow: unchanged
       	Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       	Resubmitted  odp: drop
       	Rule: table=1 cookie=0 priority=99,in_port=1
       	OpenFlow actions=resubmit(,2)

       		Resubmitted flow: unchanged
       		Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       		Resubmitted  odp: drop
       		Rule: table=2 cookie=0
       		OpenFlow actions=learn(table=10,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:NXM_OF_IN_PORT[]->NXM_NX_REG0[0..15]),resubmit(,3)

       			Resubmitted flow: unchanged
       			Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       			Resubmitted  odp: drop
       			No match

Final flow: unchanged
Relevant fields: skb_priority=0,in_port=1,vlan_tci=0x0014/0x0fff,dl_src=50:00:00:00:00:01,dl_dst=00:00:00:00:00:00/ff:ff:ff:ff:ff:f0,dl_type=0x0000,nw_frag=no
Datapath actions: drop
```

可以發現這個封包有```match```到我們設定的規則（```OpenFlow actions=learn```）。但這裡並沒有詳述```match```後的動作，也就是學習的部分。

> 請注意，這個封包設定的其中一個條件是```dl_src=50:00:00:00:00:01```。此條件也將會是驗證我們的設定的一個重點（```NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[]```）。

這裡使用到之前沒有用到的```-generate```。是因為一般來說，```ofproto/trace```並未真的傳送出封包，但今天我們想看到學習的結果，也就會需要一個真的有傳入的封包，觸發學習的動作。現在真的有封包傳入了，所以我們可以觀察一下```table 10```內的學習結果：

```bash
$ sudo ovs-ofctl dump-flows br0 table=10
NXST_FLOW reply (xid=0x4):
 cookie=0x0, duration=1022.426s, table=10, n_packets=0, n_bytes=0, idle_age=1022, vlan_tci=0x0014/0x0fff,dl_dst=50:00:00:00:00:01 actions=load:0x1->NXM_NX_REG0[0..15]
```
從中可以發現，現在```table 10```多了一條規則。match 條件為：VLAN 20 上（```vlan_tci=0x0014/0x0fff```以 16 進制表示），且```dl_dst```同於當初封包的```dl_src```。最後，表明 match 到此規則後，要將封包轉送至 port 1（```load:0x1->NXM_NX_REG0[0..15]```）。

### EXAMPLE 2

接下來第二項測試，放入與先前一個封包有相同的 MAC 及 VLAN 的封包（這次的```in_port```為 port 2，所以照先前的設定，我們並不需要附上此封包是在那個 VLAN，```table 1```中的規則，將會幫我們處理這件事情）：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=2,dl_src=50:00:00:00:00:01 -generate
Flow: metadata=0,in_port=2,vlan_tci=0x0000,dl_src=50:00:00:00:00:01,dl_dst=00:00:00:00:00:00,dl_type=0x0000
Rule: table=0 cookie=0 priority=0
OpenFlow actions=resubmit(,1)

       	Resubmitted flow: unchanged
       	Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       	Resubmitted  odp: drop
       	Rule: table=1 cookie=0 priority=99,in_port=2,vlan_tci=0x0000
       	OpenFlow actions=mod_vlan_vid:20,resubmit(,2)

       		Resubmitted flow: metadata=0,in_port=2,dl_vlan=20,dl_vlan_pcp=0,dl_src=50:00:00:00:00:01,dl_dst=00:00:00:00:00:00,dl_type=0x0000
       		Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       		Resubmitted  odp: drop
       		Rule: table=2 cookie=0
       		OpenFlow actions=learn(table=10,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:NXM_OF_IN_PORT[]->NXM_NX_REG0[0..15]),resubmit(,3)

       			Resubmitted flow: unchanged
       			Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       			Resubmitted  odp: drop
       			No match

Final flow: unchanged
Relevant fields: skb_priority=0,in_port=2,vlan_tci=0x0000,dl_src=50:00:00:00:00:01,dl_dst=00:00:00:00:00:00/ff:ff:ff:ff:ff:f0,dl_type=0x0000,nw_frag=no
Datapath actions: drop
```

接下來，我們再看看```table 10```中的規則：

```bash
$ sudo ovs-ofctl dump-flows br0 table=10
NXST_FLOW reply (xid=0x4):
 cookie=0x0, duration=6959.829s, table=10, n_packets=0, n_bytes=0, idle_age=6959, hard_age=472, vlan_tci=0x0014/0x0fff,dl_dst=50:00:00:00:00:01 actions=load:0x2->NXM_NX_REG0[0..15]
```

我們可以發現，此規則被做了一些修改：```actions=load:0x2->NXM_NX_REG0[0..15]```。如我們所預期，最後會轉送出去的 port 從 port 1 改至 port 2。

### Implementing Table 3: Look Up Destination Port

在這個階段，我們將封包導向```table 10```，讓封包依學習的結果，
在```register 0```中，記錄此封包需要轉送至哪一個 port。記錄完後，再進一步轉送至```table 4```，進行最後的封包配送。

在此，我們只需要加入一個規則：

```bash
$ sudo ovs-ofctl add-flow br0 \
"table=3 priority=50 actions=resumbit(,10), resubmit(,4)"
```

封包經過```table 10```後，```register 0```只會有兩結果。第一種，找到將要轉送的 port number，並記錄在其中。第二種，則是在```table 10```中，找不到可以```match```的規則，```register 0```中記錄的數值就會為```0```。最後，轉往```table 4```進行最後處理。

> ```register 0```所存放的數值是在下一個階段執行上，很重要的判斷依據。如果不是```0```就可以得知要轉送至哪一個 port。如果是```0```，則代表可能需要進行```flooding```。

在此，為了避免群播和廣播封包進入```table 10```中，我們可以在```table 3```加上一層過濾：

```bash
$ sudo ovs-ofctl add-flow br0 \
"table=3 priority=99 dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 \
actions=resubmit(,4)"
```

> 這層過濾，其實會是多餘的。因爲在```table 0```中就將來源為廣播及群播的封包過濾掉了。所以在```table 10```中，也不會有跟廣播及群播相關的規則存在。

### Testing Table 3

接下來進行 Table 3 的測試。

### EXAMPLE

在此，我們下指令，觸發 Open vSiwtch 進行學習。

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=1,dl_vlan=20,dl_src=f0:00:00:00:00:01,dl_dst=90:00:00:00:00:01 -generate
Flow: metadata=0,in_port=1,dl_vlan=20,dl_vlan_pcp=0,dl_src=f0:00:00:00:00:01,dl_dst=90:00:00:00:00:01,dl_type=0x0000
Rule: table=0 cookie=0 priority=0
OpenFlow actions=resubmit(,1)

       	Resubmitted flow: unchanged
       	Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       	Resubmitted  odp: drop
       	Rule: table=1 cookie=0 priority=99,in_port=1
       	OpenFlow actions=resubmit(,2)

       		Resubmitted flow: unchanged
       		Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       		Resubmitted  odp: drop
       		Rule: table=2 cookie=0
       		OpenFlow actions=learn(table=10,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:NXM_OF_IN_PORT[]->NXM_NX_REG0[0..15]),resubmit(,3)

       			Resubmitted flow: unchanged
       			Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       			Resubmitted  odp: drop
       			Rule: table=3 cookie=0 priority=50
       			OpenFlow actions=resubmit(,10),resubmit(,4)

       				Resubmitted flow: unchanged
       				Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       				Resubmitted  odp: drop
       				No match

       				Resubmitted flow: unchanged
       				Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       				Resubmitted  odp: drop
       				No match

Final flow: unchanged
Relevant fields: skb_priority=0,in_port=1,vlan_tci=0x0014/0x0fff,dl_src=f0:00:00:00:00:01,dl_dst=90:00:00:00:00:01,dl_type=0x0000,nw_frag=no
Datapath actions: drop
```
從中我們可以發現，在轉往```table 10```後的狀況是```No match```。也就是說，```table 10```中並沒符合```dl_dst=90:00:00:00:00:01```這項條件的規則。

但也因為```f0:00:00:00:00:01```這台主機傳送了這個封包，所以 Open vSwitch 將進行學習，並學習結果記錄在```table 10```中：

```bash
$ sudo ovs-ofctl dump-flows br0 table=10
NXST_FLOW reply (xid=0x4):
 cookie=0x0, duration=2414.851s, table=10, n_packets=0, n_bytes=0, idle_age=2414, vlan_tci=0x0014/0x0fff,dl_dst=f0:00:00:00:00:01 actions=load:0x1->NXM_NX_REG0[0..15]
...
```

接下來，我們加入另一個封包，來試試看如果封包要傳送到的主機存在於 learing table 中，會發生什麼事：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=2,dl_src=90:00:00:00:00:01,dl_dst=f0:00:00:00:00:01 -generate
Flow: metadata=0,in_port=2,vlan_tci=0x0000,dl_src=90:00:00:00:00:01,dl_dst=f0:00:00:00:00:01,dl_type=0x0000
Rule: table=0 cookie=0 priority=0
OpenFlow actions=resubmit(,1)

       	Resubmitted flow: unchanged
       	Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       	Resubmitted  odp: drop
       	Rule: table=1 cookie=0 priority=99,in_port=2,vlan_tci=0x0000
       	OpenFlow actions=mod_vlan_vid:20,resubmit(,2)

       		Resubmitted flow: metadata=0,in_port=2,dl_vlan=20,dl_vlan_pcp=0,dl_src=90:00:00:00:00:01,dl_dst=f0:00:00:00:00:01,dl_type=0x0000
       		Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       		Resubmitted  odp: drop
       		Rule: table=2 cookie=0
       		OpenFlow actions=learn(table=10,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:NXM_OF_IN_PORT[]->NXM_NX_REG0[0..15]),resubmit(,3)

       			Resubmitted flow: unchanged
       			Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       			Resubmitted  odp: drop
       			Rule: table=3 cookie=0 priority=50
       			OpenFlow actions=resubmit(,10),resubmit(,4)

       				Resubmitted flow: unchanged
       				Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       				Resubmitted  odp: drop
       				Rule: table=10 cookie=0 vlan_tci=0x0014/0x0fff,dl_dst=f0:00:00:00:00:01
       				OpenFlow actions=load:0x1->NXM_NX_REG0[0..15]

       				Resubmitted flow: reg0=0x1,metadata=0,in_port=2,dl_vlan=20,dl_vlan_pcp=0,dl_src=90:00:00:00:00:01,dl_dst=f0:00:00:00:00:01,dl_type=0x0000
       				Resubmitted regs: reg0=0x1 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       				Resubmitted  odp: drop
       				No match

Final flow: unchanged
Relevant fields: skb_priority=0,in_port=2,vlan_tci=0x0000,dl_src=90:00:00:00:00:01,dl_dst=f0:00:00:00:00:01,dl_type=0x0000,nw_frag=no
Datapath actions: drop
```

這次轉送到```table 10```之後，就不再是回應```No match```，而是找到對應的規則，也代表成功的進行學習。另外一點，可以注意的是，之後轉送到```table 4```中，雖然因為```table 4```目前並沒有建立任何規則，而被```drop```，但```Resubmitted regs```的```reg0```已經悄悄地變成```0x1```了。

## Implementing Table 4: Output Processing

在此，就是最後的輸出部分了。輸出的依據，也就像是在```table 3```所提到的，是依據```register 0```所存放的數值所決定（送至指定的 port 或者 進行 flooding）。

首先，配合```reg0```加入符合轉送至主幹的規則：

```bash
$ sudo ovs-ofctl add-flow br0 "table=4 reg0=1 actions=1"
```

接下來，是非主幹的部分。在這一部分，在依```reg0```轉送至各別的 access port 前，會先將封包的 VLAN header 去除，再進行轉送。所以規則是這麼下的：

```bash
$ sudo ovs-ofctl add-flows br0 - << 'EOF'
table=4 reg0=2 actions=strip_vlan,2
table=4 reg0=3 actions=strip_vlan,3
table=4 reg0=4 actions=strip_vlan,4
EOF
```

最後，就是遇到未知封包時，對應的 VLAN 要進行```flooding```或者直接丟回主幹的部分：

```bash
$ sudo ovs-ofctl add-flows br0 - << 'EOF'
table=4 reg0=0 priority=99 dl_vlan=20 actions=1,strip,2
table=4 reg0=0 priority=99 dl_vlan=30 actions=1,strip,3,4
table=4 reg0=0 priority=50 actions=1
EOF
```
> 提醒：我們的規則是建立在 OpenFlow 協定上，所以封包是不會回送到原先送出的 port 上。

### Testing Table 4

接下來，測試我們對```Table 4```設定的規則。

> 以下的測試，雖然```Rule```及```OpenFlow actions```對應上並無問題，但最後```Datapath actions```所輸出的 port number 卻在預想之外。目前對此並不確切了解是為什麼，只能推估是 OVS 認定原環境下的 Interface 已使用了第一個 port 所以自行將 OVS 下的 port ，從第二個 port 開始放置，造成意料之外的結果。

### EXAMPLE 1: Broadcast, Multicast, and Unknown Destination

* 由```port 1```傳入一個廣播封包至```VLAN 30```：

> 在此，希望專注在封包的轉送上，所以並沒有加入```-generate```。下一個部分的測試，會專注於 MAC learning，也才會用到它。


```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=1,dl_dst=ff:ff:ff:ff:ff:ff,dl_vlan=30
Flow: 
...
       				Resubmitted flow: unchanged
       				Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       				Resubmitted  odp: drop
       				Rule: table=4 cookie=0 priority=99,reg0=0x0,dl_vlan=30
       				OpenFlow actions=output:1,strip_vlan,output:3,output:4
       				skipping output to input port

Final flow: metadata=0,in_port=1,vlan_tci=0x0000,dl_src=00:00:00:00:00:00,dl_dst=ff:ff:ff:ff:ff:ff,dl_type=0x0000
Relevant fields: skb_priority=0,in_port=1,dl_vlan=30,dl_vlan_pcp=0,dl_src=00:00:00:00:00:00,dl_dst=ff:ff:ff:ff:ff:f0/ff:ff:ff:ff:ff:f0,dl_type=0x0000,nw_frag=no
Datapath actions: pop_vlan,4,5
```
由以上的資訊，可以確定如我們的預期，對```VLAN 30```進行廣播（```OpenFlow actions=output:1,strip_vlan,output:3,output:4```），並略過將封包傳送到來源的動作（```skipping output to input port```）。

* 由```port 3```傳入一個廣播封包：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=3,dl_dst=ff:ff:ff:ff:ff:ff
Flow: 
...
       				Resubmitted flow: unchanged
       				Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       				Resubmitted  odp: drop
       				Rule: table=4 cookie=0 priority=99,reg0=0x0,dl_vlan=30
       				OpenFlow actions=output:1,strip_vlan,output:3,output:4
       				skipping output to input port

Final flow: metadata=0,in_port=3,vlan_tci=0x0000,dl_src=00:00:00:00:00:00,dl_dst=ff:ff:ff:ff:ff:ff,dl_type=0x0000
Relevant fields: skb_priority=0,in_port=3,vlan_tci=0x0000,dl_src=00:00:00:00:00:00,dl_dst=ff:ff:ff:ff:ff:f0/ff:ff:ff:ff:ff:f0,dl_type=0x0000,nw_frag=no
Datapath actions: push_vlan(vid=30,pcp=0),2,pop_vlan,5
```
也因為是從 access port 進入，因此與剛剛的測試有些不同。在此，先加上了 VLAN（```push_vlan(vid=30,pcp=0)```），在進行接下來的廣播。

### EXAMPLE 2: MAC Learing

接下來，測試 MAC learing 的成果。在此，把```port 1```當成主機```10:00:00:00:00:01```，並將封包傳送至主機```20:00:00:00:00:01```，讓 OVS 進行學習：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=1,dl_vlan=30,dl_src=10:00:00:00:00:01,dl_dst=20:00:00:00:00:01 -generate
Flow: 
...
       				Resubmitted flow: unchanged
       				Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       				Resubmitted  odp: drop
       				Rule: table=4 cookie=0 priority=99,reg0=0x0,dl_vlan=30
       				OpenFlow actions=output:1,strip_vlan,output:3,output:4
       				skipping output to input port

Final flow: metadata=0,in_port=1,vlan_tci=0x0000,dl_src=10:00:00:00:00:01,dl_dst=20:00:00:00:00:01,dl_type=0x0000
Relevant fields: skb_priority=0,in_port=1,dl_vlan=30,dl_vlan_pcp=0,dl_src=10:00:00:00:00:01,dl_dst=20:00:00:00:00:01,dl_type=0x0000,nw_frag=no
Datapath actions: pop_vlan,4,5
```
執行的結果跟剛剛很像，因為並未在```table 10```中，找到封包要傳往的主機```10:00:00:00:00:01```，因此進行廣播的動作。

接下來，將```port 4```當成主機```10:00:00:00:00:01```，將封包傳往```20:00:00:00:00:01```：

```bash
$ sudo ovs-appctl ofproto/trace br0 in_port=4,dl_src=20:00:00:00:00:01,dl_dst=10:00:00:00:00:01 -generate
Flow: 
...
       			OpenFlow actions=resubmit(,10),resubmit(,4)

       				Resubmitted flow: unchanged
       				Resubmitted regs: reg0=0x0 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       				Resubmitted  odp: drop
       				Rule: table=10 cookie=0 vlan_tci=0x001e/0x0fff,dl_dst=10:00:00:00:00:01
       				OpenFlow actions=load:0x1->NXM_NX_REG0[0..15]

       				Resubmitted flow: reg0=0x1,metadata=0,in_port=4,dl_vlan=30,dl_vlan_pcp=0,dl_src=20:00:00:00:00:01,dl_dst=10:00:00:00:00:01,dl_type=0x0000
       				Resubmitted regs: reg0=0x1 reg1=0x0 reg2=0x0 reg3=0x0 reg4=0x0 reg5=0x0 reg6=0x0 reg7=0x0
       				Resubmitted  odp: drop
       				Rule: table=4 cookie=0 reg0=0x1
       				OpenFlow actions=output:1

Final flow: unchanged
Relevant fields: skb_priority=0,in_port=4,vlan_tci=0x0000,dl_src=20:00:00:00:00:01,dl_dst=10:00:00:00:00:01,dl_type=0x0000,nw_frag=no
Datapath actions: push_vlan(vid=30,pcp=0),2
```

從以上的資訊，我們可以發現學習是成功的。在轉往```table 10```後，```match```到規則```Rule: table=10 cookie=0 vlan_tci=0x001e/0x0fff,dl_dst=10:00:00:00:00:01```，也就是上一個封包讓 OVS 所學習到的主機位置，並成功傳送目的主機（```Datapath actions: push_vlan(vid=30,pcp=0),2```）。結束這個測試，也代表了完成 OVS 下的 VLAN 實作方式。

## 參考

[ovs/Tutorial](https://github.com/openvswitch/ovs/blob/master/tutorial/)

[Multicast_address（wiki）](https://en.wikipedia.org/wiki/Multicast_address)

[ovs-ofctl - administer OpenFlow switches](http://openvswitch.org/support/dist-docs/ovs-ofctl.8.txt)
