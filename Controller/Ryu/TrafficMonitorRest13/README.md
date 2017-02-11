# Traffic Monitor with Restful

此專案是 [SimpleSwitchRest13](https://github.com/YanHaoChen/Learning-SDN/tree/master/Controller/Ryu/SimpleSwitchRest13) 及 [TrafficMonitor](https://github.com/YanHaoChen/Learning-SDN/tree/master/Controller/Ryu/TrafficMonitor) 結合在一起的延伸。讓使用者可以透過 Restful 的方式取得 Switch 上，即時的流量統計數據。

## 與設備連接前的準備

* 將要連接的 Bridge 的 protocols 設定為 Openflow 1.3

> 可透過指令```$ ovs-ofctl -O OpenFlow13 dump-flows <Bridge>```進行確認。


## 啟動

```shell
ryu-manager --verbose ./TrafficMonitorRest13.py
```
執行後：

```shell
$ ryu-manager --verbose ./TrafficMonitorRest13.py
loading app ./TrafficMonitorRest13.py
loading app ryu.controller.ofp_handler
creating context wsgi
instantiating app ryu.controller.ofp_handler of OFPHandler
instantiating app ./TrafficMonitorRest13.py of TrafficMonitorRest13
BRICK ofp_event
  PROVIDES EventOFPPacketIn TO {'TrafficMonitorRest13': set(['main'])}
  PROVIDES EventOFPSwitchFeatures TO {'TrafficMonitorRest13': set(['config'])}
  PROVIDES EventOFPPortStatsReply TO {'TrafficMonitorRest13': set(['main'])}
  PROVIDES EventOFPFlowStatsReply TO {'TrafficMonitorRest13': set(['main'])}
  PROVIDES EventOFPStateChange TO {'TrafficMonitorRest13': set(['main', 'dead'])}
  CONSUMES EventOFPEchoReply
  CONSUMES EventOFPSwitchFeatures
  CONSUMES EventOFPPortDescStatsReply
  CONSUMES EventOFPErrorMsg
  CONSUMES EventOFPHello
  CONSUMES EventOFPEchoRequest
BRICK TrafficMonitorRest13
  CONSUMES EventOFPPacketIn
  CONSUMES EventOFPSwitchFeatures
  CONSUMES EventOFPPortStatsReply
  CONSUMES EventOFPFlowStatsReply
  CONSUMES EventOFPStateChange
(1035) wsgi starting up on http://0.0.0.0:8080
connected socket:<eventlet.greenio.base.GreenSocket object at 0x7f878d4182d0> address:('192.168.99.100', 35473)
hello ev <ryu.controller.ofp_event.EventOFPHello object at 0x7f878d418dd0>
move onto config mode
```
其中，可以見到```(1035) wsgi starting up on http://0.0.0.0:8080```。代表已經在 local 端的 8080 port 上開啟服務，Restful 也就是透過這個 port 提供。

## 提供的 API
在此分別提供兩隻 API：

* 取得監控中 Switch 的 Port 的狀況（GET）
* 取得監控中 Switch 的規則狀況（GET）

這兩隻 API 回傳的資料格式皆為```json```。

### 取得監控中 Switch 的 Port 的狀況（GET）
```
http://<server>:8080/trafficmonitor/portstat
```
> 可透過 curl 取得，方法如下：
> ```
> curl -X GET http://<server>:8080/trafficmonitor/portstat
> ```

#### 回傳資料
```json
{
   "OFPPortStatsReply": {
      "body": [
         {
            "OFPPortStats": {
               "collisions": 0,
               "duration_nsec": 869000000,
               "duration_sec": 1187,
               "port_no": 3,
               "rx_bytes": 558,
               "rx_crc_err": 0,
               "rx_dropped": 0,
               "rx_errors": 0,
               "rx_frame_err": 0,
               "rx_over_err": 0,
               "rx_packets": 7,
               "tx_bytes": 0,
               "tx_dropped": 0,
               "tx_errors": 0,
               "tx_packets": 0
            }
         },
         {
            "OFPPortStats": {
               "collisions": 0,
               "duration_nsec": 870000000,
               "duration_sec": 1187,
               "port_no": 1,
               "rx_bytes": 558,
               "rx_crc_err": 0,
               "rx_dropped": 0,
               "rx_errors": 0,
               "rx_frame_err": 0,
               "rx_over_err": 0,
               "rx_packets": 7,
               "tx_bytes": 0,
               "tx_dropped": 0,
               "tx_errors": 0,
               "tx_packets": 0
            }
         },
         {
            "OFPPortStats": {
               "collisions": 0,
               "duration_nsec": 852000000,
               "duration_sec": 1187,
               "port_no": 2,
               "rx_bytes": 558,
               "rx_crc_err": 0,
               "rx_dropped": 0,
               "rx_errors": 0,
               "rx_frame_err": 0,
               "rx_over_err": 0,
               "rx_packets": 7,
               "tx_bytes": 0,
               "tx_dropped": 0,
               "tx_errors": 0,
               "tx_packets": 0
            }
         },
         {
            "OFPPortStats": {
               "collisions": 0,
               "duration_nsec": 852000000,
               "duration_sec": 1187,
               "port_no": 4294967294,
               "rx_bytes": 648,
               "rx_crc_err": 0,
               "rx_dropped": 0,
               "rx_errors": 0,
               "rx_frame_err": 0,
               "rx_over_err": 0,
               "rx_packets": 8,
               "tx_bytes": 0,
               "tx_dropped": 0,
               "tx_errors": 0,
               "tx_packets": 0
            }
         }
      ],
      "flags": 0,
      "type": 4
   }
}
```

### 取得監控中 Switch 的規則狀況（GET）
```
http://<server>:8080/trafficmonitor/flowstat
```
> 可透過 curl 取得，方法如下：
> ```
> curl -X GET http://<server>:8080/trafficmonitor/flowstat
> ```

#### 回傳資料
```json
{
   "OFPFlowStatsReply": {
      "body": [
         {
            "OFPFlowStats": {
               "byte_count": 0,
               "cookie": 0,
               "duration_nsec": 730000000,
               "duration_sec": 1099,
               "flags": 0,
               "hard_timeout": 0,
               "idle_timeout": 0,
               "instructions": [
                  {
                     "OFPInstructionActions": {
                        "actions": [
                           {
                              "OFPActionOutput": {
                                 "len": 16,
                                 "max_len": 65535,
                                 "port": 4294967293,
                                 "type": 0
                              }
                           }
                        ],
                        "len": 24,
                        "type": 4
                     }
                  }
               ],
               "length": 80,
               "match": {
                  "OFPMatch": {
                     "length": 4,
                     "oxm_fields": [],
                     "type": 1
                  }
               },
               "packet_count": 0,
               "priority": 0,
               "table_id": 0
            }
         }
      ],
      "flags": 0,
      "type": 1
   }
}
```
