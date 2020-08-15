"""Define automations for circadian based lighting combined with lux sensors."""
from typing import Union
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA

# light: entity_id
# light_type: dimmer | color_temp | hs_color | xy_color | rgb_color
# lux_sensor:

class CircadianLightAutomation(AppBase):  # pylint: disable=too-many-instance-attributes
    """Define a base feature for lux based lighting."""

    def configure(self) -> None:
        """Configure."""
        self.circadian_sensor = self.args.get("circadian_sensor")
        self.lux_sensor = self.args.get("lux_sensor")
        self.max_bri_pct = self.args.get["max_brightness_pct"]
        self.min_color_temp = self.args.get["min_color_temp"]
        self.max_color_temp = self.args.get["max_color_temp"]
        self.update_interval = self.args.get["update_interval"]
        self.transition = self.args.get["transition"]
        
        self.hass.listen_state(
            self.on_light_change, self.motion_sensor, new="on", constrain_app_enabled=1
        )

    def on_light_change(
        self, entity: Union[str, dict], attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Start timer to adjust brightness at the given interval."""

        self.handles[entity] = self.adbase.run_in(self.xxxxx, self.update_interval, light=entity))

    def update_light(self, kwargs: dict) -> None:
        """Update the brightness, color temperature and RGB color."""
                if entity in self.handles:
            self.cancel_timer(self.handles[entity])
            self.handles.pop(entity)

    def calc_brightness_pct(self, lux: int) -> float:
        """Calculate brighness percentage based on lux level and circadian sensor."""
        if self.lux_sensor:
            pct_covered_by_lux = 100 - ((14000 - lux) / 140)
        else:
            pct_covered_by_lux = 0

        if self.circadian_sensor:
            pct_required_by_circadian = self.hass.get_state(self.circadian_sensor)
        else:
            pct_required_by_circadian = self.max_bri_pct

        brightness_pct = max(pct_covered_by_lux, 0)
        return max(brightness_pct - pct_covered_by_lux,0)

    def calc_color_temperature(self, bri_pct: float, max_temp: int, min_temp: int) -> float:
        """Calculate color temperature from brightness percentage."""
        return ((max_temp - min_temp) * (bri_pct / 100)) + min_temp

