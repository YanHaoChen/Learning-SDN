# 熟悉如何使用 Mininet（part 1）

雖然之後用程式碼建立 Mininet 模擬環境的情況比較多，但多熟悉一點 Mininet 的操作方式也不是一件壞事。以下內容是跟著 [Mininet Walkthrough](http://mininet.org/walkthrough/) ，學習使用 Mininet 的過程。

## 開始操作

在試著操作 Mininet 之前，先翻閱使用手冊：

```bash
$ sudo mn -h
Usage: mn [options]
(type mn -h for details)

The mn utility creates Mininet network from the command line. It can create
parametrized topologies, invoke the Mininet CLI, and run tests.

Options:
  -h, --help            show this help message and exit
  --switch=SWITCH       default|ivs|lxbr|ovs|ovsbr|ovsk|user[,param=value...]
                        ovs=OVSSwitch default=OVSSwitch ovsk=OVSSwitch
                        lxbr=LinuxBridge user=UserSwitch ivs=IVSSwitch
                        ovsbr=OVSBridge
  --host=HOST           cfs|proc|rt[,param=value...]
                        rt=CPULimitedHost{'sched': 'rt'} proc=Host
                        cfs=CPULimitedHost{'sched': 'cfs'}
  --controller=CONTROLLER
                        default|none|nox|ovsc|ref|remote|ryu[,param=value...]
                        ovsc=OVSController none=NullController
                        remote=RemoteController default=DefaultController
                        nox=NOX ryu=Ryu ref=Controller
  --link=LINK           default|ovs|tc[,param=value...] default=Link
                        ovs=OVSLink tc=TCLink
  --topo=TOPO           linear|minimal|reversed|single|torus|tree[,param=value
                        ...] linear=LinearTopo torus=TorusTopo tree=TreeTopo
                        single=SingleSwitchTopo
                        reversed=SingleSwitchReversedTopo minimal=MinimalTopo
  -c, --clean           clean and exit
  --custom=CUSTOM       read custom classes or params from .py file(s)
  --test=TEST           cli|build|pingall|pingpair|iperf|all|iperfudp|none
  -x, --xterms          spawn xterms for each node
  -i IPBASE, --ipbase=IPBASE
                        base IP address for hosts
  --mac                 automatically set host MACs
  --arp                 set all-pairs ARP entries
  -v VERBOSITY, --verbosity=VERBOSITY
                        info|warning|critical|error|debug|output
  --innamespace         sw and ctrl in namespace?
  --listenport=LISTENPORT
                        base port for passive switch listening
  --nolistenport        don't use passive listening port
  --pre=PRE             CLI script to run before tests
  --post=POST           CLI script to run after tests
  --pin                 pin hosts to CPU cores (requires --host cfs or --host
                        rt)
  --nat                 [option=val...] adds a NAT to the topology that
                        connects Mininet hosts to the physical network.
                        Warning: This may route any traffic on the machine
                        that uses Mininet's IP subnet into the Mininet
                        network. If you need to change Mininet's IP subnet,
                        see the --ipbase option.
  --version             prints the version and exits
  --cluster=server1,server2...
                        run on multiple servers (experimental!)
  --placement=block|random
                        node placement for --cluster (experimental!)
```

以上，就是我們可以給 Mininet 的參數，雖然看起來很多，但用程式撰寫環境設定還是有必要性的。接下來先用 Mininet 中的基本拓樸，學習 Mininet 內的指令操作：

```bash
mininet@mininet:~$ sudo mn
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
mininet>
```

目前我們已經建立好一個基本的虛擬網路了。接下來在```mininet>```下的指令，也代表是對這個虛擬網路下達。在其中，我們可以透過```help```翻翻 Mininet 內的操作方式：

```bash
mininet> help

Documented commands (type help <topic>):
========================================
EOF    gterm  iperfudp  nodes        pingpair      py      switch
dpctl  help   link      noecho       pingpairfull  quit    time
dump   intfs  links     pingall      ports         sh      x
exit   iperf  net       pingallfull  px            source  xterm

You may also send a command to a node using:
  <node> command {args}
For example:
  mininet> h1 ifconfig

The interpreter automatically substitutes IP addresses
for node names when a node is the first arg, so commands
like
  mininet> h2 ping h3
should work.

Some character-oriented interactive commands require
noecho:
  mininet> noecho h2 vi foo.py
However, starting up an xterm/gterm is generally better:
  mininet> xterm h2

mininet>
```
指令那麼多，先來介紹幾個顯示 Mininet 內部狀況的指令。首先是```nodes```：

```bash
mininet> nodes
available nodes are:
c0 h1 h2 s1
```
透過```nodes```可以快速觀察網路中有哪些節點。如果要看各節點的連結狀況，我們可以透過```net```：

```bash
mininet> net
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0
c0
```

其連接的狀況，是用網路介面來代表。例如```h1```就是以本身的```eth0```與```s1```的網路介面```eth1```進行連結。

接下來就是介紹能觀察所有節點詳細狀況的```dump```：

```bash
mininet> dump
<Host h1: h1-eth0:10.0.0.1 pid=2698>
<Host h2: h2-eth0:10.0.0.2 pid=2700>
<OVSSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=2705>
<Controller c0: 127.0.0.1:6653 pid=2691>
```

透過```dump```可以觀察各節點的 IP 位置、pid 的資訊。

### 第二種下達指令（個別節點執行）

Mininet 除了整體指令，還可以讓個別主機執行指令。我們可以遵循從```help```瞭解到的使用方式：

```bash
You may also send a command to a node using:
  <node> command {args}
For example:
  mininet> h1 ifconfig
```

#### ifconfig

例如想觀察```h1```的網路狀況：

```bash
mininet> h1 ifconfig -a
h1-eth0   Link encap:Ethernet  HWaddr 6e:33:30:37:d2:20
          inet addr:10.0.0.1  Bcast:10.255.255.255  Mask:255.0.0.0
          inet6 addr: fe80::6c33:30ff:fe37:d220/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:889 errors:0 dropped:0 overruns:0 frame:0
          TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:168765 (168.7 KB)  TX bytes:648 (648.0 B)

lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)
```

另外，雖然我們可以看到不同的節點內部的狀況，且感覺節點間是分開的，但在 Mininet 中，各個節點用的行程的顯示上還是會包含 Mininet 本身的行程。我們可以由執行```ps```得知：

```bash
mininet> h1 ps -a
  PID TTY          TIME CMD
 2685 pts/2    00:00:00 sudo
 2686 pts/2    00:00:00 mn
 2742 pts/24   00:00:00 controller
 3012 pts/25   00:00:00 ps
mininet> s1 ps -a
  PID TTY          TIME CMD
 2685 pts/2    00:00:00 sudo
 2686 pts/2    00:00:00 mn
 2742 pts/24   00:00:00 controller
 3014 pts/27   00:00:00 ps
```

#### ping

接下來則是```ping```。```ping```個人覺得是在網路學習上很基本且很重要的指令。我們可以透過以下方式，讓 Mininet 中的主機```ping```其他也在其中的主機：

```bash
mininet> h1 ping -c1 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=1.77 ms

--- 10.0.0.2 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 1.774/1.774/1.774/0.000 ms
```

透過```ping```我們也可以瞭解 OpenFlow 在執行上的機制。在傳送```ping```封包時，一開始會查看 ARP table 中有沒有目標主機，在一個區域網路剛建立的時候 ARP table 會是空的，因此在 ARP table 中找不到```10.0.0.2```這台主機，所以會觸發```packet_in```傳送給 controller，controller 收到後，會傳送```packet_out```要求發送廣播封包，進一步找尋目標主機有沒有在管轄範圍內，進而建立起 ARP table。所以再```ping```一次同一台主機，就會發現所需時間由```1.77 ms```降至```5.80 ms```：

```bash
mininet> h1 ping -c1 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=5.80 ms

--- 10.0.0.2 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 5.800/5.800/5.800/0.000 ms
```
如在建立實驗環境時，不希望這一開始無法避免的建表（ARP table）過程影響實驗結果，可以先使用```pingall```，把 ARP table 建立好，再進行實驗：

```bash
mininet> pingall
*** Ping: testing ping reachability
h1 -> h2
h2 -> h1
*** Results: 0% dropped (2/2 received)
```

### Mininet 還提供了簡易的 Web Service 測試方式

有時候實驗的狀況可能會需要 Web Service，Mininet 也可以在個別```host```中，快速的建立 Web Service，方法只需要像這樣：

```bash
mininet> h1 python -m SimpleHTTPServer 80 &
```

在```h1```上，就在背景執行一個 Web Service 了。接著我們可以讓```h2```跟```h1```的 Web Service 連線看看：

```bash
mininet> h2 wget -O - h1
--2016-08-12 22:24:38--  http://10.0.0.1/
Connecting to 10.0.0.1:80... connected.
HTTP request sent, awaiting response... 200 OK
...
```
如果要關掉```h1```上的 Web Service 也只需要：

```bash
mininet> h1 kill %python
Serving HTTP on 0.0.0.0 port 80 ...
10.0.0.2 - - [12/Aug/2016 22:24:38] "GET / HTTP/1.1" 200 -
```
### 把 Mininet 關掉

你只需要這樣：

```bash
mininet> exit
*** Stopping 1 controllers
c0
*** Stopping 2 links
..
*** Stopping 1 switches
s1
*** Stopping 2 hosts
h1 h2
*** Done
completed in 902.280 seconds
mininet@mininet:~$
```
如果 Mininet crash 了，你可以用```-c```把環境清理乾淨：

```bash
$ sudo mn -c
```

## 參考
[Mininet Walkthrough](http://mininet.org/walkthrough/)
