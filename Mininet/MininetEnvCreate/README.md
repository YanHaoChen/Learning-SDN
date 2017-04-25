# 使用 Python 建立 Mininet 環境
此篇將介紹如何使用 Python 建立 Mininet 環境，並在環境中連結外部Controller 及直接在程式中加入預設規則（OpenFlow entry）。

> 一般來說，預設規格應該由 Controller 下達，在此僅介紹一種加入預設規則的方式，並非都要用此方式。

## 建立的環境
* RemoteController：1 台
* Switch：1 台
* Host：2 台

## 需要的套件

```python
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController
```

## 建立環境

```python
if '__main__' == __name__:
	# 宣告 Mininet 使用的 Controller 種類
	net = Mininet(controller=RemoteController)
	
	# 指定 Controller 的 IP 及 Port，進行初始化
	c0 = net.addController('c0',ip='Controller ip', port=6633)
	
	# 加入 Switch
	s1 = net.addSwitch('s1')
	
	# 加入主機，並指定 MAC
	h1 = net.addHost('h1', mac='00:00:00:00:00:01')
	h2 = net.addHost('h2', mac='00:00:00:00:00:02')
	
	# 建立連線
	# port1 指定 s1 要使用的 port 號，port2 則是 h1 的 port 號
	net.addLink(s1, h1, port1=1, port2=1)
	net.addLink(s1, h2, port1=2, port2=1)
	
	# 建立 Mininet
	net.build()
	
	# 啟動 Controller
	c0.start()
	
	# 啟動 Switch，並指定連結的 Controller 為 c0
	s1.start([c0])
	
```

> 如果還沒有打算加入外部的 Controller，請將有`c0`的部分皆進行註解，並修改以下兩行程式碼：
> 
> ```python
>  net = Mininet(controller=RemoteController)
>  -> net = Mininet(controller=None)
> 
>  net.build()
>  -> net.start()

## 加入規則

此加入規則的方式，其實就是從此程式，直接輸入指令到虛擬的主機中（Switch）。

```python
	...
	s1.start([c0])
	
	s1.cmdPrint('ovs-ofctl add-flow s1 "in_port=1, actions=output:2"')
	s1.cmdPrint('ovs-ofctl add-flow s1 "in_port=2, actions=output:1"')

```

> 其中的雙引號，是為了將`in_port=1, actions=output:2`視為一個字串執行。如沒有加雙引號，也是可以執行，但請注意在這串文字之間是否有空格，如有則不會視為一個字串，也因此無法加入規則。

## 開啟 CLI 互動介面

所謂的 CLI 互動介面，就是直接執行 `mn` 時，出現的介面。就像這樣：

```python
mininet>...
```

```
	# 執行互動介面
	CLI(net)
	# 互動介面停止後，則結束 Mininet
	net.stop()
```