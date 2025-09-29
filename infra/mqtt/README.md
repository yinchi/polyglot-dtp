# MQTT broker

This sets up an Eclipse Mosquitto instance and a message forwarder.  Note that:

- Messages are unencrypted; the broker is set up to listen on the default 1883 port only
- Anonymous messages are allowed.

## Expected message format:

> [!NOTE]
> TODO: update `mock_sensor` module to match this specification.

An example MQTT message is:

```text
Tv54zB5V1RqlLto36KaJStWhtGVNlcfMd2ITNCR3Phg= ts 1759114961 ts_ns 671685824 temperature 10.0 humidity 20.0
```

- The first token is the signature for the payload (the rest of the message).  We use [HMAC](https://docs.python.org/3/library/hmac.html) with SHA256 to sign our messages.
- The timestamp is split into second and nanosecond parts so as not to overflow any 32-bit integer representations.  In Python, use:
  ```py
  from time import time_ns
  ts, ts_ns = divmod(time_ns(), 1_000_000_000)
  ```

### Example message generation code:

```py
import hmac
from binascii import b2a_base64 as b2a

KEY = b'mqtt-message-signing-key'
payload = b'ts 1759114961 ts_ns 671685824 temperature 10.0 humidity 20.0'
msg = f"{b2a(hmac.digest(KEY, payload, 'sha256'), newline=False).decode()} {payload.decode()}"
print(msg)
```

### Example message validation code:

```py
rx_digest, rx_payload = msg.split(" ",1)
expected_digest = b2a(hmac.digest(KEY, rx_payload.encode(), 'sha256'), newline=False).decode()
assert expected_digest == rx_digest, "HMAC digests do not match."
print(rx_payload)
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
