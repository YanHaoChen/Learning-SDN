# System Components

> 翻譯：[System Components](https://wiki.onosproject.org/display/test/System+Components)

在此章節，將介紹在 ONOS 中，主要的子系統及架構。

## 分層的系統

就像前一章所提，ONOS 的系統層級是以功能進行區分的。接下來的介紹，將以此圖作為主軸，進行討論。

![onos-stack(from https://wiki.onosproject.org/)](https://github.com/OSE-Lab/Learning-SDN/raw/master/Controller/ONOS/system_components/images/onos-stack.png)

## 服務及子系統

**服務（Service）**的組成是為實現一個功能，一個服務可能包含多個元件，且這些元件的種類垂直跨越系統的各個層級，也因此就像是將這些元件堆疊起來一樣。介於服務就像是個**子系統（Subsystem）**，所以在此文件中，**服務**跟**子系統**具有相同的意思。

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

一個 Provider 將會賦予一個關聯 `ProviderId`。此 ID 的主要用意在於提供外部識別此 Provider 所屬的 Provider 家族。進一步的允許因此 Provider 而存在的設備或模組保留與此 Provider 間的關聯，即使此 Provider 是否安裝或卸載。

`ProviderId`使用 URI（統一資源標誌符）提供一種較寬鬆的設備與 Provider （除了指定的 Provider 及可替代的同家族 Provider）的配對方式。也因此，設備可能並不是直接連接指定的 Provider 本身。

#### Multiple Providers

一個子系統可能關聯多個 Provider. 在這種情況下，Provider 將區分為`primary`及`ancillary`。Primary Provider 們擁有與服務間的實體關聯，Ancillary Provider 們提供資訊給服務的方式如 Overlay 的概念。其運作方式，為給主要的 Provider 的資訊較高的優先權，目的也就像 Overlay 解決與 Underlay 之間衝突的問題一樣。

Device Subsystem 就是能支援 Multiple Providers 的服務。

###Manager

當一個元件放置於核心當中，Mananger 將會收到來自 Providers 的資訊，並將此資訊提供給**應用程式（Applications）**或其他的服務。Manager 提供以下介面：

* 北向服務（`Service`）介面：連接應用程式或者其他可學習特定網路環境的核心元件。
* 管理者服務（`AdminService`）介面：接收管理者指令，並在網路環境或系統中加入此指令。
* 南向供應者註冊（`ProviderRegistry`）介面：連接可以註冊在此 Manager 中的 Provider，進一步可以讓 Manager 與 Provider 互動。
* 南向供應者服務（`ProviderService`）介面：提供給已註冊的 Provider 使用，讓 Provider 可以傳送及接收來自 Manager 的訊息。

使用上述介面，有可會同步地接收到用於尋訪各服務的訊息，及異步地接受到事件監聽者的訊息。（以`ListenerService`介面為例。每個服務介面註冊事件時會使用到它，以及實作`Eventlistener`介面時用它來接受觸發的事件）。