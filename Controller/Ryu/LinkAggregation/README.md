# Link Aggregation
透過網路聚合的方式，可以擴充單台主機可以使用的網路介面，其他主機雖然是向同一台主機（設定成 Link Aggregation 模式的主機）進行溝通，但其實並不一定是由同一個 port 進行。也就是說，Link Aggregation 可以將與主機溝通的其他主機進行分配，並分配到歸此主機管理的任意 port 上。這麼一來，可以有效的提高網路效率，再加上 LACP 通訊協定，當其中一個 port 突然出現問題，無法繼續進行數據傳輸，也會動態的將出問題的 port 上的主機移轉到可運作的 port 上，繼續提供服務，達成高容錯的能力。

> 提高網路效率：如果每個 port 都有 100 Mbps 的網路傳輸速度，那麼在使用兩個 port 的情況下，則總共會有 200 Mbps 的網路傳輸速度。

## 運行

在此，使用 Mininet 進行環境模擬（[MininetEnv.py](https://github.com/imac-cloud/SDN-tutorial/blob/master/Ryu/LinkAggregation/MininetEnv.py)），使用以 Ryu 建立的應用程式 [SimpleSwitchLACP13](https://github.com/imac-cloud/SDN-tutorial/blob/master/Ryu/LinkAggregation/SimpleSwitchLACP13.py) 進行控制，實現 Link Aggregation 的運作。

### MininetEnv.py
建立模擬環境。其中包含 4 台 host、1 台 switch 及 1 台遠端 controller。host1（```h1```）是實現 Link Aggregation 的主機，所以在程式內的編寫有別於其他主機。例如（標題為程式碼行號）：

* ```13```：並未直接設定 MAC Address，待主機（```h1```）設定 Link Aggregation 時，會再進行設定。
* ```18```、```19```：將```h1```與 switch 建立兩個連接 port。

> 在 Ryubook 繁體中文版內的範例程式碼中，因目前 Mininet 的版本與其中的編寫方式有些出入（循環引用及語法錯誤的問題），並無法直接執行。所以此環境建立方式是參考英文版的 Ryubook，是可以成功執行的版本。（2016/07/02）

### SimpleSwitchLACP13.py
可以說是由 SimpleSwitch13 進行修改。SimpleSwitchLACP13 與 SimpleSwitch 最大的差別，就在於加入 LACP 網路協定：

* self.\_lacp.add：初始化 Link Aggregation 的設定。
* lacplib.EventPacketIn：處理 LACP 網路協定中 PacketIn 事件。
* lacplib.EventSlaveStateChanged：處理 LACP 網路協定中 Slave 狀況改變時的事件（如斷線）。
* del_flow：刪除有關於已斷線 port 的 Flow Entry。

### 運行步驟
```shell
1. 啟動負責 Ryu 及 Mininet 的主機
2. 運行 MininetEnv.py
3. 在 h1 中，設定 Link Aggregation 的配置
4. 設定 switch 的 OpenFlow 版本（設定為 1.3 版）
5. 運行 SimpleSwitchLACP13.py
```

> 步驟二請在 Desktop 版本上執行。

### 設定 ```h1``` 的 Link Aggregation 的配置

> 接下來的指令，請在 host1 的 terminal 中執行。

在 Linux 中 Link Aggregation 是由 bonding drive 所處理。所以首先，先對 drive 做一些設定：

##### 開起檔案：```/etc/modprobe.d/bonding.conf```
寫入：

```shell
alias bond0 bonding
options bonding mode=4
```

寫入完成後，執行：

```shell
$ modprobe bonding
```
> mode 設定為 4。代表設定為 Dynamic Link Aggregation 模式（也是初始預設模式）。

##### 建立```bond0```邏輯介面，並設定其 MAC Address

```shell
$ ip link add bond0 type bond
$ ip link set bond0 address 02:01:02:03:04:08
```

##### 分別將```h1-eth0```、```h1-eth1```設定為 down 後，將其加入```bond0```中

```shell
$ ip link set h1-eth0 down
$ ip link set h1-eth0 address 00:00:00:00:00:11
$ ip link set h1-eth0 master bond0
$ ip link set h1-eth1 down
$ ip link set h1-eth1 address 00:00:00:00:00:12
$ ip link set h1-eth1 master bond0
```

##### 設定```bond0```的 IP 位址，並將原先```h1-eth0```的 IP 設定移除

```shell
$ ip addr add 10.0.0.1/8 dev bond0
$ ip addr del 10.0.0.1/8 dev h1-eth0
```

##### 最後將```bond0```設定為 UP

```shell
$ ip link set bond0 up
```

##### 透過一下兩個指令，確認設定是否正確

* ```ifconfig```：檢查```bond0```、```h1-eth0```及```h1-eth1```的 MAC Address 是否相同。
* ```cat /proc/net/bonding/bond0```：檢查在 Link Aggregation 模式下的```h1-eth0```及```h1-eth1```的 MAC Address 設定是否正確。

### 設定 switch 的 OpenFlow 版本
> 接下來的指令，請在 switch 的 terminal 中執行。

```shell
$ ovs-vsctl set Bridge s1 protocols=OpenFlow13
```

### 運行 SimpleSwitchLACP13.py
> 接下來的指令，請在負責 Ryu 的主機上執行。

```shell
$ ryu-manager ./SimpleSwitchLACP13.py
```

執行後，將會產生大量的 log。如要瞭解運行的狀況，建議直接利用以下指令，觀察 switch 中 Flow Entry 的狀況：
> 接下來的指令，請在 switch 的 terminal 中執行。

```shell
ovs-ofctl -O openflow13 dump flows s1
```

從中，也可以看出在 Link Aggregation 下，其他主機與```h1``` 的連接狀況及使用到的 port 的分配狀況。

### 最簡單增加其他主機與```h1```的 Flow Entry 方式
在這時候，請愛用```ping```。
> 請在各別的主機的 terminal 中執行。其 IP Address 10.0.0.1  在此為```h1```的 IP 位置。

```shell
$ ping 10.0.0.1
```

執行後，在 switch 中，將會新增對應的 Flow Entry。透過這些 Flow Entry，我們可以進一步的觀察整體的運做方式。

## 參考
[Ryubook](https://osrg.github.io/ryu/resources.html)
