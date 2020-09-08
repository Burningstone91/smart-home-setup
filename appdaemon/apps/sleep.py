"""Define automations for Sleeping."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv


class Sleep(AppBase):
    """Defina a class for Sleep automations."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("house_id"): str,
            vol.Required("sensors"): vol.Schema({vol.Optional(str): cv.entity_id}),
        }
    )

    def configure(self) -> None:
        """Configure."""
        bed_sensors = self.args["sensors"]
        self.house_entity = f"house.{self.args['house_id']}"

        # Set initial sleep state
        self.update_house_state()

        for person, sensor in bed_sensors.items():
            person_entity = f"person.{person}"
            # bed not occupied -> occupied
            self.hass.listen_state(
                self.on_sensor_change,
                sensor,
                new="on",
                person=person_entity,
                target_state="just_laid_down",
            )
            # bed occupied -> not occupied
            self.hass.listen_state(
                self.on_sensor_change,
                sensor,
                new="off",
                person=person_entity,
                target_state="just_got_up",
            )
            # just got up -> just laid down = back_to_bed
            self.adbase.listen_state(
                self.on_person_change,
                person_entity,
                attribute="sleep_state",
                old="just_got_up",
                new="just_laid_down",
                target_state="back_to_bed",
            )
            # just laid down -> sleeping, after 5 min
            self.adbase.listen_state(
                self.on_person_change,
                person_entity,
                attribute="sleep_state",
                new="just_laid_down",
                duration=5 * 60,
                target_state="sleeping",
            )
            # back to bed -> sleeping, after 5 min
            self.adbase.listen_state(
                self.on_person_change,
                person_entity,
                attribute="sleep_state",
                new="back_to_bed",
                duration=5 * 60,
                target_state="sleeping",
            )
            # just got up -> awake, after 5 min
            self.adbase.listen_state(
                self.on_person_change,
                person_entity,
                attribute="sleep_state",
                new="just_got_up",
                duration=5 * 60,
                target_state="awake",
            )
            # Listen to changes in persons' sleep state
            self.adbase.listen_state(
                self.on_person_change_house, person_entity, attribute="sleep_state"
            )

    def on_sensor_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when bed occupancy sensor changes state."""
        if new != old:
            # Set sleep state for person
            person = kwargs["person"]
            old_state = self.adbase.get_state(person, attribute="sleep_state")
            target_state = kwargs["target_state"]

            if old_state == "just_got_up" and target_state == "just_laid_down":
                target_state = "back_to_bed"

            self.adbase.set_state(person, sleep_state=target_state)
            self.adbase.log(
                f"{person.split('.')[1].capitalize()}: {target_state.replace('_',' ')}"
            )

    def on_person_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when person changes sleep state."""
        if new != old:
            # Set sleep state for person
            target_state = kwargs["target_state"]
            self.adbase.set_state(entity, sleep_state=target_state)
            self.adbase.log(
                f"{entity.split('.')[1].capitalize()}: {target_state.replace('_',' ')}"
            )

    def on_person_change_house(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Update the sleep state of the house."""
        self.update_house_state()

    def update_house_state(self) -> None:
        """Update the sleep state of the house."""
        persons_home = self.adbase.get_state(self.house_entity, attribute="persons")
        old_state = self.adbase.get_state(self.house_entity, attribute="sleep_state")
        if not self.persons_in_bed():
            target_state = "nobody_in_bed"
        elif set(persons_home) == set(self.persons_in_bed()):
            target_state = "everyone_in_bed"
        else:
            target_state = "someone_in_bed"
          
        if old_state != target_state:
            self.adbase.set_state(self.house_entity, sleep_state=target_state)
            self.adbase.log(f"House Sleep State: {target_state.replace('_', ' ')}")

    def who_in_state(self, *states) -> list:
        """Return list of persons in given states."""
        persons = self.adbase.get_state("person")
        return [
            attributes["attributes"]["id"]
            for attributes in persons.values()
            if attributes["attributes"]["sleep_state"] in states
        ]

    def persons_in_bed(self) -> list:
        """Return list of persons in bed."""
        return self.who_in_state(
            "just_got_up" "just_laid_down", "back_to_bed", "sleeping"
        )
