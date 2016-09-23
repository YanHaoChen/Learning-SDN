# How to Install Ryu

### 官方有提供最簡單的方式(不建議)：
```shell
$ pip install ryu
```
> 單利用 pip 進行安裝，還是會遇到一些問題，並不是一個指令就結束，所以不建議使用這種方式。

### 方式二(建議)：
其方式，是將所需套件自行安裝，並盡量由同一個套件管理系統（pip）安裝，最後再將 Ryu 下載下來，直接安裝。

1. 安裝所需要的套件
```shell
$ sudo apt-get update //更新可取得的套件版本
$ sudo apt-get install python-pip //安裝 pyhon套件管理器 pip

//以下是相關套件
$ sudo apt-get install python-greenlet //pip 安裝 greenlet 時有錯誤，只好使用 apt-get 進行安裝
$ sudo pip install oslo.config
$ sudo pip install msgpack-python
$ sudo pip install eventlet
$ sudo pip install routes
$ sudo pip install webob
$ sudo pip install paramiko

//pip 並沒有辦法直接取的要求的項目 ovs>=2.6.0.dev0（目前 ovs 最新穩定版本為2.5.0），所以只好自行指定安裝：
$ sudo pip install https://pypi.python.org/packages/source/o/ovs/ovs-2.6.0.dev0.tar.gz
```

2. 利用 git 載下 Ryu，並執行安裝
```shell
$ git clone git://github.com/osrg/ryu.git 
$ cd ryu
$ sudo python ./setup.py install
```
你現在可以嘗試看看執行它，例如像是這樣：
```shell
$ ryu-manager
```
如果你看到的是這樣：
```shell
loading app ryu.controller.ofp_handler
instantiating app ryu.controller.ofp_hendler of OFPHandler
```
恭喜你，安裝成功！
