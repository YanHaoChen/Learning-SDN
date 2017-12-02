# Overview

> 翻譯：[ONOS: An Overview](https://wiki.onosproject.org/display/ONOS/ONOS+%3A+An+Overview)

在此，將以一個綜觀的角度，談論 ONOS 的整體架構及設計目的。

## 目標（Design Goals）

ONOS 是使用 OSGi 架構建置的多重模組（multi-module）專案。以下為 ONOS 想達到的目標及其中意涵：

* 將程式碼模組化：可以輕易的引入任何獨立的新功能。
* 可配置：可自由的啟用或關閉其中的功能，不管是系統啟動時或者正在運行。
* 關係區分：子系統間，需有明確的分界，以利於模組化。
* 將協定以不可知論：其中的應用程式，不能被特定協定或者實作方式所綁定。

### 將程式碼模組化（Code Modularity）

ONOS 是由多個子專案所組成。每個子專案都有屬於自己的資源樹，也因此，各子專案可藉由自己的資源樹，獨立的進行建置。為了達到此目的，ONOS 整體的資源樹是透過 Maven 以階層方式的 POM 檔建立。每個子專案都擁有自己的 pom.xml 檔，並在父專案的目錄中放置其子專案所公同相依的 pom.xml 檔。後述的做法，為子專案提供與父專案的相依性及共同的設定，也藉此讓子專案可以自行建置。在 ONOS 的根目錄（及最高層）下的 pom.xml 用來建置整個專案，並包含所有需要的模組。

### 可配置（Configurability）

ONOS 使用 Apache Karaf 當它的 OSGi 框架。Karaf 提供在啟動時相依性上的解決方案，並在運行期間提供動態加載模組的功能。除此之外 Karaf 還提供了以下功能：

* 可以使用標準的 JAX-RS API 進行 REST APIs 的開發並確保其安全性。
* 允許客製化配置功能。
* 本地或遠端的 ssh console 都有具備擴展性 CLI（Command Line Interface）。
* 即時 log 級別機制。

### 關係區分（Separation of Concern）

ONOS 被分成以下三個部分：

* Protocol-aware network-facing 模組：直接與網路互動。
* Protocol-agnostic system core：追蹤及提供網路的狀況資訊。
* Applications：消化來自於 core 的資訊，並執行對應動作。

上述的每一個分部都是在 ONOS 層級架構的其中一層。network-facing 透過南向 API 與 core 進行溝通，core 跟 applications 則利用北向 API 進行溝通。南向 API 定義了 protocol-neutral 其用於回報網路狀況給 core。北向 API 則提供抽象化後的網路元件及屬性，以便 application 依獲得的網路狀況，進行對應的反應。

### 將協定以不可知論（Protocol Agnosticism）

當 ONOS 需要支援一個新的協定時，ONOS 在建立一個的對應的 南向 network-facing 模組時，此模組需像一個插件，可直接載入系統中。