# Example MQTT subscriber

This package demonstrates subscribing to MQTT messages from [test.mosquitto.org](https://test.mosquitto.org), parsing and pretty-printing messages to stdout in an infinite loop.

> [!WARNING]
> Ideally, we will change our example to a private MQTT broker that we control, to ensure this example does not break in the future.

Currently, we have subscribed to some German weather stations (topic `de/nrw/+/wetter/temperature`), thus we use the `babel` package for float parsing.
