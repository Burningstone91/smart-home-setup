"""Define a generic object which  all apps/automations inherit from."""
import voluptuous as vol

import adbase as ad

from utils import config_validation as cv


APP_SCHEMA = vol.Schema(
    {
        vol.Required("module"): str,
        vol.Required("class"): str,
        vol.Optional("dependencies"): cv.ensure_list,
    },
    extra=vol.ALLOW_EXTRA,
)


class AppBase(ad.ADBase):
    """Define a base automation object."""

    APP_SCHEMA = APP_SCHEMA

    def initialize(self) -> None:
        """Initialize."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")

        # Validate app configuration
        try:
            self.args = self.APP_SCHEMA(self.args)
        except vol.Invalid as err:
            self.adbase.log(f"Invalid configuration: {err}", log="error_log")
            return

        # Define holding place for timers
        self.handles = {}

        # Create a reference to every dependency in the configuration
        for app in self.args.get("dependencies", {}):
            if not getattr(self, app, None):
                setattr(self, app, self.adbase.get_app(app))

        # Run the app configuration if specified
        if hasattr(self, "configure"):
            self.configure()
