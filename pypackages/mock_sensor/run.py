"""Create and run a mock sensor.

Generates random metrics in an infinite loop.  Use Ctrl-C to stop the test.
Data is written to stdout. Optionally, we also publish to MQTT broker (configured in `sensor.env`).
"""

import logging

import yaml
from dotenv import find_dotenv
from mock_sensor.config import SensorConfig
from mock_sensor.sensor import AuthSettings, MockSensor

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

auth_settings = AuthSettings(_env_file=find_dotenv("sensor.env", raise_error_if_not_found=True))

# Load the sensor configuration from a YAML file
with open("example.sensor.yaml", "r") as f:
    obj = yaml.safe_load(f)
    config = SensorConfig.model_validate(obj)

sensor = MockSensor(config, auth_settings)
sensor.run()
