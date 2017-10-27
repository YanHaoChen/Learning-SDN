# Step 3：下達規則（Flow）

如果先寫過 Ryu 的 App，再換來寫 ONOS 的 App 一開始一定會不太習慣。很多 OpenFlow 用到的名詞在 ONOS 出現時，卻是另一種名稱，還有編寫的邏輯上也有一段落差。以下將會利用一個簡單的範例（[ForwordingProject.java](https://github.com/OSE-Lab/Learning-SDN/tree/master/Controller/ONOS/step3/ForwordingProject.java)），介紹如果使用 ONOS App 下達 OpenFlow 規則。

## 架構

在此會需要的區塊有：

* `activate`
* `processor`
* `flood`
* `installRule`
* `packetOut`
* `deactivate`

透過以上區塊，就可以達到下達規則的目的。

```shell
//init
activate -> 註冊封包處理程序（processor）

//process
封包送至 Controller -> process -> flood 或者 installRule
```

### activate

```java
@Activate
protected void activate() {
        appId = coreService.registerApplication("org.sean.app");

        packetService.addProcessor(processor, PacketProcessor.director(2));
        TrafficSelector.Builder selector = DefaultTrafficSelector.builder();
        selector.matchEthType(Ethernet.TYPE_IPV4).matchEthType(Ethernet.TYPE_ARP);

        packetService.requestPackets(selector.build(), PacketPriority.REACTIVE, appId);

        log.info("Started");
}
```
首先，註冊這個 App 並取得 appId。appId 是全域變數，之後操作上會使用到。接下來，註冊處理區段，並加上條件__只收 Ethernet Type 為 ARP 或 IPV4 的封包__。在此加上的條件，其實就會轉成 Flow 下達至管理的 Switch 中，其 Flow 如下：

Match|Priority|Action|
---|---|---
Ethernet_Type=ARP|REACTIVE(5)|Output=Controller
Ethernet_Type=IPV4|REACTIVE(5)|Output=Controller

### processor

```java
private class ReactivePacketProcessor implements PacketProcessor {

    @Override
    public void process(PacketContext context) {
        // Stop processing if the packet has been handled, since we
        // can't do any more to it.
        if (context.isHandled()) {
            return;
        }
        InboundPacket pkt = context.inPacket();
        Ethernet ethPkt = pkt.parsed();

        if (ethPkt == null) {
            return;
        }

        HostId srcId = HostId.hostId(ethPkt.getSourceMAC());
        HostId dstId = HostId.hostId(ethPkt.getDestinationMAC());

        // Do we know who this is for? If not, flood and bail.
        Host dst = hostService.getHost(dstId);
        if (dst == null || ethPkt.getEtherType() == Ethernet.TYPE_ARP) {
            flood(context);
            return;
        }
        installRule(context, srcId, dstId);
    }
}
```

此處主要是負責將封包解析，如是 ARP 封包，則進行 Flood。不是的話（也就是一般 IPV4 的封包），則寫入對應規則。

### installRule

```java
private void installRule(PacketContext context, HostId srcId, HostId dstId){
    Ethernet inPkt = context.inPacket().parsed();
    TrafficSelector.Builder selectorBuilder = DefaultTrafficSelector.builder();
    Host dst = hostService.getHost(dstId);
    Host src = hostService.getHost(srcId);
    if(src == null || dst == null){
            return;
    }else{
        selectorBuilder.matchEthSrc(inPkt.getSourceMAC())
                    .matchEthDst(inPkt.getDestinationMAC());

        TrafficTreatment treatment = DefaultTrafficTreatment.builder()
                    .setOutput(dst.location().port())
                    .build();

        ForwardingObjective forwardingObjective = DefaultForwardingObjective.builder()
                    .withSelector(selectorBuilder.build())
                    .withTreatment(treatment)
                    .withPriority(10)
                    .withFlag(ForwardingObjective.Flag.VERSATILE)
                    .fromApp(appId)
                    .makeTemporary(10) //timeout
                    .add();

        flowObjectiveService.forward(context.inPacket().receivedFrom().deviceId(), forwardingObjective);

        packetOut(context, PortNumber.TABLE);
    }
}
```

其中 ONOS 的規則名詞對應如下：

ONOS|OpenFlow
---|---
TrafficSelector|Match
TrafficTreatment|Action

在這個階段，透過 hostService 檢驗 src 跟 dst 主機是否都存在於此拓樸中。如果是，則建立對應的`TrafficSelector`及`TrafficTreatment`，並透過`flowObjectiveService`下達規則。此處的 packetOut 給的 Port Number 為`PortNumber.TABLE`，其目的在於直接將封包交給已建立規則的 Flow Table 進行處理。

> 要使用 HostService 還需要而外開啟 App：`Host Location Provider`。此 App 還會在系統中加入一個預設規則，將 ARP 封包轉入 Controller。所以在一開始設定`processor`要處的封包種類時，可省略 ARP 這項設定。

### deactivate

```java
@Deactivate
protected void deactivate() {
    packetService.removeProcessor(processor);
    processor = null;
    log.info("Stopped");
}
```
在停止此 App 時，將封包處理程序（processor）移除，並將此程序指向`null`。正式結束此 App。
