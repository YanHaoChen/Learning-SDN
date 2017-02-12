# Cumulus VX 使用入門（登入、控制 Interface 狀態）

以下將介紹 Cumulus VX 的基本操作方式。

### 登入

在 Cumulus VX 下，預設的帳號為`cumulus`，密碼則是`CumulusLinux!`：

```shell
Debian GNU/Linux 8 cumulus tty1

cumulus login: cumulus
Password:"輸入密碼 CumulusLinux! 登入"
```

> 建議在登入後，可以利用指令`passwd`修改密碼，方便往後的登入。

### Interface 設定

也可謂是 Cumulus 網路設定上的主軸。用來變更設定的檔案為`/etc/network/interfaces`：

```shell
$ cat /etc/network/interfaces
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*.intf

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
auto eth0
iface eth0 inet dhcp
```
其中的`lo`，是預先設定好的本地網路 interface，並將 IP address 配給為`127.0.0.1`。

`auto`標籤則是用來歸類 interface 的類別，如設定為`auto`，在往後的操作中，只需要使用特定指令參數，就可以對此類別的 interface 進行管理。

### 控制 Interface 狀態的指令

能控制 Interface 狀態的指令有三個：

* ifup：開啟 interface，或在更動已存在的 interface 後使用。
* ifdown：關閉 interface。
* ifreload：同（ifdown + ifup），將 interface 關閉後，再開啟。

使用方式：

```shell
$ sudo ifup "指定的 interface 名稱"
$ sudo ifdown "指定的 interface 名稱"
$ sudo ifreload "指定的 interface 名稱"
```

### 一次控制所有類別為 auto 的 interface

這也是 auto 類別的好處，因為只要在上述指令後加上`-a`，就會將此指令動作套用在所以類別為 auto 的 interface 上。

使用方式：

```shell
$ sudo ifup -a
$ sudo ifdown -a
$ sudo ifreload -a
```



