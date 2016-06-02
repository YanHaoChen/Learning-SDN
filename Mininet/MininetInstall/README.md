# How to install Mininet
將Mininet安裝在ubuntu14.04上，是一件相當簡單的事（曾經想用docker建立，但…相信我…那會是一場意義不大的惡夢），且建議使用Desktop版，因為在模擬時，可能需要開啟多個終端畫面。Mininet的官方提供了三種取得的方式及更新方法。在此是直接使用source安裝，個人認為是最直接的方式：

1. 利用git下載Mininet
```
$ git clone git://github.com/mininet/mininet
```
2. 進入mininet的目錄中，利用tag取的可用版本列表，再選擇想要使用的版本（如果沒有特別需求，要跳過這段也是可以）
```
$ cd mininet
$ git tag  
$ git checkout -b 2.2.1 2.2.1
```
3. 執行安裝（請確認是不是已經在mininet的目錄中。另外，-a的參數是指完整安裝，其他安裝選項，可以參考Mininet官方的說明）
```
$ util/install.sh -a
```
完成後，恭喜你，安裝好了mininet。如果還想確認是否安裝正確你可以執行看看：
```
$ sudo mn
```
執行後，如果你看到：
![running][https://github.com/imac-cloud/SDN-tutorial/Mininet/InstallMininet/images/running.png]
就可以確定是安裝成功的。
