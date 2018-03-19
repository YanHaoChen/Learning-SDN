# Open vSwitch In-band Control 實作方式

> 翻譯 [Open vSwitch In-band Control](http://docs.openvswitch.org/en/latest/topics/design/?highlight=in%20band#In-band-control)，並加入個人見解。有部分內容有用自己的方式改述，改述的地方無法保證完全符合官方所想表達的意思，再請參閱官方文件為主。

一個稱職的 OpenFlow Switch，應當負責建立及維護與 Controller 的連線（TCP）。連線的模式主要劃分為以下兩種：

* Out-of-band：Controller 與 Switch 連結時，連線管道**不在** Switch 所負責管理的網路下。
* In-band：Controller 與 Switch 連結時，連線管道在 Switch 所負責管理的網路中，並透過虛擬網路的方式進行。

Out-of-band 的好處：

* 簡單：略簡化 Switch 與 Controller 連接時，所需要的實作內容。
* 可靠：即使 Switch 所管理的網路中流量過大，也不會影響到 Controller 與 Switch 間的連線（Control Traffic）。
* 可信：不在控制用網路（Controller 與 Switch 的連線所在網路）中的設備，無法偽裝成其中的 Controller  或 Switch。
* 保密：不在控制網路中的設備，無法窺探其中 Controller 與 Switch 間的連線。

In-band 的好處：

* 不需要專用 Port：不需要在 Switch 上佔用一個實體的 Port 來連結控制網路。這相當重要，尤其對於一些只有少許 Port 能使用的 Switch 上（例如：無線路由器及低階嵌入式系統）。 
* 不需要控制用網路：不需要建立及維護控制用網路。在某些環境下這是相當重要的，因可減少 Switch 跟佈線上的需求。

Open vSwitch 支援以上兩種模式。此節主要討論 In-band 的設計原理。可透過[`ovs-vswitchd.conf.db(5)`](http://openvswitch.org/ovs-vswitchd.conf.db.5.pdf)的說明來設定 OVS 中的 In-band 模式。

### 原則

In-band 最基本的運作原則在於，OpenFlow Switch 需要不透過 Controller 自行認定及管理 Controller 與 Switch 間的連線。但在實作上會遇到一些**特殊需求、狀況**，導致無法單純奉行原則就可以運作。

設定這個簡要原則的原因很簡單。如果 Switch 沒辦法自行管理 Controller 與 Switch 間的連線，在執行上就會產生一些矛盾：當 Switch 想要連接 Controller 時，將無法成功。因為只有 Controller 可以下路由規則和規劃 Switch 至 Controller 的連接路徑。

以下為原則的流程：

```
開啟 In-band 模式 -> 自行建立與 Controller 之間的 In-band 連線 
-> 建立後，轉移 In-band 模式對連線規則(Flow)的控制權，全交由 Controller 完全控制 
```



以下幾點，將介紹**特殊需求、狀況**。

> 以下的論點，皆是以 Switch 的角度看待。

* 無論在 Switch 有沒有連接到 Controller 的情況下，In-band 都要可以正常運行。

  In-band 的原則上有個有趣的地方，就是只有當 Switch 無法與 Controller 連接時，才是需要以 In-band 控制規則（連接 Controller）的時候。也就是說，**一旦 Controller 與 Switch 成功建立連線後，控制權就該完全在 Controller 上**。

  也因此，原則是無法在實作上奉行的。因需考量到 Switch 與 Controller 連接時的各種情況。例如當 Switch 連接中的 Controller 忘記或著其他原因遺失 Switch 的 MAC 位址時，Controller 就需要傳送一個 ARP 請求的廣播封包，來取得 Switch 的 MAC 位址。但 Switch 在收到此請求後，卻無法透過與 Controller 之間的連線回傳，因 Switch 正與 Controller 連線中（並不符合使用 In-band 的情況），所以 Switch 的 ARP 回覆，只會變成一個普通的 **OFPT_PACKET_IN** 訊息傳送至 Controller，Controller 也只會當它是一個管轄內的封包來處理，而不是它與 Switch 間溝通的封包。這樣就會導致 Controller 無法得知 Switch 的 MAC 位址，且 Switch 也無法得到 Controller 的回覆，因為 Controller 並不知道 Switch 的 MAC 位址。這樣的**死結**，解決辦法只有一種，就是讓 Switch 可以自行判斷與 Controller 的連線狀況，再做進一步的處理。

* In-band 的規則（Flow），可能被其他由 Controller 下達的規則所覆蓋。  

  這樣的情況，也是再正常不過的事。因為在原則下，Controller 將會在與 Switch 的連線建立後，獲得整體網路規則的控制權。

  但此特例狀況仍會在實作上遇到問題。一般 Controller 在管理規則時，都會設定一個**預設規則**（最後一手），對應到此規則後，所採取的動作大多是**送至 Controller **或者**丟棄**。假設 In-band 用的連線規則被覆寫，Switch 要再與 Controller 建立 In-band 連線時，建立連線用的請求封包只能對應到預設規則，被送往 Controller 並被當作管理網路內的封包，或著直接被丟棄。

* Switch 需要認得所有的控制用封包。

  這是 In-band 中，最基本的原則。Switch 必須在沒有 Controller 幫助下，認得 Controller 與 Switch 間控制用封包。更嚴謹的說法，必須認得**所有 Controller 與 Switch 間控制用封包**。因在**假負**（False negatives）的情況下，也就是 Switch 沒有認出封包是控制用封包，就會導致控制用封包風暴。

  考量到 OpenFlow Switch 只認得傳向自己或者由他傳出的控制用封包。現在假設有 A、B 兩台 Switch 及一台  Controller，且皆接在同一個 Hub 下。當 A Switch 傳出一個控制用封包時，B Switch 也會收到。當 B Switch 收到時，因為是別人的控制用封包，因此 B Switch 並不認得，所以 B Switch 傳送 OFPT_PACKET_IN 給 Controller（也就是另一個控制用封包），此時換成 A Switch 會收到不認得的控制用封包，並傳送 OFPT_PACKET_IN 給 Controller。就這樣不斷循環下去，造成控制用封包風暴。

  另外**假正**（False positives）的情況下（不該被認為是控制用的封包，還是被認為是控制用封包），造成的網路負擔比較不嚴重。因為此狀況會導致 Controller 無法控制 Switch，但網路仍可正常運作。但此情況還會衍生出另一個問題，也是安全方面的問題（是否有偽造的控制用封包？）。

* Switch 需要使用 echo-requests 偵測連線是否中斷。

  TCP 本身就可以觀察是否還在連線，但問題就在可能會需要經過很長的時間，才能偵測的到。例如 Linux 核心在執行 TCP 時，就需要等待 13 至 30 分鐘不等，才能確定連線是否中斷（timeout）。這樣的等待時間太長了，所以 OpenFlow Switch 就需要實做自己的連線逾時，也就是 OpenFlow **OFPT_ECHO_REQUEST** 訊息。這是最佳的方式，因為 Switch 可以直接透過它來測試 OpenFlow 的連線狀況。

### 實作

此部分，將介紹 Open vSwitch 如何實作 In-band。上一個章節已經說明了，In-band 在實作上是非常困難的。因此，如想修改此部分的程式時，請確認完全瞭解上述的考量再進行更動。

Open vSwitch 在實作 In-band 時，是將 Controller 與 Switch 溝通用的連線規則（Flow）**隱藏**起來。所謂的隱藏，指的是將連線規則不歸納在 OpenFlow 中，並且將其優先權高於由 OpenFlow 下達的預設規則。這麼一來， Controller 將無法干預 In-band 的運行，也去除 Controller 與 Switch 間連線中斷的可能。雖然說連線規則不會在 OpenFlow 中，但還是可以透過`ovs-appctl`的`bridge/dump-flows`指令看到所有規則（包含連線規則）。

實作上，Open vSwitch 可以將隱藏地連線至任意的 **Remote**，遠端的意思就是一個 IP 位址上的 TCP Port。目前在實作上，這些遠端將由 In-band 自動配置，如同 OpenFlow Controller 及 OVSDB Managers。（OVSDB Manager  是最基本需要被配置的，因為 OVSDB Managers 會需要負責與 OpenFlow Controllers 溝通，所以如果無法連線至 OVSDB Manager，自然無法控制 OpenFlow）。

以下的 OpenFlow 規則（透過 OFPP_NORMAL action 運行）將建立在任何有連接 OpenFlow 設備的 OVS Bridge 上：

1. 從實體端口送出的 DHCP 請求封包。
2. 接收 ARP 回覆封包（目的地為實體端口的 MAC 位址） 。
3. 送出 ARP 請求封包（來源為實體端口的 MAC 位址） 。

在 In-band 模式下，可能因為 Remote 並不在同一個 Bridge 中，而需要多個節點（Bridge）才能到達。所以也會建立以下規則，來指定傳送到哪個節點（Next-hop），讓需要往來此 Remote 的封包能順利傳送：

4. 接收傳往特定 Next-hop（以 MAC 位址對應）的 ARP 回覆封包 。
5. 從此 Next-hop（以 MAC 位址對應）送出 ARP 請求封包 。

In-band 也會建立以下規則，來轉送每個 Remote 的 IP 位址，讓 Remote 彼此知道對方的 IP 位址：

6. 使用 ARP 回覆，傳送欲取得的 Remote IP 位址。
7. 在 ARP 請求中，附帶來源的 Remote IP 位址。

In-band 也會建立以下規則，來轉送連接建立後的 TCP 封包（以 IP、Port 對應）：

8. 傳送到指定 Remote 的 TCP 封包。
9. 接收到指定 Remote 的 TCP 封包。

這些規則的目的在於，盡可能減少 Switch 對於網路的需求，並且讓 Switch 跟能 Remote 有溝通的管道。但如稍早所提，這些規則的優先權都會高於 Controller 所下達的規則，所以如果這些規則影響的範圍越大，就越有可能會影響 Controller 實作網路的規劃。因此，In-band 模式會主動觀察流量及封包的運作狀況，進一步讓這些規則可以更精確（降低對網路的影響）。

In-band 模式觀察那些試圖將 Flow 加入 Datapath （Bridge），並可能對 Datapath 造成影響的任務。也因為這些 Datapath 只接受完全符合（Exact Match）的規則，所以利用這點， In-band 模式是可以精準的避免這些會造成影響的 Flow。如果新進的封包沒有辦法符合規則，將會傳送至使用者模式（userspace）進行處理，也因此可以避免讓這些封包存在 Data Plane 的快取中，進而符合 Fast Path 的正確性（能快速處理的封包，才是由 Data Plane 處理）。但其中有一個種狀況是需要擔心，那就是「DHCP 的回覆封包混雜在被管理網路及控制網路中」。這種狀況為什麼需要擔心呢？例如，你可以下一條規格禁止所有的 DHCP 封包不能流向 Controller，但如果此 DHCP 使廣播的方式傳送至每個連接端口（包含 Controller 所在的連接端口），就無法阻止這種情況發生。

如稍早所說，如封包無法在 Datapath 中對應到相關的規則，則會送往使用者模式進行處理。在使用者模式下，也會有一張對應的規則表（Classifier），所以 In-band 會在將封包送往這張表前，先確認此封包是不是需要特殊的處理。如果此封包是一個將回覆實體端口的 DHCP 請求的 DHCP 回覆，則此封包將會直接轉送到此實體端口，而直接跳過規則表（此部分的封包比對需要達到 ISO 第七層的處理程序，確定其中 **chaddr** 欄位是否是實體端口的 MAC 位址）。

這些實作細節，對於一個基於 ISO 第三層所建立，且主要在專注處理 ARP 封包的 In-Band 模式，是讓人意想不到的。乍看之下，會以為有很多規則是多餘的，但實際上，每個規則都有它存在的意義。例如，為了判斷 MAC 位址是否為 Remote ，所以我們建立了額外的 ARP 規則，且讓符合這些規則的封包可以透過實體端口送出（使用上述2、3 號規則）。另外，如果 Switch 是在另一台 Switch 與 Remote 的連線上，此 Switch 則需要幫忙轉送彼此的 ARP 封包（雖然我們沒辦法預先得知其他 Switch 的 MAC 位址，但我們可以透過已得知 Remote 及 Gateway 的 MAC 位址，進而運行 4、5 號規則來達到此目的）。最後，如果 Romote 是在一個實體端口所連接的主機中的虛擬機，而導致無法直接透過實體端口連接至 Romote，則連接至虛擬機的 Switch 需要能接收內容有 Remote IP 的 ARP 封包，因為此 Switch 並不能確定收到的 MAC 位址是實體端口的還是虛擬機中的 Remote 的。

除了等一下會提到的幾種例外狀況，In-band 模式能在大多數的網路中運行。以下為目前可支援的網路環境狀況：

* 本地區域連線：Switch 跟 Remote 在同一個子網內。這樣的環境下需要的是 1、2、3、8、9 號規則。
* 往需要通過 Gateway：Switch 跟 Remote 在不同的子網路內，需要透過 Gateway 連結。這樣的環境下需要的是 1、2、3、8、9 號規則。
* 介在 Switch 跟 Remote 間：此台 Switch 介在其他台 Switch 跟 Remote 的中間，我們希望它能轉送其他台 Switch 的封包。這樣的環境下需要的是 4、5、8、9 號規則。注意，除非由 Controller 明確地讓 DHCP 通行，不然 DHCP 封包是無法同行的。
* 介在 Switch 跟 Gateway 間：此台 Switch 介在其他台 Switch 跟 Gateway 的中間，我們希望它能轉送其他台 Switch 的封包。這樣的環境下需要的規則跟**介在 Switch 跟 Remote 間**一樣。
* Remote 是在實體電腦中的虛擬機：Remote 跑在一台虛擬機上，且正在執行 In-band。這樣的環境下需要的是 1、2、3、8、9 號規則。
* Remote 是在實體電腦中的虛擬機，且在不同網路中：Remote 跑在一台虛擬機上，且正在執行 In-band，但並沒有與實體端口連接。例如，將一個 IP 設定在此 Switch 的 eth0 端口上，Remote 的虛擬機透過 Switch 上的 eth1 連接 Switch，但此狀況下 eth1 就沒有對應的 IP。這麼一來，Switch 將會使用 eth0 去連接這台 Remote，但 eth1 此實體端口的規則是沒有作用的。此情況下，則需要在 eth0 上使用 1、2、3、8、9 號規則，eth1 則使用 6、7、8、9 號規則。

以下為目前無法支援的網路環境狀況：

* 以名稱指定 Remote：目前來說，Remote 都是由 IP 位址指定。最天真讓這件事可行的方法可能就是允許所有的 DNS 封包也能透過 In-band 的連線傳送。很遺憾的是，這樣做會導致 Controller 無法運行任何 DNS 的管理機制，因為當後來加入的 Switch 時，In-band 無法簡單的設定哪些實體端口需要讓 DNS 封包可以通行。正確能支援**以名稱指定 Remote**，是需要解析 DNS 請求，進而藉由解析出來 Remote 的名稱來決定哪些 DNS 封包可以放行。但基於潛在的安全及需要處理的量上，OVS 決定暫時擱置。
* Switch 需要對應不同的 Remote：Switch 需要透過 IP 位址知道所有 Switch 會使用到的 Remote，這樣一來，才能下達相關的規則（6、7、8、9 號規則），將封包轉送至 Remote。 
* Switch 需要對應不同的 Router：由於 Switch 允許其他 Switch 透過本身將封包送往 Gateway 與 Remote 連結，也就代表需要允許 Gateway 的封包流過它（4、5 號規則）。如果任兩台 Switch 到 Remote 所選擇的 Route 不同，Switch 將不知道該選擇哪個為 Gateway。