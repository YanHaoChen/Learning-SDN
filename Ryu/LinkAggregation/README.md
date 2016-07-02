# Link Aggregation
透過網路聚合的方式，可以擴充單台主機可以使用的網路介面，其他主機雖然是向同一台主機（設定成網路聚合模式的主機）進行溝通，但其實並不一定是由同一個 port 進行。也就是說，網路聚合可以將與主機溝通的其他主機進行分配，並分配到歸此主機管理的任意 port 上。這麼一來，可以有效的提高網路效率，再加上 LACP 通訊協定，當其中一個 port 突然出現問題，無法繼續進行數據傳輸，也會動態的將出問題的 port 上的主機移轉到可運作的 port 上，繼續提供服務，達成高容錯的能力。

> 提高網路效率：如果每個 port 都有 100 Mbps 的網路傳輸速度，那麼在使用兩個 port 的情況下，則總共會有 200 Mbps 的網路傳輸速度。

## 運行

在此，使用 Mininet 進行環境模擬（[MininetEnv.py](https://github.com/imac-cloud/SDN-tutorial/blob/master/Ryu/LinkAggregation/MininetEnv.py)），使用以 Ryu 建立的專案 [SimpleSwitchLACP13](https://github.com/imac-cloud/SDN-tutorial/blob/master/Ryu/LinkAggregation/SimpleSwitchLACP13.py) 進行控制，實現 Link Aggregation 運作。

### MininetEnv.py
建立模擬環境。其中包含 4 台 host、1 台 switch 及 1 台遠端 controller。host1（```h1```）是實現 Link Aggregation 的主機，所以在程式內的編寫有別於其他主機。例如（標題為程式碼行號）：

* ```13```：並未直接設定 Mac Address，待主機（```h1```）設定 Link Aggregation 時，會再進行設定。
* ```18```、```19```：為```h1```與 switch 建立兩個連接 port。

> 在 Ryubook 繁體中文版內的範例程式碼中，因目前 Mininet 的版本與其中的編寫方式有些不同（循環引用及語法錯誤的問題），並無法直接執行。所以此環境建立方式是參考英文版的 Ryubook，並可以成功執行的版本。

### SimpleSwitchLACP13.py
可以說是由 SimpleSwitch13 進行修改。SimpleSwitchLACP13 與 SimpleSwitch 最大的差別，就在於加入 LACP 網路協定：

* lacplib.EventPacketIn：處理 LACP 網路協定中 PacketIn 事件。
* lacplib.EventSlaveStateChanged：處理 LACP 網路協定中 Slave 狀況改變時的事件（如斷線）。
* del_flow：刪除有關於已斷線 port 的 Flow Entry。