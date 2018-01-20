# 利用 Vagrant 快速建立 1 台 Controller（Ryu） 2 台 OVS 之虛擬環境

單以 Mininet 建立環境會產生一些限制。例如，其中建立的 OVS Switch 皆由同一台 OVS 切 Bridge 而來， 這種情況下，我們很難評估單個 OVS 的效能狀況。雖然使用 Vagrant 仍是以模擬的方式進行，但在效能的劃分上，就比使用 Mininet 的情況下，分明許多。本文將使用一個 Vagrantfile 及兩隻腳本（安裝 Ryu 及 OVS 用）完成。

## 環境需求

* 具備 Vagrant、VirtualBox

## 取得腳本

* Git

```Shell
$ git clone https://github.com/OSE-Lab/Learning-SDN.git
```

* 直接下載
  * [Vagrantfile](https://github.com/OSE-Lab/Learning-SDN/tree/master/Experiment/Ryu1OVS2/Vagrantfile)
  * [ovs_install.sh](https://github.com/OSE-Lab/Learning-SDN/tree/master/Experiment/Ryu1OVS2/ovs_install.sh)
  * [ryu_install.sh](https://github.com/OSE-Lab/Learning-SDN/tree/master/Experiment/Ryu1OVS2/ryu_install.sh)

> 如是直接下載，請確定這個檔案都在存放在同一個目錄之中。

## 運行

直接在存放腳本的目錄下執行：

```Shell
$ vagrant up
```

執行完後，環境就建立完成！

> 因建立 OVS 需要大量的編譯時間，大概會需要跑 10 至 30 分鐘。

### 登入各虛擬機

* Ryu：

```Shell
$ vagrant ssh controller
```

* 第一台 OVS：

```Shell
$ vagrant ssh ovs1
```

- 第二台 OVS：

```Shell
$ vagrant ssh ovs2
```

>如 OVS 不只兩台，其登入規則如下：
>
>- 第 N 台 OVS：
>
>```
>$ vagrant ssh ovs[N]
>```

## 細微客製化

透過更改腳本，可以進一步的將環境微調，以符合特定需求。

### OVS 個數

例如：建立 3 個 OVS。

 原 Vagrantfile：

```Shell
...
     (1..2).each do |i| 
         config.vm.define "ovs#{i}" do |ovs|
            ovs.vm.box = "ubuntu/trusty64"
...
```

更改後：

```Shell
...
     (1..3).each do |i| 
         config.vm.define "ovs#{i}" do |ovs|
            ovs.vm.box = "ubuntu/trusty64"
...
```

> 請注意，此數值會影響 IP 的給定。

