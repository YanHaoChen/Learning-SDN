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
$ sudo apt-get install python-pip //安裝 pyhon 套件管理器 pip
$ sudo apt-get install git

//以下是相關套件
$ sudo apt-get install python-greenlet //pip 安裝 greenlet 時有錯誤，只好使用 apt-get 進行安裝
$ sudo pip install --upgrade pip
$ sudo pip install oslo.config
$ sudo pip install msgpack
$ sudo pip install eventlet==0.18.2
$ sudo pip install routes
$ sudo pip install webob
$ sudo pip install paramiko
$ sudo pip install tinyrpc
$ sudo pip install ovs
```
或推薦直接使用以下批次下載
```shell
sudo pip install -r ./requirement.txt

```


> 如果是 Ubuntu 16.04 版的環境，在執行`sudo pip install --upgrade pip`此行後可能會出現問題。後來要安裝的模組，在安裝時出現這樣的提示：
>
> ```
> Traceback (most recent call last):
>   File "/usr/local/bin/pip", line 7, in <module>
>     from pip._internal import main
> ImportError: No module named _internal
> ```
>
> 此時請重新安裝 pip：
>
> ```
> $ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
> # 如果你的 python 就是 python2 的版本
> $ python get-pip.py --force-reinstall
> ```
>
> 解決方式參考來源：https://stackoverflow.com/questions/49940813/pip-no-module-named-internal
>
> 註：pip 原本有的模組也會需要重新安裝。 

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
