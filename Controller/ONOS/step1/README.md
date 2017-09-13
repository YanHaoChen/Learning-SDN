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

> 安裝完後，記得在`/etc/environment`這個檔案中，加入`JAVA_HOME`此環境變數。如下：
> 
> ```
> # 在 /etc/environment 中，加入此行
> JAVA_HOME="/usr/lib/jvm/java-8-oracle"
> ```

#### Curl

```shell
$ sudo apt-get install curl
```