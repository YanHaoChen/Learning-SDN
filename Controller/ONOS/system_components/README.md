# System Components

> 翻譯：[System Components](https://wiki.onosproject.org/display/test/System+Components)

在此章節，將介紹在 ONOS 中，主要的子系統及架構。

## 分層的系統

就像前一章所提，ONOS 的系統層級是以功能進行區分的。接下來的介紹，將以此圖作為主軸，進行討論。

![onos-stack](https://github.com/OSE-Lab/Learning-SDN/raw/master/Controller/ONOS/system_components/images/onos-stack.png)

## 服務及子系統

**服務**的組成是為實現一個功能，一個服務可能包含多個元件，且這些元件的種類垂直跨越系統的各個層級，也因此就像是將這些元件堆疊起來一樣。介於服務就像是個**子系統**，所以在此文件中，**服務**跟**子系統**具有相同的意思。

ONOS 定義了幾個主要的服務：

* Device Subsystem：管理、紀錄基礎設備。
* Link Subsystem：管理、紀錄基礎設備間的連接狀況。
* Host Subsystem：管理、紀錄終端主機的資訊及在拓樸的邏輯位置。
* Topology Subsystem：管理網路拓樸的時序快照。
* PathService：使用最新的拓樸快照，運算、找尋基礎設備或終端主機間的路徑。
* FlowRule Subsystem：管理、紀錄基礎建設中的 flow 規則，並提供 flow 的狀態資訊。
* Packet Subsystem：允許ONOS 中的應用程式，接收、監聽來自網路基礎設備的封包，並能將封包轉送至網路中一或多個網路基礎設備中。

下圖為 ONOS 中具備的多元子系統。其中包含已經完成及一些將要發佈的子系統：

![onos-subsystems](https://github.com/OSE-Lab/Learning-SDN/raw/master/Controller/ONOS/system_components/images/onos-subsystems.png)