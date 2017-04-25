# -*- coding:utf-8 -*-
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController

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

    # 以指令的方式建立規則
    s1.cmdPrint('ovs-ofctl add-flow s1 "in_port=1, actions=output:2"')
    s1.cmdPrint('ovs-ofctl add-flow s1 "in_port=2, actions=output:1"')

	# 執行互動介面(mininet>...)
    CLI(net)
	# 互動介面停止後，則結束 Mininet
    net.stop()