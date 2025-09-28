"""Example MQTT subscriber.

Here we subscribe to a topic that provides temperature data for various
locations in North Rhine-Westphalia (NRW), Germany.  The topic structure is:
  de/nrw/<location>/wetter/temperature
where <location> is a placeholder for the actual location name.
"""

from datetime import datetime
from time import time

import paho.mqtt.client as mqtt
import pytz
from babel.numbers import parse_decimal
from paho.mqtt.packettypes import PacketTypes

TOPIC = "de/nrw/+/wetter/temperature"
TIMEZONE = "Europe/Berlin"
timezone = pytz.timezone(TIMEZONE)


def on_connect(client: mqtt.Client, _, _2, reason_code: mqtt.ReasonCode, _3):
    """Callback for when the client receives a CONNACK response from the server."""
    assert reason_code == mqtt.ReasonCode(PacketTypes.CONNACK, identifier=0), (
        f"Connection failed with reason code {reason_code}"
    )
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(TOPIC)


def on_message(_, _2, msg: mqtt.MQTTMessage):
    """Callback for when a PUBLISH message is received from the server.

    Since the messages are German-formatted numbers (e.g., "21,5"), we use
    babel.numbers.parse_decimal to correctly parse them.  Also, since there is
    no timestamp in the MQTT message, we use the time of receipt as the timestamp.
    """
    rx_timestamp = time()
    topic = msg.topic
    payload = msg.payload.decode("utf-8")

    # Use Berlin timezone for timestamp
    timestamp = datetime.fromtimestamp(rx_timestamp, timezone).isoformat()

    # Extract location from topic
    location = topic.split("/")[2]

    # Parse the temperature using German locale
    temp = float(parse_decimal(payload, locale="de_DE"))

    # Print the received data
    print(f"{timestamp}    {location:<8}{temp:.1f} °C")


def on_disconnect(client: mqtt.Client, _, _2, reason_code: mqtt.ReasonCode, _3):
    """Callback for when the client disconnects from the broker."""
    if reason_code != mqtt.ReasonCode(PacketTypes.DISCONNECT, identifier=0):
        print(f"Unexpected disconnection. Reason code: {reason_code}")
    else:
        print("Disconnected successfully.")


def main() -> None:
    """Main function to run the MQTT subscriber."""
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    print("Connecting to broker...")
    mqtt_client.connect("test.mosquitto.org", 1883, 60)
    print("Connected. Listening for messages...")

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("Disconnecting from broker...")
        mqtt_client.disconnect()
    print("Exited.")
