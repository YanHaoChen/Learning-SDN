# How to Connect Pica8 P-3297 with Console Port and Set the Environment

藉由操作實體機（Pica8 P-3297），實際感受 SDN 的運作及操作方式。以下將介紹使用 Console Port 連接 Pica8 P-3297 及運作模式設定。方法如下：

## 使用 Console Port 與連結虛擬機（ubuntu14.04）連接

如要透過 Console Port 將虛擬機與 Pica8 P-3297 相連，首先 VirtualBox 上就要做些設定。設定如下：
 
### 開啟連接埠
![開啟連接埠](https://github.com/imac-cloud/SDN-tutorial/blob/master/Pica8-P-3297/ConnectAndSetEnvironment/images/%E9%96%8B%E5%95%9F%E4%B8%B2%E6%8E%A5%E5%9F%A0.png?raw=true)

### 選擇連接設備
![選擇連接設備](https://github.com/imac-cloud/SDN-tutorial/blob/master/Pica8-P-3297/ConnectAndSetEnvironment/images/%E9%81%B8%E6%93%87%E9%80%A3%E6%8E%A5%E8%A8%AD%E5%82%99.png?raw=true)

### 安裝 GtkTerm
GtkTerm 是一個讓我們可以與周邊硬體設備連接的套件，Pica8 P-3297 官方文件雖然有提出其他套件（U-Boot），但 GtkTerm 的使用方式較直覺，所以在此使用它與 Pica8 P-3297 連接。

```shell
//雖然非必要，但還是建議先更新一下
sudo apt-get update
//安裝GtkTerm
sudo apt-get install GtkTerm
```

### 啟動 GtkTerm
```shell
//記得要加上sudo，不然會因為權限不足，無法正常執行
sudo gtkterm
```

### 設定連結參數
執行```sudo gtkterm```後，將會開啟一個視窗，在視窗上方點選 Configuration->Port，選擇好連接埠即可配置連線的參數。與 Pica8 P-3297 的連線參數如下：

* baud rate:115200
* data bits:8
* stop bits:1

![設定連結參數](https://github.com/imac-cloud/SDN-tutorial/blob/master/Pica8-P-3297/ConnectAndSetEnvironment/images/%E8%A8%AD%E5%AE%9A%E9%80%A3%E7%B5%90%E5%8F%83%E6%95%B8.png?raw=true)

### 開始連線
設定完參數，回到原本視窗，此時按下 enter ，就會出現以下畫面：

```shell
XopPlus login:
```

成功登入後，就可以看到：

```shell
admin@XorPlus$
```
現在已經跟 Pica8 P-3297 成功連結囉！
> 如在預設狀態下，可以透過輸入預設的帳號（admin）密碼（pica8）登入，並在登入後，修改密碼。

## 運作模式設定（設定成 OVS 模式）

Pica8 P-3297，有兩種模式可以提供選擇，分別為 L2/L3 及 Open vSwitch 兩種。為了設定為我們所需要的模式（Open vSwitch），我們可以輸入```sudo picos_boot```進行設定，輸入後，就會顯示以下畫面：

```shell
Please configure the default system start-up options:
 (Press other key if no change)
    [1] PicOS L2/L3    * default
    [2] PicOS Open vSwitch/OpenFlow
    [3] No start-up options
Enter your choice (1,2,3):
```
此時，我們選擇2，也就是 Open vSwitch 模式。接下來，會要求你輸入固定的 IP 及網路遮罩，輸入完後，還會要求你輸入預設閘道。這些都設定好後，就可以重新啟動（執行 service picos restart），執行設定。

> 請將對外的網路線，插入 Management Port。固定的IP其實指的就是這條對外網路的 IP，遮罩、預設閘道也需要照此網路的規定設定。

重新登入後，看到：

```shell
admin@PicOS-OVS$
```

就代表成功設定了！此時可以輸入 ifconfig，觀看目前 Pica8 P-3297 的網路狀況，並可以發現 en0 顯示的 IP，就是設定的固定 IP。
> 現在也可以透過 ssh 進入 Pica8 P-3297 囉！
