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