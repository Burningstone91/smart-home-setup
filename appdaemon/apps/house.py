"""Define automations for the house."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA


class House(AppBase):
    """Representation of a House."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("id"): str,
            vol.Optional("attributes"): vol.Schema(
                {
                    vol.Optional("friendly_name"): str,
                }
            )
        }
    )

    def configure(self) -> None:
        """Configure an area."""
        houses = self.adbase.get_state("house")
        house_id = self.args["id"]
        attributes = self.args.get("attributes")
        entity_id = f"house.{house_id}"

        # Create an entity for the house if it doesn't already exist
        if entity_id not in houses.keys():
            if "friendly_name" not in attributes:
                attributes.update({"friendly_name": area.title()})

            attributes.update(
                {
                    "id": house_id,
                    "persons": [],
                    "occupied": None,
                    "presence_state": None,
                }
            )

            self.adbase.set_state(entity_id, state="idle", attributes=attributes) 

        # Listen for no changes in house state for 30 seconds
        self.adbase.listen_state(
            self.state_changed, entity_id, duration=30
        )

    def state_changed(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when house doesn't change state for 30s."""
        # Set area to idle
        self.adbase.set_state(entity, state="idle")