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
            vol.Optional("occupancy"): vol.Schema(
                {vol.Optional(cv.entity_id): str}
            ),
        }
    )

    def configure(self) -> None:
        """Configure an area."""
        areas = self.adbase.get_state("area")
        area = self.args["area"]
        area_id = area.lower().replace(" ", "_")
        attributes = self.args["attributes"]
        self.area_entity = f"area.{area_id}"

        # Create an entity for the area if it doesn't already exist
        if self.area_entity not in areas.keys():
            if "friendly_name" not in attributes:
                attributes.update({"friendly_name": area.title()})

            attributes.update(
                {"id": area_id, "persons": [], "occupied": None, "occupancy": {}}
            )

            self.adbase.set_state(self.area_entity, state="idle", attributes=attributes)

        # Listen for no changes in area state for 30 seconds
        self.adbase.listen_state(self.on_state_change, self.area_entity, duration=30)

        # Listen for changes in occupancy entities of area
        if "occupancy_entities" in self.args:
            occupancy_entities = self.args.get("occupancy_entities")
            for entity, state in occupancy_entities.items():
                self.hass.listen_state(
                    self.on_occupancy_entity_change,
                    entity,
                    occupied_state=state,
                )

        # Listen for changes in occupancy of area
        self.adbase.listen_state(
            self.on_occupancy_change, self.area_entity, attribute="occupancy"
        )

        # Listen for changes in persons in area
        self.adbase.listen_state(
            self.on_occupancy_change, self.area_entity, attribute="persons"
        )

    def on_state_change(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when area doesn't change state for 30s."""
        # Set area to idle
        self.adbase.set_state(entity, state="idle")

    def on_occupancy_entity_change(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None: 
        """Respond when occupancy factor changes."""
        occupied_state = kwargs["occupied_state"]
        # Determine occupancy state of entity
        occupancy = self.adbase.get_state(self.area_entity, attribute="occupancy")
        if new == occupied_state:
            occupancy[entity] = True
        else:
            occupancy[entity] = False
        
        # Set state of occupancy entity
        self.adbase.set_state(self.area_entity, occupancy=occupancy)
        
    def on_occupancy_change(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when occupancy factor changes."""
        occupied = self.is_occupied(entity)
        # Set occupancy of area
        self.adbase.set_state(entity, occupied=occupied)
        self.adbase.log(f"{entity.split('.')[1].capitalize()} Occupied: {occupied}")

    def is_occupied(self, area: str) -> bool:
        """Return occupancy of given area."""
        """Return True if area is occupied."""
        # Get state of occupancy entities
        area_attr = self.adbase.get_state(area, attribute="attributes")
        occupancy = area_attr["occupancy"]
        # Check if persons in area
        persons = len(area_attr["persons"]) > 0
        return persons or any(value == True for key, value in occupancy.items())

