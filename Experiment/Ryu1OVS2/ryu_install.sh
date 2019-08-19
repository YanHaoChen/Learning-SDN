#! /bin/bash

sudo locale-gen zh_TW.UTF-8
sudo apt-get update -y
sudo apt-get install git -y

sudo apt-get install libffi-dev libssl-dev -y
sudo apt-get install python-pip -y
sudo apt-get install python-greenlet -y
echo y | sudo pip install --upgrade pip
echo y | sudo pip install pyopenssl
echo y | sudo pip install ndg-httpsclient
echo y | sudo pip install pyasn1

echo y | sudo pip install oslo.config
echo y | sudo pip install msgpack-python
echo y | sudo pip install eventlet==0.18.2
echo y | sudo pip install routes
echo y | sudo pip install webob
echo y | sudo pip install paramiko
echo y | sudo pip install tinyrpc
echo y | sudo pip install ovs

git clone git://github.com/osrg/ryu.git
cd ryu
sudo python ./setup.py install
