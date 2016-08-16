# 熟悉如何使用 Mininet（part 2）

除了一些基本的啟動參數，接下來介紹一些進階一點的參數。

### 進行回歸測試（Regression Test）

在 Mininet 中，透過```--test```就可以對欲建立的拓樸進行回歸測試。除了可以測試拓樸是否可以建立，我們還可以加一些指令，測試更多項目：

```bash
$ sudo mn --test pingpair
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2
*** Adding switches:
s1
*** Adding links:
(h1, s1) (h2, s1)
*** Configuring hosts
h1 h2
*** Starting controller
c0
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1
h1 -> h2
h2 -> h1
*** Results: 0% dropped (2/2 received)
*** Stopping 1 controllers
c0
*** Stopping 2 links
..
*** Stopping 1 switches
s1
*** Stopping 2 hosts
h1 h2
*** Done
completed in 5.331 seconds
```
這在這裡，除了測試建立拓樸，還利用```pingpair```測試主機之間的連線狀況。

> 如果對指令有不清楚的地方，也可以透過 Mininet 內的```help```來瞭解指令的意義：
> 
> ```bash
> mininet> help pingpair
> Ping between first two hosts, useful for testing.
>```

除了```pingpair```，還可以試試看```iperf```：

```bash
$ sudo mn --test iperf
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2
*** Adding switches:
s1
*** Adding links:
(h1, s1) (h2, s1)
*** Configuring hosts
h1 h2
*** Starting controller
c0
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1
*** Iperf: testing TCP bandwidth between h1 and h2
.*** Results: ['36.2 Gbits/sec', '36.3 Gbits/sec']
*** Stopping 1 controllers
c0
*** Stopping 2 links
..
*** Stopping 1 switches
s1
*** Stopping 2 hosts
h1 h2
*** Done
completed in 10.893 seconds
```

如果只是單純想測試拓樸是否能運作（不包含連線等功能），可以直接給它```none```。這樣的測試方式，也可當成是此拓樸的基準測試：

```bash
$ sudo mn --test none
```

### 用參數調整拓樸

參數```--topo```可以讓我們鍵入特定的拓樸模式及規格，另外也可以結合```--test```對建立起的拓樸進行測試：

```bash
$ sudo mn --test pingall --topo single,3
[sudo] password for mininet:
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3
*** Adding switches:
s1
*** Adding links:
(h1, s1) (h2, s1) (h3, s1)
*** Configuring hosts
h1 h2 h3
*** Starting controller
c0
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1
*** Ping: testing ping reachability
h1 -> h2 h3
h2 -> h1 h3
h3 -> h1 h2
*** Results: 0% dropped (6/6 received)
*** Stopping 1 controllers
c0
*** Stopping 3 links
...
*** Stopping 1 switches
s1
*** Stopping 3 hosts
h1 h2 h3
*** Done
completed in 5.415 seconds
```

### 對 Mininet 的連線條件進行設定

在 Mininet 2.0 後允許使用者可以對連線條件進行設定，所以使用者可以進一步的設定頻寬、延遲時間等等：

```bash
$ sudo mn --link tc,bw=10,delay=10ms
*** Creating network
...
*** Adding links:
(10.00Mbit 10ms delay) (10.00Mbit 10ms delay) (h1, s1) (10.00Mbit 10ms delay) (10.00Mbit 10ms delay) (h2, s1)
...
*** Starting 1 switches
s1 ...(10.00Mbit 10ms delay) (10.00Mbit 10ms delay)
...
mininet>
```

