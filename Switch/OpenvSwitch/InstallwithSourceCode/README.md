# Install Open vSwitch with Source Code

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

先利用`get clone`將 OVS 的原始碼下載下來：

```shell
$ git clone https://github.com/openvswitch/ovs.git
```
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
$ sudo make
```

接下來，模組安裝入系統中：

```shell
$ sudo make install
```

另外，也因為我們有建立 kernel modules 的部分，所以還需要執行這項指令：

```shell
$ sudo make modules_install
```
> 如果執行後得到訊息：
>
> ```shell
> ...
> Can't read private key
> ...
> ```
> 請不用擔心，並沒有出錯。[詳情](http://discuss.openvswitch.narkive.com/c3Zva9hW/ovs-discuss-get-errors-when-i-try-to-install-ovs-2-0-from-souce-code-can-t-read-private-key)

載入核心模組：

```shell
sudo /sbin/modprobe openvswitch
``` 

確認是否已經載入：

```shell
$ sudo /sbin/lsmod | grep openvswitch
openvswitch            70989  0
vxlan                  37611  1 openvswitch
gre                    13796  1 openvswitch
libcrc32c              12644  1 openvswitch
```

## 啟動

再啟動之前，需要先設定好 ovs-vswitchd 所依賴的資料庫，也就是 ovsdb-server。設定方式如下：

```shell
$ mkdir -p /usr/local/etc/openvswitch
$ sudo ovsdb-tool create /usr/local/etc/openvswitch/conf.db \
    vswitchd/vswitch.ovsschema
```
設定資料庫連結：

```shell
$ mkdir -p /usr/local/var/run/openvswitch
$ sudo ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
    --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
    --private-key=db:Open_vSwitch,SSL,private_key \
    --certificate=db:Open_vSwitch,SSL,certificate \
    --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
    --pidfile --detach --log-file
```

使用 ovs-vsctl 初始化資料庫：

```shell
$ sudo ovs-vsctl --no-wait init
```

開始連結：

```shell
$ sudo ovs-vswitchd --pidfile --detach --log-file
```

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