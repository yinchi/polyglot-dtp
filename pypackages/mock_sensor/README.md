# Mock Sensor with MQTT publishing capabilty

This module fakes data using a random walk with upper and lower bounds.

1. Using the provided `example.sensor.yaml` in the link above, create your sensor configuration.
2. Create `mqtt.env` to hold your MQTT configuration.  An example is as follows:

    ```properties
    # leave blank to disable MQTT
    MQTT_HOSTNAME=mosquitto
    MQTT_PORT=1883
    MQTT_HMAC_KEY=example-mqtt-signing-key
    ```

   MQTT messages are signed with [HMAC](https://docs.python.org/3/library/hmac.html) using SHA-256 and the key above. An example message is:

    ```json
    {"hmac":"FKlepUuqx4dR6VX2fRIuavVvOkwRRUlay8IgM1VSmrQ=","payload":{"humidity":60.64,"temperature":20.52,"ts":1759384453,"ts_ns":920529791}}
    ```

3. In your Docker Compose file, mount your sensor config file to `/app/sensor.yaml` and load in your environment variables using `env_file`.

To see the full set of availble configuration settings, refer to `config.py` in the `src/mock_sensor` directory.
