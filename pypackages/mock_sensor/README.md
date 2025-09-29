# Mock Sensor with MQTT publishing capabilty

This module fakes data using a random walk with upper and lower bounds.

Use `example_config()` for default settings: a sensor with temperature and humidity readings and an optional MQTT connection. You can use the `run.py` script to set up a sensor with these settings, publishing to `MQTT_HOSTNAME` in `sensor.env`.

Messages are formatted according to the specification in `infra/mqtt/README.md`.

> [!NOTE]
> Use `screen` in `bash` to run the script in a new, detached `screen` session in the background. You can later reattach to this session with `screen -r`.
>
> ```bash
> screen -d -m -s uv run python pypackages/mock_sensor/run.py
> ```

By default, we use anonymous MQTT connections; however, authentication can be set up adding `mqtt_username` and `mqtt_password` values to `sensor.env`.
