"""Create and run a mock sensor.

Generates random metrics in an infinite loop.  Use Ctrl-C to stop the test.
Data is written to stdout. Optionally, we also publish to MQTT broker.

TODO: add MQTT publishing, fix module to match the specification change in README.md.
"""

import logging

from dotenv import find_dotenv
from mock_sensor.config import example_config
from mock_sensor.sensor import AuthSettings, MockSensor

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

auth_settings = AuthSettings(_env_file=find_dotenv("sensor.env", raise_error_if_not_found=True))

config = example_config("test_sensor", mqtt=False)
sensor = MockSensor(config, auth_settings)

sensor.run()
