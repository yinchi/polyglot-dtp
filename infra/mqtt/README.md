# MQTT broker

This sets up an Eclipse Mosquitto instance and a message forwarder.  Note that:

- Messages are unencrypted; the broker is set up to listen on the default 1883 port only
- Anonymous messages are allowed.

## Expected message format:

> [!NOTE]
> TODO: update `mock_sensor` module to match this specification.

An example MQTT message is:

```text
{"hmac":"jT2pFmBVqXDi+mM+r2qH+Jb9BKyk7F4yQi1luw98HRs=","payload":{"humidity":51.84,"temperature":20.11,"ts":1759295542,"ts_ns":72719155}}
```

- The timestamp is split into second and nanosecond parts so as not to overflow any 32-bit integer representations.  In Python, use:
  ```py
  from time import time_ns
  ts, ts_ns = divmod(time_ns(), 1_000_000_000)
  ```
- For the digest, we use [HMAC](https://docs.python.org/3/library/hmac.html) with [SHA256](https://docs.python.org/3/library/hashlib.html#module-hashlib).  Python-based MQTT data sources should use the `hashlib` module from the Python Standard library.
- To ensure functionality of the validation process, payload objects should be JSON-encoded in canonical form with sorted keys and no whitespace:
  ```py
  CANONICAL_JSON = {
    "indent": None,
    "separators": (",", ":"),
    "sort_keys": True,
  }
  ```

## Raspberry Pi setup

>[!WARNING]
> The instructions in this section are untested.

First, follow the appropiate instructions to install the necessary Linux packages for your sensor, such as:

- `sense-hat`: <https://pythonhosted.org/sense-hat/>
- `python3-bme280`: <https://bme280.readthedocs.io/en/latest/>
- `python3-periphery`: <https://github.com/vsergeev/python-periphery/>

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y <packages>
```

Then, install the `paho-mqtt` Python package:

```bash
sudo apt-get install -y python3-paho-mqtt
```
