from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController

UP_PORT = 1
RIGHT_PORT = 2
DOWN_PORT = 3
LEFT_PORT = 4
HOST_PORT = 5

GIRD_NUM = 5

if '__main__' == __name__:
	net = Mininet(controller=RemoteController)
	c0 = net.addController('c0',ip='192.168.99.123', port=6633)
	switch_map = {}
	host = net.addHost('host')
	for i in xrange(1, GIRD_NUM * GIRD_NUM + 1):
		switch_name = "s%d" % i
		tmp_switch = net.addSwitch(switch_name, protocols="OpenFlow13")
		switch_map.update({i:tmp_switch})
		left_switch = i-1
		if left_switch > 0 and i % GIRD_NUM != 1:
			net.addLink(tmp_switch, switch_map[left_switch], port1=LEFT_PORT, port2=RIGHT_PORT)
		up_switch = i-GIRD_NUM
		if up_switch > 0:
			net.addLink(tmp_switch, switch_map[up_switch], port1=UP_PORT, port2=DOWN_PORT)
		host_ip = "10.0.0.%d/8" % i
		host_mac = "00:00:00:00:00:%02x" % i

		net.addLink(tmp_switch, host, port1=HOST_PORT, addr2=host_mac, params2={'ip':host_ip})

	net.build()
	c0.start()
	for switch in switch_map:
		switch_map[switch].start([c0])

	CLI(net)
	net.stop()