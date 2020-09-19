"""Define automations for areas."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv


class Area(AppBase):
    """Representation of an Area."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("area"): str,
            vol.Optional("attributes"): vol.Schema(
                {vol.Optional("friendly_name"): str}
            ),
            vol.Optional("occupancy"): vol.Schema({vol.Optional(cv.entity_id): str}),
        }
    )

    def configure(self) -> None:
        """Configure an area."""
        areas = self.adbase.get_state("area")
        area = self.args["area"]
        area_id = area.lower().replace(" ", "_")
        attributes = self.args["attributes"]
        self.occupancy_entities = self.args.get("occupancy_entities")
        self.area_entity = f"area.{area_id}"

        # Create an entity for the area if it doesn't already exist
        if self.area_entity not in areas.keys():
            if "friendly_name" not in attributes:
                attributes.update({"friendly_name": area.title()})

            attributes.update(
                {"id": area_id, "persons": [], "occupied": None, "motion": None}
            )

            self.adbase.set_state(self.area_entity, state="idle", attributes=attributes)

        # Listen for no changes in area state for 30 seconds
        self.adbase.listen_state(self.on_state_change, self.area_entity, duration=30)

        # Listen for changes in occupancy entities of area
        if "occupancy_entities" in self.args:
            for entity in self.occupancy_entities.keys():
                self.hass.listen_state(self.on_occupancy_change, entity)

        # Listen for changes in occupancy of area
        self.adbase.listen_state(
            self.on_occupancy_change, self.area_entity, attribute="occupancy"
        )

        # Listen for changes in persons of area
        self.adbase.listen_state(
            self.on_occupancy_change, self.area_entity, attribute="persons"
        )

    def on_state_change(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when area doesn't change state for 30s."""
        # Set area to idle
        self.adbase.set_state(entity, state="idle")

    def on_occupancy_change(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when occupancy factor changes."""
        old = self.adbase.get_state(self.area_entity, attribute="occupied")
        occupied = self.is_occupied(self.area_entity)
        # Set occupancy of area
        if old != occupied:
            self.adbase.set_state(self.area_entity, occupied=occupied)
            self.adbase.log(f"{entity.split('.')[1].capitalize()} Occupied: {occupied}")

    def is_occupied(self, area: str) -> bool:
        """Return True if area is occupied."""
        # Check if motion in area
        motion = self.adbase.get_state(area, attribute="motion")
        # Check if persons in area
        # persons = len(area_attr["persons"]) > 0
        persons = False
        # Check if occupancy devices are "on"
        devices_on = False
        if self.occupancy_entities:
            devices_on = any(
                self.hass.get_state(entity) == state
                for entity, state in self.occupancy_entities.items()
            )
        return persons or motion or devices_on
