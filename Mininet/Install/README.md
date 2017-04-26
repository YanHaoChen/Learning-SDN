# How to Install Mininet
將 Mininet 安裝在 ubuntu14.04 上，是一件相當簡單的事，且建議使用 Desktop 版，因為在模擬時，可能需要開啟多個終端畫面。Mininet 的官方提供了三種取得的方式及更新方法。在此是直接使用 source 安裝，個人認為是最直接的方式：

1. 利用 git 下載 Mininet
```shell
$ git clone git://github.com/mininet/mininet
```
2. 進入 mininet 的目錄中，利用 tag 取的可用版本列表，再選擇想要使用的版本（如果沒有特別需求，要跳過這段也是可以）
```shell
$ cd mininet
$ git tag  
$ git checkout -b 2.2.1 2.2.1
```
3. 執行安裝（請確認是不是已經在 Mininet 的目錄中。另外，```-a```的參數是指完整安裝，其他安裝選項，可以參考 Mininet 官方的說明）
```shell
$ util/install.sh -a
```
完成後，恭喜你，安裝好了 Mininet。如果還想確認是否安裝正確你可以執行看看：
```shell
$ sudo mn
```
執行後，如果你看到：
![running](https://github.com/imac-cloud/SDN-tutorial/blob/master/Mininet/Install/images/running.png?raw=true)
就可以確定是安裝成功的。
