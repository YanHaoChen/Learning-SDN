# Open vSwitch In-Band Control 實作方式

> 翻譯 [Open vSwitch In-Band Control](http://docs.openvswitch.org/en/latest/topics/design/?highlight=in%20band#in-band-control)

一個稱職的 OpenFlow Switch，應當負責建立及維護與 Controller 的連線（TCP）。連線的模式主要劃分為以下兩種：

* Out-of-band：Controller 與 Switch 連結時，連線管道**不在** Switch 所負責管理的網路下。
* In-band：Controller 與 Switch 連結時，連線管道在 Switch 所負責管理的網路中，並透過虛擬網路的方式進行。

Out-of-band 的好處：

* 簡單：略簡化 Switch 與 Controller 連接時，所需要的實作內容。
* 可靠：即使 Switch 所管理的網路中流量過大，也不會影響到 Controller 與 Switch 間的連線。
* 可信：不在控制用網路（Controller 與 Switch 的連線所在網路）中的設備，無法偽裝成其中的 Controller  或 Switch。
* 保密：不在控制網路中的設備，無法窺探其中 Controller 與 Switch 間溝通用的封包。

In-band 的好處：

* 不需要專用 Port：不需要在 Switch 上佔用一個實體的 Port 來連結控制網路。這相當重要，尤其對於一些只有少許 Port 能使用的 Switch 上（例如：無線路由器及低階嵌入式系統）。 
* 不需要控制用網路：不需要建立及維護控制用網路。在某些環境下這是相當重要的，因可減少 Switch 跟佈線上的需求。

 Open vSwitch 支援以上兩種模式。此節主要討論 In-Band 的設計原理。可透過[`ovs-vswitchd.conf.db(5)`](http://openvswitch.org/ovs-vswitchd.conf.db.5.pdf)的說明來設定 OVS 中的 In-Band 模式。