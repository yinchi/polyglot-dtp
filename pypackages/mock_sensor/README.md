# Mock Sensor with MQTT publishing capabilty

This module fakes data using a random walk with upper and lower bounds.

By default, we use anonymous MQTT connections; however, authentication can be set up using `sensors.env` (currently blank).

Use `example_config()` for default settings: a sensor with temperature and humidity readings and an optional (boolean `mqtt` parameter) MQTT connection using the default server (localhost:1883).
