# Controller

在 SDN 的架構中，Controller 就像是大腦，負責管理整體的封包配送規則，是 Control Plane 的部分。透過 Controller 將管理的方式程式化，也因此增加了整體的靈活度。Controller 透過協定向 Switch 下達管理規則，進而管理整體的封包流動方式，也可以透過協定，取得 Switch 的運行狀況。

選擇要使用的 Controller。想必是剛踏入 SDN 的初學者，很快就會遇到的課題。目前作者正在嘗試以下兩種 Controller。初步的結論如下：

### 選擇 Ryu 的理由（入門容易。建議初學者、研究使用）

Ryu 在安裝、編寫控制邏輯（Forwarding...）都相當好上手，執行上也只要一行指令，並不拖泥帶水。相當適合初學 SDN，想嘗試實作、瞭解 OpenFlow 協定在 Controller 上運作模式的人使用。但在接觸 ONOS 後，就會發現 Ryu 就像一個空殼，可以很方便的打造自己想要的特定功能沒錯，但其他實際會需要的功能 Ryu 並沒有提供任何現成模組，在執行上也並未註冊服務在作業系統中，並不太像一個可以馬上商用的 Controller。但也因為空殼，所以對於初學者來說，可以降低複雜度，只需要專注在想瞭解的部分嘗試、理解。對於研究生來說，也降低了入門的門檻，能快速嘗試自己設計的演算法。

* [Ryu](https://github.com/OSE-Lab/Learning-SDN/tree/master/Controller/Ryu)

### 選擇 ONOS 的理由（框架完整，適合商業用）

ONOS 的完整度，相較於 Ryu 高出很多。已經有很多現成的模組可以使用，但也因為完整度高，入門的技術門檻也高出許多，因為不只有單單 SDN 的技術要瞭解，還有一些系統方面的知識也需要具備。雖然不是一個好入門的 Controller，但它的學習價值極高，因為其商業用的可能性。

* [ONOS](https://github.com/OSE-Lab/Learning-SDN/tree/master/Controller/ONOS)
