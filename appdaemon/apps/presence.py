"""Define an automation for updating a device tracker from the state of a sensor."""
from enum import Enum
from typing import Union

from appbase import AppBase, APP_SCHEMA
from globals import PERSONS, HOUSE


class BleDeviceTrackerUpdater(AppBase):
    """Define a base class for the BLE updater."""

    def configure(self) -> None:
        """Configure."""
        for person, attribute in PERSONS.items():
            room_presence_sensor = attribute["sensor_room_presence"]
            topic = attribute["topic_room_device_tracker"]

            # set initial state of device tracker
            if self.hass.get_state(room_presence_sensor) == "not_home":
                self.update_device_tracker(topic, "not_home")
            else:
                self.update_device_tracker(topic, "home")

            # home -> not_home after 3 min no activity
            self.hass.listen_state(
                self.on_presence_change,
                room_presence_sensor,
                new="not_home",
                duration=3 * 60,
                target_state="not_home",
                topic=topic,
            )

            # room presence sensor change
            self.hass.listen_state(
                self.on_presence_change, room_presence_sensor, topic=topic
            )

    def on_presence_change(
        self, entity: Union[str, dict], attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Take action on presence change."""
        if kwargs.get("target_state") == "not_home":
            self.update_device_tracker(kwargs["topic"], "not_home")
        elif new != "not_home":
            self.update_device_tracker(kwargs["topic"], "home")

    def update_device_tracker(self, topic: str, target_state: str) -> None:
        """Update the location of the MQTT device tracker."""
        self.mqtt.mqtt_publish(topic, target_state, namespace="mqtt")


class NonBinaryPresence(AppBase):
    """Define a base class for Non Binary Presence."""

    class PresenceStates(Enum):
        """Define an enum for person related presence states."""

        home = "zu Hause"
        just_arrived = "gerade angekommen"
        just_left = "gerade gegangen"
        away = "weg"
        extended_away = "lange weg"

    class HouseStates(Enum):
        """Define an enum for house related presence states."""

        someone = "Jemand ist zu Hause"
        everyone = "Alle sind zu Hause"
        noone = "Niemand ist zu Hause"
        vacation = "Ferien"

    def configure(self) -> None:
        """Configure."""
        # set initial state for the house
        self.update_house_presence_state()

        for person, attribute in PERSONS.items():
            input_select = attribute["input_select_non_binary_state"]
            person_sensor = attribute["person"]

            # away/extended away -> just arrived
            self.hass.listen_state(
                self.on_presence_change,
                person_sensor,
                new="home",
                person=person,
                input_select=input_select,
                non_binary_state=self.PresenceStates.just_arrived.value,
            )

            # home -> just left
            self.hass.listen_state(
                self.on_presence_change,
                person_sensor,
                old="home",
                person=person,
                input_select=input_select,
                non_binary_state=self.PresenceStates.just_left.value,
            )

            # just arrived -> home, after 5 min
            self.hass.listen_state(
                self.on_presence_change,
                input_select,
                new=self.PresenceStates.just_arrived.value,
                duration=5 * 60,
                person=person,
                input_select=input_select,
                non_binary_state=self.PresenceStates.home.value,
            )

            # just left -> away, after 5 min
            self.hass.listen_state(
                self.on_presence_change,
                input_select,
                new=self.PresenceStates.just_left.value,
                duration=5 * 60,
                person=person,
                input_select=input_select,
                non_binary_state=self.PresenceStates.away.value,
            )

            # away -> extended away, after 24 hours
            self.hass.listen_state(
                self.on_presence_change,
                input_select,
                new=self.PresenceStates.away.value,
                duration=24 * 60 * 60,
                person=person,
                input_select=input_select,
                non_binary_state=self.PresenceStates.extended_away.value,
            )

    def on_presence_change(
        self, entity: Union[str, dict], attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Take action on person's presence change."""
        input_select = kwargs["input_select"]
        old_state = self.hass.get_state(input_select)
        target_state = kwargs["non_binary_state"]

        # just left -> just arrived = home
        if (old_state == self.PresenceStates.just_left.value) and (
            target_state == self.PresenceStates.just_arrived.value
        ):
            target_state = self.PresenceStates.home.value

        # set person non-binary presence state
        if old_state != target_state:
            self.hass.select_option(input_select, target_state)
            self.adbase.log(
                f"{kwargs['person']} war {old_state}, ist jetzt {target_state}"
            )

        # set house non-binary presence state
        self.update_house_presence_state()

    def update_house_presence_state(self) -> None:
        """Update the presence state of the house."""
        old_state = self.house_presence_state
        if self.everyone_home:
            new_state = self.HouseStates.everyone.value
        elif self.everyone_extended_away:
            new_state = self.HouseStates.vacation.value
        elif self.noone_home:
            new_state = self.HouseStates.noone.value
        else:
            new_state = self.HouseStates.someone.value

        if old_state != new_state:
            self.hass.select_option(HOUSE["input_select_presence"], new_state)
            self.adbase.log(f"Vorher: {old_state}, Jetzt: {new_state}")

    def whos_in_state(self, *presence_states: Enum) -> list:
        """Return list of person in given state."""
        presence_state_list = [
            presence_state.value for presence_state in presence_states
        ]
        return [
            person
            for person, attribute in PERSONS.items()
            if self.hass.get_state(attribute["input_select_non_binary_state"])
            in presence_state_list
        ]

    @property
    def whos_just_arrived(self) -> bool:
        """Return true if everyone is *home*."""
        return self.whos_in_state(self.PresenceStates.just_arrived)

    @property
    def whos_home(self) -> list:
        """Return list of persons *home*."""
        return self.whos_in_state(
            self.PresenceStates.home, self.PresenceStates.just_arrived
        )

    @property
    def everyone_home(self) -> bool:
        """Return true if everyone is *home*."""
        return self.whos_home == list(PERSONS.keys())

    @property
    def someone_home(self) -> bool:
        """Return true if someone is *home*."""
        return len(self.whos_home) != 0

    @property
    def noone_home(self) -> bool:
        """Return true if no one is *home*."""
        return not self.whos_home

    @property
    def everyone_extended_away(self) -> bool:
        """Return true if everyone is *extended away*."""
        return self.whos_in_state(self.PresenceStates.extended_away) == list(
            PERSONS.keys()
        )

    @property
    def house_presence_state(self) -> str:
        """Return current state of the house presence."""
        return self.hass.get_state(HOUSE["input_select_presence"])
