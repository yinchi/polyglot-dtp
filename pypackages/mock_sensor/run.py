"""Create and run a mock sensor.

Generates random metrics in an infinite loop.  Use Ctrl-C to stop the test.
Data is written to stdout. Optionally, we also publish to MQTT broker (configured in `sensor.env`).
"""

import logging
import pathlib

import click
import yaml
from mock_sensor.config import SensorConfig
from mock_sensor.sensor import AuthSettings, MockSensor

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

CONTEXT_SETTINGS = {"help_option_names": ["--help", "-h"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--config-path",
    "-c",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=pathlib.Path),
    required=True,
    help="Path to the sensor config file (YAML format).",
)
@click.option(
    "--env-path",
    "-e",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=pathlib.Path),
    required=False,
    help="Path to the MQTT config file (dotenv format).",
)
def run(config_path: pathlib.Path, env_path: pathlib.Path) -> None:
    """Run the mock sensor."""
    # Print the paths we are using
    logging.info(f"Using config file: {config_path.resolve()}")
    if env_path:
        logging.info(f"Using env file: {env_path.resolve()}")
    else:
        logging.info("No env file specified, using defaults and environment variables only.")
    logging.info("")

    # Load authentication settings from environment file
    if not env_path:
        auth_settings = AuthSettings()
    else:
        auth_settings = AuthSettings(_env_file=env_path.resolve())

    # Load the sensor configuration from a YAML file
    with open(config_path.resolve(), "r") as f:
        obj = yaml.safe_load(f)
        sensor_config = SensorConfig.model_validate(obj)

    sensor = MockSensor(sensor_config, auth_settings)
    sensor.run()


if __name__ == "__main__":
    run()
