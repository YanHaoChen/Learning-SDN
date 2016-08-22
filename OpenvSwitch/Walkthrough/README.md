# 熟悉如何使用 Open vSwitch

為了更瞭解 Open vSwitch 的運作模式，所以照著 [官方的 Tutorial](https://github.com/openvswitch/ovs/blob/master/tutorial/Tutorial.md) 做一遍，進而熟悉 Open vSwitch。在官方文件的開始，提到可以使用```ovs-sandbox```進行學習，但感覺上，開一個虛擬機，直接安裝 Open vSwitch 感覺簡單許多，所以在這個部分並沒有照他的方式做，希望將重點集中在對整體的瞭解及指令的操作上。以下將會介紹官方的教學動機，及實際操作過程。

## 動機（官方文件翻譯）

這份教學是為了展示 Open vSwitch flow tables 的能耐。教學將會實際演練在 VLAN 及 access ports 底下的 MAC-learning。除了 Open vSwitch 本身的功能外，我們還會在此探討由 OpenFlow 所提供的兩種實現 Switch 功能的方式：

1. 用一種被動的方式，讓 OpenFlow 的 Controller 實現 MAC learning。每當有新的 MAC 加入 switch 中，或者 MAC 所使用的 switch port 有所搬移，則交由 Controller 對 flow table 進行調整。

2. 使用 "normal" 行為。OpenFlow 將這個行為定義成將封包當做在 "傳統沒有使用 OpenFlow 的 switch" 中傳送。如果一個 flow 使用的是這種行為（normal），其中的封包仍可以在並沒有設定 OpenFlow 的 Switch 中傳送。

每一個方式，都有它的缺陷存在。例如第一種，因為所有的控制都是由 Controller 負責，所以網路的頻寬及延遲成了很需要考量的成本，進一步可以想像 Controller 在控制大量的 switch 時，是相當吃力。也因為全部的控制都仰賴 Controller，所以一旦 Controller 本身出現問題，連帶影響的就是所有被控管的網路。

第二種方式的問題則跟第一種不同。"normal" 行為是被定義的標準，所以在不同廠商的 switch 下，也會產生各自的特性跟如何設定這些特性的差異性問題。另外，第二點，"normal" 行為在 OpenFlow 中運行的效果並不好，因為變成 OpenFlow 需要額外承擔調整自己的行為以符合個別的特性的成本。

## Setup（準備中）

首先開啟安裝好 Open vSwitch 的虛擬機，並下達以下指令：

```bash
$ sudo ovs-vsctl add-br br0 -- set Bridge br0 fail-mode=secure
```

以上指令的意思為：創建一個新的 bridge ```br0```並將```br0```設定為模式 fail-secure。這樣設定的用意，是要讓其 OpenFlow table 一開始就是空的狀況。

> 如果我們不這麼設定，switch 就會在一開始時，加入一個 flow，並以 normal 模式運行（運作方式如動機所提）。

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

> 上面的腳本與官方的有一處差異，也就是多了```type=internal```。如果照著官方的方式，省略```type=internal```，在執行到指令```ovs-ofctl mod-port br0 p$i up```時會發生錯誤：
> 
> ```
> ovs-ofctl: br0: couldn't find port `p1'
> ovs-ofctl: br0: couldn't find port `p2'
> ovs-ofctl: br0: couldn't find port `p3'
> ovs-ofctl: br0: couldn't find port `p4'
> ```

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
$ sudo ovs-appctl ofproto/trace br0 in_port,dl_dst=01:80:c2:00:00:10
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

## 參考

[Multicast_address（wiki）](https://en.wikipedia.org/wiki/Multicast_address)

[ovs-ofctl - administer OpenFlow switches](http://openvswitch.org/support/dist-docs/ovs-ofctl.8.txt)