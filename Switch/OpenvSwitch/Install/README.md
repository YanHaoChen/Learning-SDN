# Install Open vSwitch

雖然在 Mininet 中所模擬出來的 Switch 就包含了 Open vSwitch，但為了要清楚瞭解 Open vSwitch 的運作方式，所以利用 Vargant 建一個獨立的 Ubuntu 環境，並利用```apt-get```安裝 Open vSwitch，進行 Open vSwitch 的測試與學習。

### Vagrant

一套可以快速建立虛擬系統環境的軟體。操作方便，且可以直接取用與虛擬機同目錄下的檔案，也容易搬移。另外，使用虛擬環境還有一個很重要的原因，可以將測試環境與自己電腦的環境切開，讓自己的電腦乾乾淨淨的（還有很多好處，這裡不再贅述）。因此當做學習新工具，將 Open vSwitch 建立在 Vagrant 所管理的虛擬環境上。以下將會簡單介紹如何使用。

####  安裝

Vagrant 的官方很貼心，就直接照著官方的指示安裝即可。以下為官方連結：
[INSTALLING VAGRANT](https://www.vagrantup.com/docs/installation/)

#### 建立一個虛擬機

接下來的動作，只要透過下指令就可以完成。首先，建立一個資料夾，來當做此虛擬機的工作環境：

```bash
$ mkdir sdn
```

進入```sdn```，並加入虛擬機```ubuntu/trusty64```：

```bash
$ cd sdn
$ vagant init ubuntu/trusty64
```

執行完後，現在就可以把機器打開了：

```bash
$ vagrant up
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'ubuntu/trusty64'...
==> default: Matching MAC address for NAT networking...
==> default: Checking if box 'ubuntu/trusty64' is up to date...
...
```

接下來就可以與虛擬接連接，並進行操作。只需要在工作目錄下鍵入：

```bash
$ vagrant ssh
Welcome to Ubuntu 14.04.4 LTS (GNU/Linux 3.13.0-91-generic x86_64)

 * Documentation:  https://help.ubuntu.com/

  System information as of Fri Aug 19 06:17:16 UTC 2016
...
```

離開虛擬主機：

```bash
$ exit
```

關閉虛擬主機：

```bash
$ vagrant halt
==> default: Attempting graceful shutdown of VM...
```

以上，是 Vargant 的基本教學，接下來進入正題，安裝 Open vSwitch。

### 安裝 Open vSwitch

接下來，直接在剛剛建立的虛擬環境中安裝 Open vSwitch。在 Ubuntu 的環境下，安裝 Open vSwitch 並不困難。方法如下，首先更新資源庫：

```bash
$ sudo apt-get update
```

接下來直接安裝即可：

```bash
$ sudo apt-get install openvswitch-switch
```

