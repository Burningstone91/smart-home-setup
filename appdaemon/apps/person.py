"""Define automations for persons."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv

class Person(AppBase):
    """Representation of a Person."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("person"): str,
            vol.Required("attributes"): vol.Schema(
                {
                    vol.Required("full_name"): str,
                    vol.Optional("notifiers"): vol.All(cv.ensure_list, [str]),
                }
            )
        }
    )

    def configure(self) -> None:
        """Configure a person."""
        person = self.args["person"].lower()
        attributes = self.args["attributes"]
        entity_id = f"person.{person}"

        attributes.update(
            {
                "id": person,
                "home": None,
                "non_binary_presence": None,
                "sleep_state": None,
            }
        )

        self.adbase.set_state(entity_id, attributes=attributes)
        