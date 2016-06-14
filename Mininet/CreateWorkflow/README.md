# Create a Workflow


在 Mininet 中，用一行指令就建立起一個 workflow，且依輸入的參數，客製化建立。


### 你可以這樣做用：

```shell
sudo mn
```

取得一個最基本的 network，其中包含2台 host（h1,h2）、1台 switch（s1）、1台 controller（c0）。

### 如果想再做更多的設定，可以這樣用：
```shell
sudo mn --switch ovs --controller ref --topo tree,depth=2,fanout=8
```
以上指令的參數分別代表：

```shell
--switch ovs //switch 選擇使用 OpenvSwitch
--controller ref //controller 選擇使用 OpenFlow/Stanford reference controller
--topo tree,depth=2,fanout=8 //使用樹狀拓樸，深度為2，扇出為8
```
輸入指令後，將會模擬出64台 host、9台 switch、1台 controller。

### 跟建立出來的 network 進行互動：

建立好 network 後，在終端機將會出現 Mininet 的 CLI，就像這樣：

```shell
mininet>
```
將可利用 mininet CLI 輸入指令，來控制 network 的內部活動。例如，想要讓其中一台主機 ping 其他主機：

```shell
mininet>h2 ping h3
```

或者是要測試當中 http server 的反應，也可以快速在指定主機上，建立一個 http server，並透過 wget 測試 http server 的反應：

```shell
mininet>h2 python -m SimpleHTTPServer 80 >& /tmp/http.log &
mininet>h3 wget -O - h2
```

輸入指令後，會在 h2 上就會建立一個簡單的 http server，並透過 h3 使用 wget 取得 h2 上的 http server 所回傳的內容。

> ```wget -O - h2```這段指令，本來的格式是這樣```wget -O [file] [網址]```。現在的指令把```[file]```設定為```-```，wget 就會直接把結果顯示在 CLI 上，不會儲存成檔案。

### 運用 Python 客製化一個 network：
也可以寫一個 Python 程式，把 network 客製化成想要的樣子，並要求它執行特定指令，像這樣：

```python
from mininet.net import Mininet
from mininet.topolib import TreeTopo
tree4 = TreeTopo(depth=2,fanout=2)
net = Mininet(topo=tree4)
net.start()
h1, h4  = net.hosts[0], net.hosts[3]
print h1.cmd('ping -c1 %s' % h4.IP())
net.stop()
```
執行後，將會得到像這樣的結果：
```shell
$ sudo python YourPythonName.py
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=4.35 ms
--- 10.0.0.4 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 4.355/4.355/4.355/0.000 ms
```

如果看到以上內容，恭喜你成功寫出一個啟動 Mininet 且控制它的Python！

但如果你看到的是像以下這樣：

```shell
$ sudo python YourPythonName.py
ping: bad number of packets to tranmit.
```

不要灰心的太早，因為只是發生了一點小誤會，請注意你程式內的這段，並改成這樣：
```python
print h1.cmd('ping -c2 %s' % h4.IP())
```

很好，現在應該不會有誤會了。
