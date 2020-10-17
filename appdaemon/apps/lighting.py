"""Define automations for lighting."""
from itertools import chain
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv


class AreaLighting(AppBase):
    """Define a class for Area Lighting."""

    # pylint: disable=too-many-instance-attributes

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("area"): str,
            vol.Required("motion_sensors"): cv.entity_ids,
            vol.Optional("delay_off", default=600): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=3600)
            ),
            vol.Optional("lux_sensor"): cv.entity_id,
            vol.Optional("lux_threshold", default=100): vol.Coerce(int),
            vol.Required("lights"): cv.entity_ids,
            vol.Optional("sleep_lights"): cv.entity_ids,
            vol.Optional("circadian_sensor"): cv.entity_id,
            vol.Optional("default_brightness", default=80): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("sleep_brightness"): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("min_brightness", default=1): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("max_brightness", default=100): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("transition", default=60): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=3600)
            ),
            vol.Optional("update_interval", default=300): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=3600)
            ),
        }
    )

    def configure(self) -> None:
        """Configure."""
        self.area_id = self.args["area"]
        self.motion_sensors = self.args["motion_sensors"]
        self.delay_off = self.args.get("delay_off")
        self.lux_sensor = self.args.get("lux_sensor")
        self.lux_threshold = self.args.get("lux_threshold")
        self.lights = self.args["lights"]
        self.sleep_lights = self.args.get("sleep_lights")
        self.circadian_sensor = self.args.get("circadian_sensor")
        self.default_brightness = self.args.get("default_brightness")
        self.sleep_brightness = self.args.get("sleep_brightness")
        self.min_brightness = self.args.get("min_brightness")
        self.max_brightness = self.args.get("max_brightness")
        self.transition = self.args.get("transition")
        self.update_interval = self.args.get("update_interval")

        # Build area entity and get friendly name
        self.area_entity = f"area.{self.area_id}"
        self.area_name = self.adbase.get_state(
            self.area_entity, attribute="friendly_name"
        )

        # Create a list of all lights in the area
        lights = [self.lights, self.sleep_lights]
        lights = [light for light in lights if light]
        self.all_lights = set(chain(*lights))

        # Listen for motion detected
        for sensor in self.motion_sensors:
            self.hass.listen_state(self.on_motion, sensor)

        # Listen for changes in light state
        if self.circadian_sensor:
            for light in self.all_lights:
                self.hass.listen_state(self.on_light_change, light)

        # Listen for occupancy changes of area
        self.adbase.listen_state(
            self.on_occupancy_change, self.area_entity, attribute="occupied", new=False
        )

    def on_motion(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when motion is detected."""
        if new == "on":
            # Cancel existing timers
            if "motion_timer" in self.handles:
                self.adbase.cancel_timer(self.handles["motion_timer"])
                self.handles.pop("motion_timer")
            # Turn lights on if not already on
            if not self.lights_on():
                self.turn_lights_on()
            # Set area motion to True
            self.adbase.set_state(self.area_entity, motion=True)
            self.adbase.log(f"Motion Detected: {self.area_name}")
        elif new == "off":
            # Start timer to set area motion to False
            self.handles["motion_timer"] = self.adbase.run_in(
                self.disable_area_motion, self.delay_off
            )

    def on_occupancy_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when occupancy of area changed to False."""
        for light in self.all_lights:
            self.hass.turn_off(light)

    def on_light_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when light changes state."""
        if new != old:
            if new == "on":
                if "circadian_timer" in self.handles:
                    self.adbase.cancel_timer(self.handles["circadian_timer"])
                    self.handles.pop("circadian_timer")
                self.handles["circadian_timer"] = self.adbase.run_every(
                    self.turn_lights_on,
                    f"now+{self.update_interval}",
                    self.update_interval,
                    transition=self.transition,
                )
            elif new == "off":
                if "circadian_timer" in self.handles:
                    self.adbase.cancel_timer(self.handles["circadian_timer"])
                    self.handles.pop("circadian_timer")

    def lights_on(self) -> list:
        """Return lights currently on."""
        return [
            entity for entity in self.all_lights if self.hass.get_state(entity) == "on"
        ]

    def disable_area_motion(self, *args: list) -> None:
        """Set area motion to False."""
        self.adbase.set_state(self.area_entity, motion=False)
        self.adbase.log(f"No More Motion: {self.area_name}")

    def turn_lights_on(self, *args: list, **kwargs: dict) -> None:
        """Turn on lights."""
        if not self.lux_above_threshold():
            if self.is_sleep() and self.sleep_brightness:
                lights = self.sleep_lights if self.sleep_lights else self.lights
            else:
                lights = self.lights

            brightness_pct = int(self.calc_brightness_pct())
            color_temp = int(
                self.hass.get_state(self.circadian_sensor, attribute="colortemp")
            )
            color = self.hass.get_state(self.circadian_sensor, attribute="rgb_color")
            transition = args[0]["transition"] if args else 1

            for light in lights:
                if self.supports_color(light):
                    self.hass.turn_on(
                        light,
                        brightness_pct=brightness_pct,
                        rgb_color=color,
                        transition=transition,
                    )
                elif self.supports_color_temp(light):
                    self.hass.turn_on(
                        light,
                        brightness_pct=brightness_pct,
                        color_temp=color_temp,
                        transition=transition,
                    )
                elif self.supports_brightness(light):
                    self.hass.turn_on(
                        light, brightness_pct=brightness_pct, transition=transition
                    )
                else:
                    self.hass.turn_on(light)

    def lux_above_threshold(self) -> bool:
        """Return true if lux is above threshold."""
        if self.lux_sensor:
            value = self.hass.get_state(self.lux_sensor)
            if value not in ["unavailable", "unknown"]:
                return float(value) > self.lux_threshold

        return False

    def calc_brightness_pct(self) -> float:
        """Calculate brightness percentage."""
        if self.is_sleep() and self.sleep_brightness:
            return self.sleep_brightness

        if self.circadian_sensor:
            brightness_pct = self.hass.get_state(self.circadian_sensor)
            if float(brightness_pct) > 0:
                return self.max_brightness

            return (
                (self.max_brightness - self.min_brightness)
                * ((100 + float(brightness_pct)) / 100)
            ) + self.min_brightness

        return self.default_brightness

    def supports_color(self, entity: str) -> bool:
        """Return True if light supports color."""
        supported_features = self.hass.get_state(entity, "supported_features")
        return supported_features & 16 == 16

    def supports_color_temp(self, entity: str) -> bool:
        """Return True if light supports color temperature."""
        supported_features = self.hass.get_state(entity, "supported_features")
        return supported_features & 2 == 2

    def supports_brightness(self, entity: str) -> bool:
        """Return True if light supports brightness."""
        supported_features = self.hass.get_state(entity, "supported_features")
        return supported_features & 1 == 1

    def is_sleep(self) -> bool:
        """Return True if someone is asleep."""
        sleep_state = self.adbase.get_state(self.area_entity, attribute="sleep_state")
        return sleep_state != "nobody_in_bed"
