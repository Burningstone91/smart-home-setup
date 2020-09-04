"""Define automations for lighting."""
from color import color_temperature_to_rgb, color_temperature_kelvin_to_mired
from enum import Enum
from itertools import chain
from typing import Union, Tuple
import math
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv


class AreaLighting(AppBase):
    """Define a class for Area Lighting."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("area"): str,
            vol.Required("motion_sensors"): cv.entity_ids,
            vol.Optional("delay_off", default=600): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=3600)
            ),
            vol.Optional("lights"): cv.entity_ids,
            vol.Optional("lights_ct"): cv.entity_ids,
            vol.Optional("lights_rgb"): cv.entity_ids,
            vol.Optional("default_brightness", default=80): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("lux_sensor"): cv.entity_id,
            vol.Optional("lux_threshold", default=100): vol.Coerce(int),
            vol.Optional("sleep_lights"): cv.entity_ids,
            vol.Optional("sleep_lights_ct"): cv.entity_ids,
            vol.Optional("sleep_brightness"): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("circadian_sensor"): cv.entity_id,
            vol.Optional("min_brightness", default=1): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("max_brightness", default=100): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("min_colortemp", default=2500): vol.All(
                vol.Coerce(int), vol.Range(min=1000, max=12000)
            ),
            vol.Optional("max_colortemp", default=5500): vol.All(
                vol.Coerce(int), vol.Range(min=1000, max=12000)
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
        self.lights = self.args.get("lights")
        self.lights_ct = self.args.get("lights_ct")
        self.lights_rgb = self.args.get("lights_rgb")
        self.default_brightness = self.args.get("default_brightness")
        self.lux_sensor = self.args.get("lux_sensor")
        self.lux_threshold = self.args.get("lux_threshold")
        self.sleep_lights = self.args.get("sleep_lights")
        self.sleep_lights_ct = self.args.get("sleep_lights_ct")
        self.sleep_brightness = self.args.get("sleep_brightness")
        self.circadian_sensor = self.args.get("circadian_sensor")
        self.min_brightness = self.args.get("min_brightness")
        self.max_brightness = self.args.get("max_brightness")
        self.min_colortemp = self.args.get("min_colortemp")
        self.max_colortemp = self.args.get("max_colortemp")
        self.transition = self.args.get("transition")
        self.update_interval = self.args.get("update_interval")

        # Build area entity and get friendly name
        self.area_entity = f"area.{self.area_id}"
        self.area_name = self.adbase.get_state(
            self.area_entity, attribute="friendly_name"
        )

        # Create a list of all lights in the area
        lights = [
            self.lights,
            self.lights_ct,
            self.lights_rgb,
            self.sleep_lights,
            self.sleep_lights_ct,
        ]
        lights = [light for light in lights if light]
        self.all_lights = set(chain(*lights))

        # Listen for motion detected
        for sensor in self.motion_sensors:
            self.hass.listen_state(self.on_motion, sensor, new="on")

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
        self.adbase.log(f"Motion detected: {self.area_name}")
        # Turn lights on if not already on
        if not self.lights_on():
            self.turn_lights_on()

        # Set motion state of room to True
        self.set_area_motion(True)

        # Start/Restart timer to turn motion state to False
        self.restart_motion_timer()

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
                if "motion_timer" in self.handles:
                    self.adbase.cancel_timer(self.handles["motion_timer"])
                    self.handles.pop("motion_timer")
                if "circadian_timer" in self.handles:
                    self.adbase.cancel_timer(self.handles["circadian_timer"])
                    self.handles.pop("circadian_timer")

    def on_occupancy_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when occupancy of area changed to False."""
        for light in self.all_lights:
            self.hass.turn_off(light)

    def turn_lights_on(self, *args: list, **kwargs: dict) -> None:
        """Turn on lights."""
        if not self.lux_above_threshold():
            if self.is_sleep():
                lights = self.sleep_lights if self.sleep_lights else self.lights
                lights_ct = (
                    self.sleep_lights_ct if self.sleep_lights_ct else self.lights_ct
                )
            else:
                lights = self.lights
                lights_ct = self.lights_ct
                lights_rgb = self.lights_rgb

            brightness_pct = int(self.calc_brightness_pct())
            colortemp = int(self.calc_colortemp(brightness_pct))
            mired = color_temperature_kelvin_to_mired(colortemp)
            rgb = (
                tuple(map(int, self.calc_rgb(colortemp)))
                if self.lights_rgb is not None
                else None
            )

            transition = args[0]["transition"] if args else 0

            if lights is not None:
                for light in lights:
                    self.hass.turn_on(
                        light, brightness_pct=brightness_pct, transition=transition
                    )
            if lights_ct is not None:
                for light in lights_ct:
                    self.hass.turn_on(
                        light,
                        brightness_pct=brightness_pct,
                        color_temp=mired,
                        transition=transition,
                    )
            if lights_rgb is not None:
                for light in lights_rgb:
                    self.hass.turn_on(
                        light,
                        brightness_pct=brightness_pct,
                        color_temp=mired,
                        rgb_color=rgb,
                        transition=transition,
                    )

    def set_area_motion(self, motion: bool) -> None:
        """Set motion of area."""
        occupancy = self.adbase.get_state(self.area_entity, attribute="occupancy")
        occupancy["motion"] = motion
        self.adbase.set_state(self.area_entity, occupancy=occupancy)

    def restart_motion_timer(self) -> None:
        """Set/Reset timer to set occupany of are to False."""
        if "motion_timer" in self.handles:
            self.adbase.cancel_timer(self.handles["motion_timer"])
            self.handles.pop("motion_timer")
        self.handles["motion_timer"] = self.adbase.run_in(
            self.disable_area_motion, self.delay_off
        )

    def disable_area_motion(self, *args: list) -> None:
        """Set area motion to False."""
        self.set_area_motion(False)

    def calc_brightness_pct(self) -> float:
        """Calculate brightness percentage."""
        if self.is_sleep() and self.sleep_brightness:
            return self.sleep_brightness
        else:
            if self.circadian_sensor:
                brightness_pct = self.hass.get_state(self.circadian_sensor)
                if float(brightness_pct) > 0:
                    return self.max_brightness
                else:
                    return (
                        (self.max_brightness - self.min_brightness)
                        * ((100 + float(brightness_pct)) / 100)
                    ) + self.min_brightness
            else:
                return self.default_brightness

    def calc_colortemp(self, brightness_pct: float) -> float:
        if brightness_pct > 0:
            return (
                (self.max_colortemp - self.min_colortemp) * (brightness_pct / 100)
            ) + self.min_colortemp
        else:
            return self.min_colortemp

    def calc_rgb(self, colortemp: int) -> list:
        return color_temperature_to_rgb(colortemp)

    def lux_above_threshold(self) -> bool:
        """Return true if lux is above threshold."""
        if self.lux_sensor:
            value = float(self.hass.get_state(self.lux_sensor))
            return value > self.lux_threshold
        else:
            return False

    def lights_on(self) -> list:
        """Return lights currently on."""
        return [
            entity for entity in self.all_lights if self.hass.get_state(entity) == "on"
        ]

    def is_sleep(self) -> bool:
        """Return true if someone is asleep."""
        sleep_state = self.adbase.get_state(self.area_entity, attribute="sleep_state")
        return sleep_state != "nobody_in_bed"

