# Mininet 連結 Ryu

### 用 Mininet 建立一個網路拓樸，並進行連接 Ryu 前的準備工作

```shell
$ sudo mn --topo single,3 --mac --switch ovsk --controller=remote,ip=192.168.1.110,port=6633 -x
```
參數意義：

```shell
//建立一個拓捕，包含3台 host、1台 switch
--topo single,3

//自動設定 host 的 MAC 位址
--mac

//指定 switch 使用 Open vSwitch(ovsk)
--switch ovsk

//選定外部 controller(--controller=remote)
//外部 controller(Ryu)的 ip(ip=192.168.1.110)
//外部 controller(Ryu)的 port(port=6633)
--controller=remote,ip=192.168.1.110,port=6633

//開啟各台設備(host、switch、controoler)的 terminal，這也是為甚麼建議 Mininet 安裝在 Ubuntu Desktop 版上的原因(可以一次顯示多個 terminal)
-x
```
執行後，Mininet 就會建立一個網路，包含3台 host、1台 ovs switch 及1台連結外部的 controller（Ryu）。要注意的是，switch 尚未進行設定（ovs 的 bridge 使用的協定為何），如果沒有設定好，Ryu 是沒辦法正常運作的。對於Ryu還沒有認識的小夥伴可以先移步到[Controller](https://github.com/OSE-Lab/Learning-SDN/tree/master/Controller)的區域，先將Controller的Server先架起。

> 在執行前，記得先開啟 Ryu 的主機，不然會一直卡在 add controller。

在此，就會建立出一個網路拓樸，但它並未與連接好 controller，因此你會發現以下這行訊息：（ ip 及 port 就看你當初設定的是什麼，所以你的狀況不一定是顯示192.168.1.110:6633）

```shell
Unable to contact the remote controller at 192.168.1.110:6633
```
> 以下的指令請使用剛剛開啟的 s1 terminal 執行

接下來設定 switch，也就是連接 Ryu 的關鍵。首先你可以先利用以下指令，瞭解一下你的 switch 的狀況：

```shell
$ ovs-vsctl show
$ ovs-dpctl show
```

執行完後，你可以發現，你的 switch 多了3個 port，並連接到3台 host。確認後，接下來就是設定 Bridge，設定方法如下：

```shell
//將 Bridge s1 的訊息協定設定為 OpenFlow13
$ ovs-vsctl set Bridge s1 protocols=OpenFlow13
```

檢查一下，是否設定好了：

```shell
$ ovs-ofctl -O OpenFlow13 dump-flows s1
```

執行後，你會看到這樣：

```shell
OFPST_FLOW reply (OF1.3) (xid=0x2):
```

### 與 Ryu 連接

> 把工作環境換到 Ryu 的主機上

基本上，只要輸入一行，運行它即可：

```shell
//開啟 Ryu 的範例程式
$ ryu-manager --verbose ryu.app.simple_switch_13
```

Ryu 主機上，就會顯示很多行執行結果。當你看到最後一行是：

```shell
move onto main mode
```
也代表完成連結。可透過 Mininet 操縱整個網路：

```shell
//要求 host h1 對 host h2 進行 ping 的動作
mininet> h1 ping -c2 h2
```
且在 Ryu 上，也會顯示封包流動狀況。
