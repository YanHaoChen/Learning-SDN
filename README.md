# SDN-tutorial

SDN（Software-defined networking，軟體定義網路）是一個相當大的架構，字面上雖然簡單，但這一切最有問題的地方是在於「如何實作軟體定義網路」。要學會實作 SDN ，最重要的是瞭解 SDN 整體的架構，也因為 SDN 並非單一單元，如果缺失其中一個單元的瞭解，在最後的設計上，將會綁手綁腳、無從下手。在此，我將 SDN 分為三個單元，分別為：

* Switch（連接設備，屬於 Data Plane）

* 協定（Switch 的運作規則、Switch 與 Controller 之間的溝通）

* Controller（定義 Switch 的運作規則及整體網路邏輯，屬於 Control Plane）

在學習的項目上又分為四個部分（依順序排列）：

1. [協定](https://github.com/YanHaoChen/Learning-SDN/tree/master/Protocols/)

2. [Switch](https://github.com/YanHaoChen/Learning-SDN/tree/master/Switch/)

3. [虛擬網路環境（Mininet）](https://github.com/YanHaoChen/Learning-SDN/tree/master/Mininet)

4. [Controller](https://github.com/YanHaoChen/Learning-SDN/tree/master/Controller/)


## 實際設備操作

* [Pica8 P-3297 實際操作-連結與模式設定](https://github.com/YanHaoChen/Learning-SDN/tree/master/Pica8-P-3297/ConnectAndSetEnvironment)

## 使用到的套件
* Mininet（虛擬網路環境）
* Open vSwitch（虛擬 Switch）
* Ryu（SDN Controller）
* Vagrant（建立虛擬系統環境）
* GtkTerm（連接週邊硬體）

## 硬體設備
* Pica8 P-3297

## 參考
* [OpenFlow（Flowgrammable）](http://flowgrammable.org/sdn/openflow/classifiers/#tab_ofp_1_0)
* [Mininet](http://mininet.org/)
* [Open vSwitch](https://github.com/openvswitch/ovs)
* [ryu readthedocs](http://ryu.readthedocs.io/en/latest/getting_started.html)
* [Ryubook](https://osrg.github.io/ryu/resources.html)
