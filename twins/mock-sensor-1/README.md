# Mock temperature and humidity sensor

This sensor uses a bounded random walk to generate temperature and humidity values and publishes them to an MQTT broker, signing payloads with HMAC.  Payloads are in the format:

```text
<digest> ts <val> ts_ns <val> temperature <val> humidity <val>
```
