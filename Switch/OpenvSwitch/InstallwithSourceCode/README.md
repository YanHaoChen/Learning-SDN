# Install Open vSwitch with Source Code

> 更新日期：12/2017

以下將介紹如何使用 Source Code 將 Open vSwitch（OVS）安裝在 Ubuntu 上。OVS 官方提及，如要安裝會需要具備以下套件：

> 以下的步驟，是參考 OVS 的 [Installation Guide](https://github.com/openvswitch/ovs/blob/master/Documentation/intro/install/general.rst) 進行，如有不清楚的地方，可以直接參考官方版本。

* A C compiler:
  * GCC 4.X
* libssl
* libcap-ng
* python 2.7（six）

Ubuntu 本身就帶有 GCC 且版本也在 4 以上，所以第一個條件不用擔心。接下來的部分，就需要自行安裝。首先，更新可安裝的套件：

```shell
$ sudo apt-get update
```

接下來，安裝 libssl 相關套件：

```shell
$ sudo apt-get install libssl-dev
$ sudo apt-get install openssl
```

安裝 libcap-ng：

```shell
$ sudo apt-get install libcap-ng-dev
```

Python 2.7 在 Ubuntu 也是本身就有安裝的。所以我們還需要的是其中的套件 six。利用 pip 來安裝：

```shell
$ sudo apt-get install python-pip
$ sudo pip install six
```

其他在安裝上需要的套件：

```shell
$ sudo apt-get install libtool
$ sudo apt-get install autoconf
```

最後，安裝下載 Source Code 用的 git：

```shell
$ sudo apt-get install git
```

## 安裝的準備作業

先利用 `get clone` 將 OVS 的原始碼下載下來：

```shell
$ git clone https://github.com/openvswitch/ovs.git
```
選擇想安裝的版本：

```shell
$ git checkout v2.7.0
```

> 也可以直接 checkout 到想安裝的 branch 上

接下來，到 Source Code 目錄中，並執行 boot.sh 產生安裝所需的 configure 檔：

```shell
$ cd ovs
$ ./boot.sh
```

我們可以利用執行 configure 檔時，給予參數。透過參數，可以決定安裝的內容（Makefile 的內容）。在此示範安裝 Linux kernel module 的參數給定方式：

```shell
$ ./configure --with-linux=/lib/modules/$(uname -r)/build
```

## 編譯、安裝

使用 make 進行編譯：

```shell
$ make
```

接下來，模組安裝入系統中：

```shell
$ sudo make install
```

另外，也因為我們有建立 kernel modules 的部分，所以還需要執行這項指令：

```shell
$ sudo make modules_install
```
因系統可能曾安裝過 OVS kernel module，所以我們需要複寫 `openvswitch.conf` ，讓系統指向正確 kernel module 位置（這次編譯產生的 module）。腳本如下：

```
#! /bin/bash

config_file="/etc/depmod.d/openvswitch.conf"
for module in datapath/linux/*.ko; do
        modname="$(basename ${module})"
        echo "override ${modname%.ko} * extra" >> "$config_file"
        echo "override ${modname%.ko} * weak-updates" >> "$config_file"
done

depmod -a
```

> 此腳本（[prefer_this_kernel_module.sh](https://github.com/OSE-Lab/Learning-SDN/tree/master/Switch/OpenvSwitch/InstallwithSourceCode/prefer_this_kernel_module.sh)）請在 clone 下的的資料夾 `ovs` 中執行。
>
> 如果執行後得到訊息：
>
> ```
> ...
> Can't read private key
> ...
> ```
>
> 請不用擔心，並沒有出錯。[詳情](http://discuss.openvswitch.narkive.com/c3Zva9hW/ovs-discuss-get-errors-when-i-try-to-install-ovs-2-0-from-souce-code-can-t-read-private-key)

載入核心模組：

```shell
sudo /sbin/modprobe openvswitch
```

確認是否已經載入：

```shell
$ /sbin/lsmod | grep openvswitch
openvswitch           257342  0
nf_nat_ipv6            13279  1 openvswitch
nf_nat_ipv4            13263  1 openvswitch
nf_defrag_ipv6         34768  2 openvswitch,nf_conntrack_ipv6
nf_defrag_ipv4         12758  2 openvswitch,nf_conntrack_ipv4
nf_nat                 21841  3 openvswitch,nf_nat_ipv4,nf_nat_ipv6
nf_conntrack           97201  6 openvswitch,nf_nat,nf_nat_ipv4,nf_nat_ipv6,nf_conntrack_ipv4,nf_conntrack_ipv6
gre                    13796  1 openvswitch
libcrc32c              12644  1 openvswitch
```

## 啟動

再啟動之前，需要先設定好 OVS 所需要的配置檔。產生方式如下：

```shell
$ mkdir -p /usr/local/etc/openvswitch
$ sudo ovsdb-tool create /usr/local/etc/openvswitch/conf.db \
    vswitchd/vswitch.ovsschema
```
接下來，透過 OVS 提供的好用工具 `ovs-ctl` 來啟動 OVS！

> 除了啟動，還其它的操作可以利用方便的 `ovs-ctl` 進行。[ovs-ctl](http://openvswitch.org/support/dist-docs/ovs-ctl.8.txt) 

```Sh
$ sudo /usr/local/share/openvswitch/scripts/ovs-ctl --system-id=random start 
```

`--system-id=random` 的用意在於，給此 OVS 一個特定的編號（UUID）。如果沒有要特別指定的編號，就可以像上述指令，給予參數 `random`。

> 在我的環境中使用指令：
>
> ```shell
> export PATH=$PATH:/usr/local/share/openvswitch/scripts
> ```
>
> 後，`root` 的環境變數中依然沒有加入此路徑。因此，將此路徑直接加入 `/etc/environment` 中，即可被 `root` 找到。此動作為可選（Optional），單純為了往後操作方便。

現在，已經完成 OVS 的安裝了。接下來，可以透過設定一個 bridge 來確定是否安裝成功：

```shell
$ sudo ovs-vsctl add-br br0
$ sudo ovs-vsctl show
0973ab3d-96e8-4a49-a2c2-dbc8c83bb6c4
    Bridge "br0"
        Port "br0"
            Interface "br0"
                type: internal
```

安裝成功！
