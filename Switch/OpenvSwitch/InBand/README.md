# Open vSwitch In-Band Control 實作方式

> 翻譯 [Open vSwitch In-Band Control](http://docs.openvswitch.org/en/latest/topics/design/?highlight=in%20band#in-band-control)，並加入個人見解

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

Open vSwitch 支援以上兩種模式。此節主要討論 In-Band 的設計原理。可透過[`ovs-vswitchd.conf.db(5)`](http://openvswitch.org/ovs-vswitchd.conf.db.5.pdf)的說明來設定 OVS 中的 In-Band 模式。

### 原則

In-Band 最基本的運作原則在於，OpenFlow Switch 需要不透過 Controller 自行認定及管理 Controller 與 Switch 間的連線。但在實作上會遇到一些**特殊需求、狀況**，導致無法單純奉行原則就可以運作。

設定這個簡要原則的原因很簡單。如果 Switch 沒辦法自行管理 Controller 與 Switch 間的連線，在執行上就會產生一些矛盾：當 Switch 想要連接 Controller 時，將無法成功。因為只有 Controller 可以下路由規則和規劃 Switch 至 Controller 的連接路徑。

以下為原則的流程：

```
開啟 In-Band 模式 -> 自行建立與 Controller 之間的 In-Band 連線 
-> 建立後，轉移 In-Band 模式對連線規則(Flow)的控制權，全交由 Controller 完全控制 
```



以下幾點，將介紹**特殊需求、狀況**。

> 以下的論點，皆是以 Switch 的角度看待。

* 無論在 Switch 有沒有連接到 Controller 的情況下，In-Band 都要可以正常運行。

  In-Band 的原則上有個有趣的地方，就是只有當 Switch 無法與 Controller 連接時，才是需要以 In-Band 控制規則（連接 Controller）的時候。也就是說，**一旦 Controller 與 Switch 成功建立連線後，控制權就該完全在 Controller 上**。

  也因此，原則是無法在實作上奉行的。因需考量到 Switch 與 Controller 連接時的各種情況。例如當 Switch 連接中的 Controller 忘記或著其他原因遺失 Switch 的 MAC 位址時，Controller 就需要傳送一個 ARP 請求的廣播封包，來取得 Switch 的 MAC 位址。但 Switch 在收到此請求後，卻無法透過與 Controller 之間的連線回傳，因 Switch 正與 Controller 連線中（並不符合使用 In-Band 的情況），所以 Switch 的 ARP 回覆，只會變成一個普通的 **OFPT_PACKET_IN** 訊息傳送至 Controller，Controller 也只會當它是一個管轄內的封包來處理，而不是它與 Switch 間溝通的封包。這樣就會導致 Controller 無法得知 Switch 的 MAC 位址，且 Switch 也無法得到 Controller 的回覆，因為 Controller 並不知道 Switch 的 MAC 位址。這樣的**死結**，解決辦法只有一種，就是讓 Switch 可以自行判斷與 Controller 的連線狀況，再做進一步的處理。

* In-Band 的規則（Flow），可能被其他由 Controller 下達的規則所覆蓋。  

  這樣的情況，也是再正常不過的事。因為在原則下，Controller 將會在與 Switch 的連線建立後，獲得整體網路規則的控制權。

  但此特例狀況仍會在實作上遇到問題。一般 Controller 在管理規則時，都會設定一個**預設規則**（最後一手），對應到此規則後，所採取的動作大多是**送至 Controller **或者**丟棄**。假設 In-Band 用的連線規則被覆寫，Switch 要再與 Controller 建立 In-Band 連線時，建立連線用的請求封包只能對應到預設規則，被送往 Controller 並被當作管理網路內的封包，或著直接被丟棄。

* Switch 需要認得所有的控制用封包。

  這是 In-Band 中，最基本的原則。Switch 必須在沒有 Controller 幫助下，認得 Controller 與 Switch 間控制用封包。更嚴謹的說法，必須認得**所有 Controller 與 Switch 間控制用封包**。因在**假負**（False negatives）的情況下，也就是 Switch 沒有認出封包是控制用封包，就會導致控制用封包風暴。

  考量到 OpenFlow Switch 只認得傳向自己或者由他傳出的控制用封包。現在假設有 A、B 兩台 Switch 及一台  Controller，且皆接在同一個 Hub 下。當 A Switch 傳出一個控制用封包時，B Switch 也會收到。當 B Switch 收到時，因為是別人的控制用封包，因此 B Switch 並不認得，所以 B Switch 傳送 OFPT_PACKET_IN 給 Controller（也就是另一個控制用封包），此時換成 A Switch 會收到不認得的控制用封包，並傳送 OFPT_PACKET_IN 給 Controller。就這樣不斷循環下去，造成控制用封包風暴。

  另外**假正**（False positives）的情況下（不該被認為是控制用的封包，還是被認為是控制用封包），造成的網路負擔比較不嚴重。因為此狀況會導致 Controller 無法控制 Switch，但網路仍可正常運作。但此情況還會衍生出另一個問題，也是安全方面的問題（是否有偽造的控制用封包？）。

* Switch 需要使用 echo-requests 偵測連線是否中斷。

  TCP 本身就可以觀察是否還在連線，但問題就在可能會需要經過很長的時間，才能偵測的到。例如 Linux 核心在執行 TCP 時，就需要等待 13 至 30 分鐘不等，才能確定連線是否中斷（timeout）。這樣的等待時間太長了，所以 OpenFlow Switch 就需要實做自己的連線逾時，也就是 OpenFlow **OFPT_ECHO_REQUEST** 訊息。這是最佳的方式，因為 Switch 可以直接透過他來測試 OpenFlow 的連線狀況。