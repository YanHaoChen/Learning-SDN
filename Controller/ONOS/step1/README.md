# Step 1：初步瞭解 ONOS 並安裝

ONOS 可以有很多元的方式，部署在各種的 OS 上。ONOS 的核心團隊是以 **Ubuntu 16.04 LTS** 當作主要開發用的 OS 版本，所以這篇文件的安裝環境也是使用此版本的 OS。

再開始動手安裝前，先瞭解 ONOS 中設定的角色定義：

* Target machine：ONOS 所在的環境內的基本單位。一個 ONOS 環境內，至少會有一台 Target machine，並在其中運行 ONOS 系統。此主機除可以獨自運行 ONOS 外，可利用 Management machine 對它進行進一步的管理。

* Management machine：在 ONOS 所在的環境內，並非必備的角色。它能用來部署、管理環境內的 Target machine。

* Cluster：一群 Target machine 一起合作、運作，組成一個分散式的系統。為整體網路環境進行改善及優化。

## 環境需求

以下將說明架設 ONOS 的環境需求。

### 硬體需求

因為需要考慮的因素（叢集的大小、管理的網路大小等）很多，所以硬體的需求相當難直接的定義，但在此還是定義了一個最基本的需求：

* 2 core CPU
* 2 GB RAM
* 10 GB hdd
* 1 NIC（any speed）

### 連接（網路）需求

以下將討論 ONOS 整體環境、Target machine 及 Management machine 所需求的網路狀況。 

#### ONOS 整體環境

在建立一個 ONOS 環境，並不一定需要對外的網路。但比如說要下載 ONOS 原始檔或者其他的相依套件時，還是會需要用到對外網路。另一方面，如需要一些遠端的管理，譬如連接遠端 Management machine 進行整體環境管理，則可依需求連接對外網路。

#### 對於 Target machine

需要確保同叢集內的 Target machine 在 IP 層是可以互通的（簡單說，就是可以互相 ping 的到）。

#### 對於 Management machine

只要能利用 IP 層與其需要控制的 Target machine 連接即可（一樣是可以互相 ping 到即可）。

#### 須保留的 Port

以下列出 ONOS 在運行時會需要的 Port 號：

* 8181：提供 REST API 及 GUI 使用
* 8101：提供進入 ONOS 的 CLI 使用
* 9876：提供叢集內部的進行溝通用（Target machine 之間）
* 6653：（非必要）提供給 OpenFlow 使用
* 6640：（非必要）提拱給 OVSDB 使用

### 系統環境及軟體需求

以下將介紹安裝前的所需的設定及安裝的軟體。

#### User

ONOS 跟其他商業服務系統一樣，不應該以 root 執行。所以我們先加入一個專屬運行 ONOS 的系統使用者`sdn`，並創建一個同名的`group`：

```shell
sudo adduser sdn --system --group
```

#### Java8

ONOS 就是一個以 Java 建立的系統。另外，非常強烈建議使用 Oracle 1.8 這個版本。以下為在 Ubuntu 下，安裝此版本的方式：

```shell
$ sudo apt-get install software-properties-common -y && \
sudo add-apt-repository ppa:webupd8team/java -y && \
sudo apt-get update && \
echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections && \
sudo apt-get install oracle-java8-installer oracle-java8-set-default -y
```

> 安裝完後，記得在`/etc/environment`這個檔案中，加入`JAVA_HOME`此環境變數，並重新開機。如下：
> 
> ```
> # 在 /etc/environment 中，加入此行
> JAVA_HOME="/usr/lib/jvm/java-8-oracle"
> ```

#### Curl

```shell
$ sudo apt-get install curl
```

### 開始安裝（單機）

透過以下的安裝步驟，即可安裝好一台 Target machine。

#### 將 ONOS 放在`/opt`目錄下

```shell
# 確保 opt 目錄是存在的
$ sudo mkdir /opt
# 進入 opt 目錄
$ cd /opt
```

#### 安裝 ONOS

在此選擇的版本為`1.9.0`，現有的版本可參考 [Release Notes](https://wiki.onosproject.org/display/ONOS/Release+Notes)，再依需求下載。

```shell
$ sudo wget -c http://downloads.onosproject.org/release/onos-1.9.0.tar.gz
```
##### 解壓縮
```shell
$ sudo tar xzf onos-1.9.0.tar.gz
```

##### 重新命名解壓縮後的資料夾名稱
```shell
$ sudo mv onos-1.9.0 onos
```

##### 啟動（確定安裝成功）
```shell
$ /opt/onos/bin/onos-service start
Welcome to Open Network Operating System (ONOS)!
     ____  _  ______  ____
    / __ \/ |/ / __ \/ __/
   / /_/ /    / /_/ /\ \
   \____/_/|_/\____/___/

Documentation: wiki.onosproject.org
Tutorials:     tutorials.onosproject.org
Mailing lists: lists.onosproject.org

Come help out! Find out how at: contribute.onosproject.org

Hit '<tab>' for a list of available commands
and '[cmd] --help' for help on a specific command.
Hit '<ctrl-d>' or type 'system:shutdown' or 'logout' to shutdown ONOS.
```

#### 與 ONOS 互動

有兩種方式可以跟 ONOS 互動，分別為`CLI`及`GUI`。

> 預設帳號密碼為：onos/rocks。想加入新的使用者可以使用`onos\bin`中的`onos-user-password`及`onos-user-key`這兩項工具。

##### CLI

透過 ssh 進入 ONOS CLI 介面：

```shell
ssh -p 81 onos@<Target machine IP>
```

##### GUI

使用瀏覽器，輸入網址：

```shell
http://<Target machine>:8181/onos/ui/index.html
```

並輸入帳號密碼即可。

#### 將 ONOS 註冊在作業系統服務中

以下介紹的方式，是屬於 **Ubuntu 16.04 LTS** 的方式。其他 OS 可以參考[原文](https://wiki.onosproject.org/display/ONOS/Running+ONOS+as+a+service)。將 ONOS 註冊在系統服務中的好處在於，如遇到 Crash 等狀況，系統可以依配置檔，重啟服務進一步提高服務運作的穩定。

##### 複製啟動 ONOS 腳本至`init.d`中

```shell
sudo cp /opt/onos/init/onos.initd /etc/init.d/onos
```

##### 註冊服務至 Systemd 中

```shell
sudo cp /opt/onos/init/onos.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable onos
```

##### 服務控制

```shell
sudo systemctl {start|stop|status|restart} onos.service
```
