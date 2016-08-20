# 熟悉如何使用 Open vSwitch

為了更瞭解 Open vSwitch 的運作模式，所以照著 [官方的 Tutorial](https://github.com/openvswitch/ovs/blob/master/tutorial/Tutorial.md) 做一遍，進而熟悉 Open vSwitch。在官方文件的開始，提到可以使用```ovs-sandbox```進行學習，但感覺上，開一個虛擬機，直接安裝 Open vSwitch 感覺簡單許多，所以在這個部分並沒有照他的方式做，希望將重點集中在對整體的瞭解及指令的操作上。以下將會介紹官方的教學動機，及實際操作過程。

## 動機（官方文件翻譯）

這份教學是為了展示 Open vSwitch flow tables 的能耐。教學將會實際演練在 VLAN 及 access ports 底下的 MAC-learning。除了 Open vSwitch 本身的功能外，我們還會在此探討由 OpenFlow 所提供的兩種實現 Switch 功能的方式：

1. 用一種被動的方式，讓 OpenFlow 的 Controller 實現 MAC learning。每當有新的 MAC 加入 switch 中，或者 MAC 所使用的 switch port 有所搬移，則交由 Controller 對 flow table 進行調整。

2. 使用 "normal" 行為。OpenFlow 將這個行為定義成將封包當做在 "傳統沒有使用 OpenFlow 的 switch" 中傳送。如果一個 flow 使用的是這種行為（normal），其中的封包仍可以在並沒有設定 OpenFlow 的 Switch 中傳送。

每一個方式，都有它的缺陷存在。例如第一種，因為所有的控制都是由 Controller 負責，所以網路的頻寬及延遲成了很需要考量的成本，進一步可以想像 Controller 在控制大量的 switch 時，是相當吃力。也因為全部的控制都仰賴 Controller，所以一旦 Controller 本身出現問題，連帶影響的就是所有被控管的網路。

第二種方式的問題則跟第一種不同。"normal" 行為是被定義的標準，所以在不同廠商的 switch 下，也會產生各自的特性跟如何設定這些特性的差異性問題。另外，第二點，"normal" 行為在 OpenFlow 中運行的效果並不好，因為變成 OpenFlow 需要額外承擔調整自己的行為以符合個別的特性的成本。

## Setup（準備中）

```bash
$ sudo ovs-vsctl add-br br0 -- set Bridge br0 fail-mode=secure
```

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