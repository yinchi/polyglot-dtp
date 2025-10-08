# IoT network

## Sensing: IoT Sensor &rarr; InfluxDB

IoT devices publish sensor data to the DT platform via one or more MQTT brokers.  These brokers are designed to function as dumb pipes:

1. A sensor publishes to an MQTT broker (`mqtt_broker` in the figure below) using one of its assigned topics.
2. A worker process (`mqtt2influx` in the figure below) subscribes to various topics on the MQTT broker (e.g. `sensors/#` for all sensor topics), processes and validates each message, and writes the processed data to the appropriate table in the InfluxDB database.
3. Worker processes may aggregate time-series data.  For example, raw data collected every 10 seconds might be retained for 1 day, while 5-minute averages (300 seconds or 30 sampling periods) are retained for 1 month.

In the example above, the MQTT broker is only involved in Steps 1 and 2, while the time-series database is involved in Steps 2 and 3.  A network diagram showing the separation of the IoT and main DT platform network is shown as follows:

```kroki-plantuml
@startuml
!theme crt-green
nwdiag {
  intranet [shape = cloud];
  intranet -- reverse_proxy;
  network internal {
      address = "172.17.x.x/16";

      reverse_proxy [address = "172.17.x.254"];
      Collections [shape = collections, description="Other DT\nplatform services"]
      mqtt_broker [address = "172.17.x.101"];
      mqtt2influx [address = "172.17.x.102"];
      influxdb [address = "172.17.x.103"] [shape = database ];
  }
  network iot {
      address = "172.16.x.x/16"

      sensor1 [address = "172.16.x.1"];
      sensor2 [address = "172.16.x.2"];
      sensor3 [address = "172.16.x.3"];
      mqtt_broker  [address = "172.16.x.254"];
  }
}
caption IP addresses shown above are arbitrary and shown for example purposes only.
@enduml
```

### MQTT messsage format

MQTT messages should be JSON-encoded. An example message is as follows:

```kroki-plantuml
@startjson
!theme crt-green
{
    "hmac":"FKlepUuqx4dR6VX2fRIuavVvOkwRRUlay8IgM1VSmrQ=",
    "payload": {
        "humidity":60.64,
        "temperature":20.52,
        "ts":1759384453,
        "ts_ns":920529791
    }
}
```

- The timestamp is split between second and nanosecond portions to ensure both portions fit within a 32-bit signed integer (until 2038).  In Python, we use:

    ```py
    from time import time_ns
    ts, ts_ns = divmod(time_ns(), 1_000_000_000)
    payload = {"ts": ts, "ts_ns": ts_ns} | payload  # both original and new `payload` are dicts
    ```

- The HMAC digest is created using SHA-256.  This is provided using [`hmac.digest()`](https://docs.python.org/3/library/hmac.html#hmac.digest) in Python.
- When encoding payloads as strings to compute the HMAC digest, be sure to sort all dict keys and remove all unnecessary whitespace.  In Python, use:

    ```py
    CANONICAL_JSON = {
        "indent": None,
        "separators": (",", ":"),
        "sort_keys": True,
    }

    payload_str = json.dumps(payload, **CANONICAL_JSON)
    ```

  This is necessary to ensure a one-to-one mapping between a JSON object and its HMAC digest.

!!! note
    HMAC only authenticates the sender and does not provide encryption.  However, we can use WPA2's built-in encryption for secure wireless transmission of MQTT packets.

    🚧 **TODO**: handle MQTT over SSL for cases where extra security is needed (e.g. remote sensors connecting via public internet)

### MQTT keep-alive and client takeover

To prevent wasted resources by the MQTT broker due to zombie connections:

- Each MQTT client should define a keep-alive duration.  For sensors this should be several times the sensing interval.
- Each MQTT client should set a unique Client ID.  Thus, when the client attempts to reconnect after a broken connection, the broker identifies the client as a returning one and clears any outdated session data associated with that client.

For more details, see this [HiveMQ article](https://www.hivemq.com/blog/mqtt-essentials-part-10-alive-client-take-over/).

### InfluxDB data ingestion

A worker thread subscribes to a set of topics on the MQTT broker (e.g. `#`) and writes to an InfluxDB table.  An **IoT registry** maps MQTT topics to a specific InfluxDB table and tag combination.  The worker thus:

1. Validates incoming MQTT messages using HMAC.
2. Checks that the MQTT topic is registered and that the payload matches the expected data format.
3. Writes the payload data into the correct InfluxDB table, based on the registry.

The IoT registry should also specify the retention period of raw data.  **If data aggregation is enabled**, the IoT registry should also specify an aggregation policy (mean/median/min/max/sum over a given period), and a retention period for the aggregated data.

!!! warning
    Setting the retention period for all time-series data is crucial for ensuring the InfluxDB data volume never becomes full.  Periodic (cron) jobs may be set up to back up time-series data to secondary storage.

## 🚧 Actuation: Digital Twin &rarr; IOT device (TODO)

IoT devices may also subscribe to MQTT messages from the DT platform.  These should also match the format above (signed JSON payload with timestamps).

## Actions, alarms, and QoS

Whereas sensor data is generally non-critical (if a sensor reading is lost, just wait for the next one), some messages have higher importance: for example, a missed alarm could result in injury.  For this reason, we will generally use:

- QoS 0 for sensor data
- QoS 1 for alarms (if multiple copies received, continue the state of alarm)
- QoS 2 for actions (device should perform action **exactly once**, thus requiring the highest MQTT QoS level)

To maintain a log of alarms and actions, we will record these in InfluxDB in a similar manner to sensor data. (🚧 **TODO**: define the IoT registry schema for tracking sensor data, alarms, and actions.)
