# Step 1:初步了解 ONOS 並安裝

ONOS 可以有很多元的方式，部署在各種的 OS 上。ONOS 的核心團隊是以 **Ubuntu 16.04 LTS** 當作主要開發用的 OS 版本，所以這篇文件的安裝環境也是使用此版本的 OS。

再開始動手安裝前，先瞭解 ONOS 中設定的角色定義：

* Target machine：ONOS 所在的環境內的基本單位。一個 ONOS 環境內，至少會有一台 Target machine，並在其中運行 ONOS 系統。此主機除可以獨自運行 ONOS 外，可利用 Management machine 對它進行進一步的管理。

* Management machine：在 ONOS 所在的環境內，並非必備的角色。它能用來部署、管理環境內的 Target machine。

* Cluster：一群 Target machine 一起合作、運作，組成一個分散式的系統。為整體網路環境進行改善及優化。