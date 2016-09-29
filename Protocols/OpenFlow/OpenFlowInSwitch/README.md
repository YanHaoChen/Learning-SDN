# 使用 OpenFlow 的 Switch

在能運行 OpenFlow 的 Switch 中，將有兩個主要單元：

* Switch Agent
* Data Plane

### Switch Agent

Switch Agent 將會負責 Switch 與 Controller 的溝通，並解析 OpenFlow 協定，進而將解析出的規則下達至 Data Plane 中執行。

### Data Plane

在 Data Plane 部分，則由以下項目完成整體的運行：

* Ports：封包進入或離開 Switch 的端口。

* Flow Tables：存放規則（Flow）。可以用一個 Table 存放所有的規則，也可利用多個 Table 進行分層管理（過濾、轉送、學習），端看需求而定。

* Flows：包含 Match 條件（符合此規則的封包條件）及 Action（封包符合此規則後的運行動作），並存放在 Flow Table 中。

* Classifiers：封包進入 Flow Table 後，藉由 Classifiers 比對符合的規則（Flow），並進行相對應的作動，如無符合項目，則轉送至 Controller，規劃此封包的處理方式。

#### 各項目在 Data Plane 中的運作流程

```shell
Ports(in) -> Flow Tables -> Classifiers -> (Match) -> Flows -> (Action) -> Ports(out)
```

#### 封包在 Data Plane 中的 Lifecycle

封包在到達 Switch 後，將會建立出一個代表此封包的 __Key__，並轉送至 Table 中，搜尋對應的 Flow ，並執行其中的 Action。也因為特定 Action 可以將封包轉往其它的 Table 進行下一步的規則對應，所以封包有可能在 Action 後離開 Switch，也有可能是轉往下一個 Table 進行下一步的轉送規劃。

> Key 中將包含此封包的部分資訊，例如協定、進入的 port、到達時間等。

#### Lifecycle

```shell
封包到達 -> 取出特定封包資訊產生 Key -> 進入 Flow Table -> 搜尋對應規則 -> 執行 Action 離開 Switch，或轉往其他 Flow Table
```


## 參考

[SDN / OpenFlow | Flowgrammable](http://flowgrammable.org/sdn/openflow/)