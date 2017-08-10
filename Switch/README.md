# Switch

## 使用 OpenFlow 的 Switch

在 SDN 的架構中，Switch 是離主機（Host）最近的設備，並包含了 Data Plane 的部分。SDN 中的 Switch 與傳統不同的地方就在於，可以與 Control Plane 進行溝通。透過協定，Switch 可以與 Controller 溝通並依 Controller 要求，將封包配送規則寫入其中的 Data Plane，達成 Switch 在 SDN 中的角色。

* [Open vSwitch](https://github.com/OSE-Lab/Learning-SDN/tree/master/Switch/OpenvSwitch)

## 沒有使用 OpenFlow 的 Switch （沒有 SDN 的架構）

在此介紹一些開源的網路設備專案。因為其中沒有支援 OpenFlow 協定，所以歸納在非 SDN 架構下的 Switch。

* [Cumulus](https://github.com/OSE-Lab/Learning-SDN/tree/master/Switch/Cumulus)
