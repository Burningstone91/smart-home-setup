"""Define an automation for updating a device tracker from the state of a sensor."""
from typing import Union

from appbase import AppBase, APP_SCHEMA
from globals import PERSONS

class BleDeviceTrackerUpdater(AppBase):
    """Define a base class for the BLE updater."""

    def configure(self) -> None:
        """Configure."""
        for person, attribute in PERSONS.items():
            presence_sensor = attribute['sensor_room_presence']
            topic = attribute['topic_room_device_tracker']

            # set initial state of device tracker
            if self.hass.get_state(presence_sensor) =="not_home":
                self.update_device_tracker(topic, "not_home")
            else:
                self.update_device_tracker(topic, "home")
            
            # home -> not_home after 5 min no activity
            self.hass.listen_state(
                self.on_presence_change, 
                presence_sensor,
                new="not_home",
                duration=5*60,
                target_state="not_home",
                topic=topic,
            )

            # presence sensor change
            self.hass.listen_state(
                self.on_presence_change, 
                presence_sensor,
                topic=topic,
            )

    def on_presence_change(
        self, entity: Union[str, dict], attribute: str, 
        old: str, new: str, kwargs: dict
    ) -> None:
        """Take action on presence change."""
        if kwargs.get("target_state") == "not_home":
            self.update_device_tracker(kwargs["topic"], "not_home")
        elif new != "not_home":
            self.update_device_tracker(kwargs["topic"], "home")

    def update_device_tracker(self, topic: str, target_state: str) -> None:
        """Update the location of the MQTT device tracker."""
        self.mqtt.mqtt_publish(
            topic,
            target_state,
            namespace="mqtt",
        )
