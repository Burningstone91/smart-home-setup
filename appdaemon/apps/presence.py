"""Define an automation for updating a device tracker from the state of a sensor."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv


class RoomPresence(AppBase):
    """Define a base class for room presence."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {vol.Required("sensors"): vol.Schema({vol.Optional(str): cv.entity_id})}
    )

    def configure(self) -> None:
        """Configure."""
        room_presence_sensors = self.args["sensors"]

        for person, sensor in room_presence_sensors.items():

            # Listen for person changing area
            self.hass.listen_state(
                self.on_sensor_change, sensor, duration=5, person_id=person
            )

    def on_sensor_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when room presence sensor changes state."""
        if new != old:
            person_id = kwargs["person_id"]
            person_entity = f"person.{person_id}"
            areas = self.adbase.get_state("area")
            area_entity = f"area.{new}"

            # Remove person from other areas
            for area in areas.keys():
                if area != area_entity:
                    persons = self.adbase.get_state(area, attribute="persons")
                    if person_id in persons:
                        persons.remove(person_id)
                        self.adbase.set_state(area, persons=persons)

            # Add person to new area
            if new != "not_home":
                persons = self.adbase.get_state(area_entity, attribute="persons")
                if person_id not in persons:
                    persons.append(person_id)
                    self.adbase.set_state(area_entity, persons=persons)

            # Set area for person
            self.adbase.set_state(person_entity, area=new)
            self.adbase.log(f"{person_id.capitalize()} Area: {new}")


class PersonPresence(AppBase):
    """Define a base class for binary person presence."""

    def configure(self) -> None:
        """Configure."""
        persons = self.adbase.get_state("person")

        for person in persons.keys():
            # Listen for person entering the house
            self.adbase.listen_state(
                self.on_person_arrival,
                person,
                attribute="area",
            )

            # area 3 minutes "not_home" -> person left
            self.adbase.listen_state(
                self.on_person_leave,
                person,
                attribute="area",
                new="not_home",
                duration=3 * 60
            )

    def on_person_arrival(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when person enters house."""
        # Set person to "home"
        not_home_states = ["not_home", "undefined", "unknown", None]
        if new != old and old in not_home_states and new not in not_home_states:
            self.adbase.set_state(entity, home=True)
            self.adbase.log(f"{entity.split('.')[1].capitalize()}: home")
            
    def on_person_leave(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when person left house for 3 minutes."""
        # Set person to "not home"
        self.adbase.set_state(entity, home=False)
        self.adbase.log(f"{entity.split('.')[1].capitalize()}: not home")

class NonBinaryPresence(AppBase):
    """Define a base class for non binary person presence."""

    def configure(self) -> None:
        """Configure."""
        persons = self.adbase.get_state("person")

        for person in persons.keys():
            # away/extended away -> just arrived
            self.adbase.listen_state(
                self.on_presence_change,
                person,
                attribute="home",
                new=1,
                non_binary_state="just_arrived",
            )

            # home -> just left
            self.adbase.listen_state(
                self.on_presence_change,
                person,
                attribute="home",
                new=0,
                non_binary_state="just_left",
            )

            # just arrived -> home, after 5 min
            self.adbase.listen_state(
                self.on_presence_change,
                person,
                attribute="non_binary_presence",
                new="just_arrived",
                duration=5 * 60,
                non_binary_state="home",
            )

            # just left -> away, after 5 min
            self.adbase.listen_state(
                self.on_presence_change,
                person,
                attribute="non_binary_presence",
                new="just_left",
                duration=5 * 60,
                non_binary_state="away",
            )

            # away -> extended away, after 24 hours
            self.adbase.listen_state(
                self.on_presence_change,
                person,
                attribute="non_binary_presence",
                new="away",
                duration=24 * 60 * 60,
                non_binary_state="extended_away",
            )

    def on_presence_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when person changes presence state."""
        # just left -> just arrived = home
        if old == "just_left" and new == "just_arrived":
            non_binary_state = "home"
        else:
            non_binary_state = kwargs["non_binary_state"]

        # Set non binary presence state for person
        self.adbase.set_state(entity, non_binary_presence=non_binary_state)
        self.adbase.log(
            f"{entity.split('.')[1].capitalize()}: {non_binary_state.replace('_',' ')}"
        )


class HousePresence(AppBase):
    """Define a base class for house presence."""

    APP_SCHEMA = APP_SCHEMA.extend({vol.Required("house_id"): str})

    def configure(self) -> None:
        """Configure."""
        house_id = self.args["house_id"]
        self.house_entity_id = f"house.{house_id}"
        persons = self.adbase.get_state("person")

        # Listen for person changing home state
        for person in persons.keys():
            self.adbase.listen_state(self.on_presence_change, person, attribute="home")

    def on_presence_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when person changes presence state."""
        person_id = entity.split(".")[1]
        persons = self.adbase.get_state("person")
        
        persons_home = self.adbase.get_state(self.house_entity_id, attribute="persons")
        persons_extended_away = [
            person
            for person, attributes in persons.items()
            if attributes["attributes"]["non_binary_presence"] == "extended_away"
        ]

        # Add/remove person from the house
        if new == True:
            persons_home.append(person_id)
        elif person_id in persons_home:
            persons_home.remove(person_id)

        # Set occupancy of the house
        if not persons_home:
            occupied = False
        else:
            occupied = True

        # Set presence state of the house
        if len(persons.keys()) == len(persons_home):
            presence_state = "everyone_home"
        elif len(persons.keys()) == len(persons_extended_away):
            presence_state = "vacation"
        elif not persons_home:
            presence_state = "nobody_home"
        else:
            presence_state = "someone_home"

        self.adbase.set_state(
            self.house_entity_id,
            presence_state=presence_state,
            occupied=occupied,
            persons=persons_home,
        )
        self.adbase.log(f"House Presence: {presence_state.replace('_',' ')}")
