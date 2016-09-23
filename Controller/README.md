# Controller

在 SDN 的架構中，Controller 就像是大腦，負責管理整體的封包配送規則，是 Control Plane 的部分。透過 Controller 將管理的方式程式化，也因此增加了整體的靈活度。Controller 透過協定向 Switch 下達管理規則，進而管理整體的封包流動方式，也可以透過協定，取得 Switch 的運行狀況。

* [Ryu](https://github.com/imac-cloud/SDN-tutorial/tree/master/Controller/Ryu)