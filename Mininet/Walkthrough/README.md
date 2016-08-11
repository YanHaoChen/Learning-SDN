# 熟悉如何使用 Mininet

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
## 參考
[Mininet Walkthrough](http://mininet.org/walkthrough/)