> [更多關於 link 的設定方式](https://github.com/mininet/mininet/wiki/Introduction-to-Mininet#setting-performance-parameters)

### 調整 Mininet 輸出的內容（Verbosity）

Mininet 內部預設的狀況是```info```，所以我們可以看見以下資訊：

```bash
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2
*** Adding switches:
s1
*** Adding links:
(h1, s1) (h2, s1)
*** Configuring hosts
h1 h2
*** Starting controller
c0
*** Starting 1 switches
s1 ...
*** Starting CLI:
```
但其實輸出的內容還有其他選項可以設定，現在介紹其中的兩個，分別為```debug```及```output```。```debug```顯示更詳細的內容，```output```則是直接省略所有過程中的資訊：

```bash
// debug 模式
$ sudo mn -v debug
*** errRun: ['which', 'controller']
/usr/local/bin/controller
  0*** errRun: ['grep', '-c', 'processor', '/proc/cpuinfo']
1
  0*** Setting resource limits
*** Creating network
*** Adding controller
*** errRun: ['which', 'mnexec']
/usr/bin/mnexec
  0*** errRun: ['which', 'ifconfig']
...

// output 模式
$ sudo mn -v output
mininet>
```

> 模式```warning```在回歸測試模式下，較為適用。

### 執行客製化拓樸

我們可以利用 python 直接撰寫我們想要的拓樸環境，並透過 Mininet 執行它。在當初 clone 下來的 Mininet 檔案中，就有放一個自行撰寫的範例程式```mininet/custom/topo-2sw-2host.py```。接下來我們試著用 Mininet 執行它看看：

```bash
$ sudo mn --custom mininet/custom/topo-2sw-2host.py --topo mytopo --test pingall
[sudo] password for mininet:
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2
*** Adding switches:
s3 s4
...
...
```

> 如果想自行撰寫，也可以把```topo-2sw-2host.py```當作參考。

### 參數 mac

一般我們在建立拓樸時，如沒有加入參數```--mac```，Mininet 將會以隨機產生的方式將產生出來的 MAC address 分配給各個節點，但如果加入了，則會變成有順序的方式產生 MAC address：

```bash
//沒有參數 mac
$ sudo mn
...
mininet> h1 ifconfig
h1-eth0   Link encap:Ethernet  HWaddr 92:3d:a5:9a:c3:c0
          inet addr:10.0.0.1  Bcast:10.255.255.255  Mask:255.0.0.0
          inet6 addr: fe80::903d:a5ff:fe9a:c3c0/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:40 errors:0 dropped:0 overruns:0 frame:0
          TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:5647 (5.6 KB)  TX bytes:648 (648.0 B)
          
//加入參數 mac
$ sudo mn --mac
...
mininet> h1 ifconfig
h1-eth0   Link encap:Ethernet  HWaddr 00:00:00:00:00:01
          inet addr:10.0.0.1  Bcast:10.255.255.255  Mask:255.0.0.0
          inet6 addr: fe80::200:ff:fe00:1/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:36 errors:0 dropped:0 overruns:0 frame:0
          TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:5651 (5.6 KB)  TX bytes:668 (668.0 B)
```

### 開啟各別主機的 terminal（xterm）

為了要方便對不同主機下指令，Mininet 也提供了可以讓使用者開啟各節點的 terminal 的功能，只需要在建立時加入參數```-x```：

```bash
$ sudo mn -x
```

以上指令是一次開啟所有節點的 terminal，但如果只想開啟特定主機，你可以這樣做：

```bash
$ sudo mn
...
mininet> xterm h1
```

> 請在桌面版的系統上進行這項指令，否則其他主機的 terminal 是無法開啟的。

### 選擇不同的 Switch

Mininet 在建立時，預設使用的 Switch 就是 OVSSwitch。除了 OVSSwitch 還有其他的 Switch 可以供使用者選擇：

```bash
$ man mn
...
--switch=SWITCH
              default|ivs|lxbr|ovs|ovsbr|ovsk|user[,param=value...]     ovs=OVSSwitch     default=OVSSwitch
              ovsk=OVSSwitch lxbr=LinuxBridge user=UserSwitch ivs=IVSSwitch ovsbr=OVSBridge
...
```

Switch 的選擇，對整體的測試是佔有一定程度的影響的。以下就舉```UserSwitch```跟預設的```OVSSwitch```進行比較：

```bash
// UserSwitch
$ sudo mn --switch user --test iperf
...
*** Iperf: testing TCP bandwidth between h1 and h2
.*** Results: ['945 Kbits/sec', '1.01 Mbits/sec']
...

// OVSSwitch
$ sudo mn --switch ovsk --test iperf
...
*** Iperf: testing TCP bandwidth between h1 and h2
.*** Results: ['38.6 Gbits/sec', '38.6 Gbits/sec']
...
```

測試出來的數據，有很明顯的差異。```UserSwitch```因為還需要額外處理核心與使用者介面的溝通，大幅增加效率上的成本。```UserSwitch```也是會有需要它的時候，但應該不會使用在需要高即時性的狀況下。

### 將 Switch 與 Controller 規劃在同一個 Netwrok Namespace（user switch only）

如果一時間會意不過來是什麼意思，直接執行一次，就可以了解。先來試試沒有這項設定的狀況：

```bash
$ sudo mn --switch user
...
mininet> dump
<Host h1: h1-eth0:10.0.0.1 pid=2760>
<Host h2: h2-eth0:10.0.0.2 pid=2762>
<UserSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=2764>
<Controller c0: 127.0.0.1:6653 pid=2753>
```

加了```--innanmespace```這項設定後：

```bash
$ sudo mn --innamespace --switch user
...
mininet> dump
<Host h1: h1-eth0:10.0.0.1 pid=2871>
<Host h2: h2-eth0:10.0.0.2 pid=2873>
<UserSwitch s1: s1-eth0:192.168.123.2,s1-eth1:None,s1-eth2:None pid=2875>
<Controller c0: 192.168.123.1:6653 pid=2864>
```

現在我們可以觀察出差別了。加入選項```--innamespace```後，Switch 跟 Controller 被分開了，並分配在同一個網段中。

> 在此，設定參數的介紹，就到一個段落！

## 參考

[Mininet Walkthrough](http://mininet.org/walkthrough/)