# Step 2：使用板模創建第一個 ONOS App

一開始想開發 ONOS App 的人，相信在一開始一定會覺得相當難以入門，因為連程式都還沒開始寫，就有很多參數需要理解、設定（例如：`pom.xml`）。但其實可以透過 Maven 直接創建一個基本的 ONOS App 專案。

### Install Maven

Maven 是一個專門管理 Java 專案的套件。透過專案中的 `pom.xml` 檔，即可定義整個專案的生命週期、架構及加入所需的 Package。另外，還可以透過 Maven 提供的指令，進一步控制、管理。

#### For Ubuntu

```shell
$ sudo apt-get update
$ sudo apt-get install maven
```
#### For OS X

```shell
$ brew install maven
```

### 使用 Maven 創建板模

```shell
mvn archetype:generate -DarchetypeGroupId=org.onosproject -DarchetypeArtifactId=onos-bundle-archetype
```
