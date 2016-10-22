from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.term import makeTerm

if '__main__' == __name__:

	net = Mininet(controller=RemoteController)
	c0 = net.addController('c0',ip='192.168.99.101', port=6633)

	s1 = net.addSwitch('s1')

	h1 = net.addHost('h1', mac='00:00:00:00:00:01')
	h2 = net.addHost('h2', mac='00:00:00:00:00:02')
	h3 = net.addHost('h3', mac='00:00:00:00:00:03')

	net.addLink(s1, h1)
	net.addLink(s1, h2)
	net.addLink(s1, h3)

	net.build()

	c0.start()
	s1.start([c0])

	net.terms.append(makeTerm(s1))

	CLI(net)
	net.stop()
