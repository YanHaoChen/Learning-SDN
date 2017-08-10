# 熟悉如何使用 Mininet（part 3）

Mininet 可以讓使用者在環境中，直接執行 python 的程式碼，因此使用者可以更靈活運用。以下將介紹在 Mininet 中，python 程式碼的執行方式，另外再提一個方便的應用（Link Up/Down）。

### Mininet 識別 python

Mininet 要識別 python，其實只需要在欲執行的 python 程式碼前加入識別字串```py```。現在來一個簡單的例子，```print```出```Hello world!```：

```bash
$ sudo mn
...
mininet> py 'Hello ' + 'world!'
Hello world!
```
還可以利用它來取得一些有用的數據。像是 Mininet 中的節點（object）：

```bash
mininet> py locals()
{'h2': <Host h2: h2-eth0:10.0.0.2 pid=2335> , 'net': <mininet.net.Mininet object at 0x7f2d57431350>, 'h1': <Host h1: h1-eth0:10.0.0.1 pid=2333> , 'c0': <Controller c0: 127.0.0.1:6653 pid=2326> , 's1': <OVSSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=2340> }
```

知道個節點（object）可以使用的參數及方法：

```bash
mininet> py dir(h1)
['IP', 'MAC', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_popen', 'addIntf', 'checkSetup', 'cleanup', 'cmd', 'cmdPrint', 'config', 'configDefault', 'connectionsTo', 'defaultIntf', 'deleteIntfs', 'execed', 'fdToNode', 'inNamespace', 'inToNode', 'intf', 'intfIsUp', 'intfList', 'intfNames', 'intfs', 'isSetup', 'lastCmd', 'lastPid', 'linkTo', 'monitor', 'mountPrivateDirs', 'name', 'nameToIntf', 'newPort', 'outToNode', 'params', 'pexec', 'pid', 'pollOut', 'popen', 'portBase', 'ports', 'privateDirs', 'read', 'readbuf', 'readline', 'sendCmd', 'sendInt', 'setARP', 'setDefaultRoute', 'setHostRoute', 'setIP', 'setMAC', 'setParam', 'setup', 'shell', 'startShell', 'stdin', 'stdout', 'stop', 'terminate', 'unmountPrivateDirs', 'waitOutput', 'waitReadable', 'waiting', 'write']
```

或是直接看文件的方式，瞭解使用方式：

```bash
mininet> py help(h1)
```
> 非常建議使用

觀察節點（object）的參數狀況：

```bash
mininet> py h1.IP()
10.0.0.1
```

### 開關結點間的連結

節點間的連結在 Mininet 中，只需要簡單的指令，就可以自在操作。首先示範斷開連結：

```bash
mininet> link s1 h1 down
mininet> net
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0
c0
mininet> h1 ping -c1 h2
connect: Network is unreachable
```
雖然利用```net```看起來```h1```跟```s1```仍是有連結的，但實際上使用```ping```，是可以發現連結確實被斷開了。接下來，把它接回去：

```bash
mininet> link s1 h1 up
mininet> h1 ping -c1 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=1.44 ms

--- 10.0.0.2 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 1.443/1.443/1.443/0.000 ms
```

> Mininet 的介紹就到一個段落。如想自行撰寫 Mininet 的部屬程式，建議參考 [Mininet 提供的範例](https://github.com/mininet/mininet/tree/master/examples)。

## 參考

[Mininet Walkthrough](http://mininet.org/walkthrough/)
