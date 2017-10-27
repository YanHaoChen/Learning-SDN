# Step 2：使用板模創建第一個 ONOS App

一開始想開發 ONOS App 的人，相信在一開始一定會覺得相當難以入門，因為連程式都還沒開始寫，就有很多參數需要理解、設定。但其實可以透過 Maven 直接創建一個基本的 ONOS App 專案。

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

在運行此指令前，先切換到想放置專案的目錄下。

```shell
mvn archetype:generate -DarchetypeGroupId=org.onosproject -DarchetypeArtifactId=onos-bundle-archetype
```

運行到一半時，會詢問一些關於這個專案的設定（擁有者、名稱...）。依需求填入即可。

```shell
...
Define value for property 'groupId': sean
Define value for property 'artifactId': example-app
Define value for property 'version' 1.0-SNAPSHOT: :
Define value for property 'package' sean: :
Confirm properties configuration:
groupId: sean
artifactId: example-app
version: 1.0-SNAPSHOT
package: sean
 Y: : y
...
```

創建完成後，即可以看到：

```shell
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 39.622 s
[INFO] Finished at: 2017-10-16T10:08:08Z
[INFO] Final Memory: 14M/54M
[INFO] ------------------------------------------------------------------------
```
此時，你的檔案目錄下，就會多一個以`artifactId`命名的資料夾，那就是建立好的專案。

### 調整`pom.xml`檔

雖然專案已經建好了，但專案的敘述及套件的版本都需要稍微修改一下。首開，開啟 `pom.xml` 並修改專案敘述及 ONOS 本版：

```xml
...
<properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <onos.version>1.9.0</onos.version>
        <onos.app.name>org.sean.app</onos.app.name>
        <onos.app.title>example app</onos.app.title>
        <onos.app.origin>sean</onos.app.origin>
        <!--
        <onos.app.category>default</onos.app.category>
        <onos.app.url>http://onosproject.org</onos.app.url>
        <onos.app.readme>ONOS OSGi bundle archetype.</onos.app.readme>
        -->
    </properties>
...

```

> 使用的 ONOS API 版本，會隨著版本的設定而更改哦！ 

### 讓 App 說：Hello!

接下來，進入程式碼的部分。開啟`你的專案/src/main/java/設定的 package name/AppComponent.java`：

```java
...
public class AppComponent {

    private final Logger log = LoggerFactory.getLogger(getClass());

    @Activate
    protected void activate() {
        log.info("Started");
    }

    @Deactivate
    protected void deactivate() {
        log.info("Stopped");
    }

}
```

其中你會看到一些不熟習的敘述像是：

* @Activate
* @Deactivate

這些是屬於 OSGI 的敘述之一。簡而言之，就是可以用幫助程式模組化的系統。
分別為：

* @Activate：啟用時做什麼？
* @Deactivate：關閉時做什麼？

所以，我們要讓 App 在被啟用時說 Hello，只要加入一行程式碼即可：

```java
    @Activate
    protected void activate() {
        log.info("Started");
        log.info("Hello!");
    }
```

在把 App 編譯成 oar 檔之前，還需要做一件事。就是把關於 test 的程式碼註解起來（`你的專案/src/test/java/設定的 package name/AppComponentTest.java`）：
> 因為並未攥寫測試程式碼，所以如果沒有註解，在編譯時會出錯哦!

```java
...
    public void setUp() {
        //component = new AppComponent();
        //component.activate();

    }

    @After
    public void tearDown() {
        //component.deactivate();
    }

    @Test
    public void basics() {

    }

}
```

### 編譯

接下來就是最後一步，編譯。整個專案透過 Maven 管理，所以在最後的編譯，當然也少不了它。所編譯指令如下：

> 請在專案的目錄下執行

```shell
mvn clean install
```

執行完後，編譯好的 App 就會放在專案目錄的 `target` 資料夾中。現在，就可以透過 GUI 啟動它。流程大概如下：

```
登入 GUI -> 點擊左上角三條橫線 -> 選擇 Applications -> 點擊右邊 + 字號 -> 開啟剛剛建立好的 oar 檔 -> 匯入後，點擊箭頭 Activate app.
``` 

> 如使用 OpenFlow 協定連接 Controller，請啟動 App:`OpenFlow Provider`。

### 查看 Console

咦？我們怎麼知道它有沒有說？

我們剛剛讓它說 Hello 的方式，其實是透過 log，所以我們只要進一步看 log，就可以知道它到底有沒有說了。先登入 Cli 介面：

```shell
$ssh -p 8101 onos@<主機 IP>
```

登入後，看 log 的指令如下：

```shell
onos> log:display
```

此時，你可以在茫茫 log 海中，找到 App 喊出來的 Hello 哦！

```shell
...
2017-10-16 13:45:44,217 | INFO  | -message-handler | AppComponent                     | 175 - sean.example-app - 1.0.0.SNAPSHOT | Started
2017-10-16 13:45:44,217 | INFO  | -message-handler | AppComponent                     | 175 - sean.example-app - 1.0.0.SNAPSHOT | Hello!
...
```
