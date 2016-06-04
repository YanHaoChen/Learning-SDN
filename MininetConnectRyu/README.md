# Mininet 連結 Ryu

### 用Mininet建立一個網路拓樸，並進行連接Ryu前的準備工作

```
$ sudo mn --topo single,3 --mac --switch ovsk --controller=remote,ip=192.168.1.110,port=6633 -x
```
參數意義：

```
//建立一個拓捕，包含3台host、1台switch
--topo single,3

//自動設定host的MAC位址
--mac

//指定switch使用Open vSwitch(ovsk)
--switch ovsk

//選定外部controller(--controller=remote)
//外部controller(Ryu)的ip(ip=192.168.1.110)
//外部controller(Ryu)的port(port=6633)
--controller=remote,ip=192.168.1.110,port=6633

//開啟各台設備(host、switch、controoler)的terminal，這也是為甚麼建議Mininet安裝在Ubuntu Desktop版上的原因(可以一次顯示多個terminal)
-x
```
執行後，Mininet就會建立一個網路，包含3台host、1台ovs switch及1台連結外部的controller（Ryu）。要注意的是，switch尚未進行設定（ovs的bridge使用的協定為何），如果沒有設定好，Ryu是沒辦法正常運作的。

> 在執行前，記得先開啟Ryu的主機，不然會一直卡在add controller

在此，就會建立出一個網路拓樸，但它並未與連接好controller，因此你會發現以下這行訊息：（ip及port就看你當初設定的是什麼，所以你的狀況不一定是顯示192.168.1.110:6633）

```
Unable to contact the remote controller at 192.168.1.110:6633
```
> 以下的指令請使用剛剛開啟的s1 terminal執行

接下來設定switch，也就是連接Ryu的關鍵。首先你可以先利用以下指令，瞭解一下你的switch的狀況：

```
$ ovs-vsctl show
$ ovs-dpctl show
```

執行完後，你可以發現，你的switch多了3個port，並連接到3台host。確認後，接下來就是設定Bridge，設定方法如下：

```
//將Bridge s1的訊息協定設定為OpenFlow13
$ ovs-vsctl set Bridge s1 protocols=OpenFlow13
```

檢查一下，是否設定好了：

```
$ ovs-ofctl -O OpenFlow13 dump-flows s1

```

執行後，你會看到這樣：

```
OFPST_FLOW reply (OF1.3) (xid=0x2):
```

### 與Ryu連接

> 把工作環境換到Ryu的主機上

基本上，只要輸入一行，運行它即可：

```
//開啟Ryu的範例程式
$ ryu-manager --verbose ryu.app.simple_switch_13
```

Ryu主機上，就會顯示很多行執行結果。當你看到最後一行是：

```
move onto main mode
```
也代表完成連結。可透過Mininet操縱整個網路：

```
//要求host h1對host h2進行ping的動作
mininet> h1 ping -c2 h2
```
且在Ryu上，也會顯示封包流動狀況。