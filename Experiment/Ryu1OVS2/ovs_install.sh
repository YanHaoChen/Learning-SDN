#! /bin/bash

sudo locale-gen zh_TW.UTF-8
sudo apt-get update -y
sudo apt-get install openssl -y
sudo apt-get install libcap-ng-dev -y
sudo apt-get install libtool -y
sudo apt-get install autoconf -y
sudo apt-get install git -y

sudo apt-get install libffi-dev -y
sudo apt-get install libssl-dev -y
sudo apt-get install python-pip -y
echo y | sudo pip install --upgrade pip 
echo y | sudo pip install pyopenssl
echo y | sudo pip install ndg-httpsclient
echo y | sudo pip install pyasn1
echo y | sudo pip install six
git clone https://github.com/openvswitch/ovs.git
cd ovs
git checkout v2.7.0
sh boot.sh
sh ./configure --with-linux=/lib/modules/$(uname -r)/build
make
sudo make install
sudo make modules_install

config_file="/etc/depmod.d/openvswitch.conf"
for module in datapath/linux/*.ko; do
        modname="$(basename ${module})"
        echo "override ${modname%.ko} * extra" >> "$config_file"
        echo "override ${modname%.ko} * weak-updates" >> "$config_file"
done

depmod -a

sudo /sbin/modprobe openvswitch

mkdir -p /usr/local/etc/openvswitch
sudo ovsdb-tool create /usr/local/etc/openvswitch/conf.db \
    vswitchd/vswitch.ovsschema
