# System Components

> 翻譯：[System Components](https://wiki.onosproject.org/display/test/System+Components)

在此章節，將介紹在 ONOS 中，主要的子系統及架構。

## 分層的系統

就像前一章所提，ONOS 的系統層級是以功能進行區分的。接下來的介紹，將以此圖作為主軸，進行討論。

![onos-stack(from https://wiki.onosproject.org/)](https://github.com/OSE-Lab/Learning-SDN/raw/master/Controller/ONOS/system_components/images/onos-stack.png)

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

![onos-subsystems(from https://wiki.onosproject.org/)](https://github.com/OSE-Lab/Learning-SDN/raw/master/Controller/ONOS/system_components/images/onos-subsystems.png)

## 子系統架構

每個子系統的元件分別散佈在三個主要層級中，並可藉由一或多個  Java 介面識別他們實作的內容。

下圖為子系統中元件之間的關係圖。圖中的上虛線，由北向 API 所定義，下虛線則由南向 API 。

![onos-service(from https://wiki.onosproject.org/)](https://github.com/OSE-Lab/Learning-SDN/raw/master/Controller/ONOS/system_components/images/onos-service.png)

### Provider

在 ONOS 中屬於最底層，Provider 的介面透過特定的協定連接網路，並透過`ProviderService`與 ONOS 核心（中間層）溝通。

Protocol-aware provider 則是藉由多樣（控制用、設定用）的協定管理網路環境。並將特定服務所需求的網路資訊傳入核心中。Provider 提供給特定服務的資訊有可能是取自其他子系統並加以轉換而來。

有些 Provider 則是需要透過核心下達指令，將它們應用於特定的協定下。這些動作則透過`Provider`介面，下達至 Provider 中。

#### Provider ID

一個 Provider 將會賦予一個關聯 `PrviderId`。此 ID 的主要用意在於提供外部識別此 Provider 的所屬的 Provider 家族。