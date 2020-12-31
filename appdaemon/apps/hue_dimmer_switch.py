"""Define automations for switches/remote controls."""
from appdaemon.plugins.hass.hassapi import Hass

class SwitchBase(Hass)):
    """Define a base class for switches."""

    def initialize(self) -> None:
        """Initialize."""
        switch_id = self.args["switch_id"]
        self.lights = self.args.get("lights")
        self.transition_time = self.args.get("transition_time", 50)
        self.custom_action_map = self.args.get("custom_button_config", {})
        self.action_map = {}
        self.button_map = {}

        # Check if lights are deconz lights
        self.check_deconz_light()

        # Listen for button presses
        self.listen_event(self.on_button_press, "deconz_event", id=switch_id)

    def on_button_press(self, event_name: str, data: dict, kwargs: dict) -> None:
        """Respond on button press."""
        button_name = self.get_button_name(data["event"])
        # Get button configuration
        if self.lights:
            action_map = {**self.action_map, **self.custom_action_map}
        else:
            action_map = {**self.custom_action_map}

        # Check if button press is configured
        try:
            service_data = action_map[button_name]
        except KeyError:
            return

        # Execute light services
        if isinstance(service_data, str):
            light_service = getattr(SwitchBase, service_data)
            light_service(self)
            self.log(
                f"Switch executed {service_data} for {', '.join(self.lights)}"
            )
            return

        # Execute custom button presses
        delay = service_data.get("delay")
        if delay:
            self.run_in(
                self.action_delayed, delay, service_data=service_data
            )
        else:
            self.action(service_data)

    def check_deconz_light(self) -> bool:
        """Raise error when configured lights are not deconz lights."""
        if self.lights:
            if any(
                self.get_state(light, attribute="is_deconz_group") is None
                for light in self.lights
            ):
                raise ValueError(
                    "Only DeCONZ lights can be used with the light configuration"
                )

    def get_button_name(self, button_code) -> str:
        """Get the human friendly name of the button press."""
        try:
            return self.button_map[button_code]
        except KeyError:
            return None

    def get_light_type(self, light: str) -> str:
        """Get the DeCONZ light type of the given light."""
        if self.get_state(light, attribute="is_deconz_group"):
            return "/action"
        return "/state"

    def action(self, service_data) -> None:
        """Execute service."""
        service = service_data["service"].replace(".", "/")
        entity = service_data.get("entity_id")
        data = service_data.get("data", {})
        self.call_service(service, entity_id=entity, **data)
        self.log(f"Switch executed {service} for {', '.join(entity)}")

    def action_delayed(self, kwargs: dict) -> None:
        """Execute service delayed."""
        self.action(kwargs["service_data"])

    def light_on(self) -> None:
        """Turn lights on."""
        for light in self.lights:
            self.turn_on(light)

    def light_on_full(self) -> None:
        """Turn on light at full brightness."""
        for light in self.lights:
            self.call_service("light/turn_on", entity_id=light, brightness_pct=100)

    def light_off(self) -> None:
        """Turn lights off."""
        for light in self.lights:
            self.turn_off(light)

    def light_toggle(self) -> None:
        """Toggle lights."""
        for light in self.lights:
            self.toggle(light)

    def light_dim_up_step(self) -> None:
        """Increase brightness by 10%."""
        for light in self.lights:
            self.call_service(
                "light/turn_on", entity_id=light, brightness_step_pct=10
            )

    def light_dim_up_hold(self) -> None:
        """Smoothly increase brightness."""
        for light in self.lights:
            self.call_service(
                "deconz/configure",
                field=self.get_light_type(light),
                entity=light,
                data={"bri_inc": 254, "transitiontime": self.transition_time},
            )

    def light_dim_down_step(self) -> None:
        """Decrease brightness by 10%."""
        for light in self.lights:
            self.call_service(
                "light/turn_on", entity_id=light, brightness_step_pct=-10
            )

    def light_dim_down_hold(self) -> None:
        """Smoothly decrease brightness."""
        for light in self.lights:
            self.call_service(
                "deconz/configure",
                field=self.get_light_type(light),
                entity=light,
                data={"bri_inc": -254, "transitiontime": self.transition_time},
            )

    def light_stop_dim(self) -> None:
        """Stop dimming."""
        for light in self.lights:
            self.call_service(
                "deconz/configure",
                field=self.get_light_type(light),
                entity=light,
                data={"bri_inc": 0},
            )


class HueDimmerSwitch(SwitchBase):
    """Define a base feature for Philips Hue Dimmer Switche."""

    def initialize(self) -> None:
        """Configure."""
        super().initialize()
        self.button_map = {
            1000: "short_press_turn_on",
            1002: "short_release_turn_on",
            1001: "long_press_turn_on",
            1003: "long_release_turn_on",
            2000: "short_press_dim_up",
            2002: "short_release_dim_up",
            2001: "long_press_dim_up",
            2003: "long_release_dim_up",
            3000: "short_press_dim_down",
            3002: "short_release_dim_down",
            3001: "long_press_dim_down",
            3003: "long_release_dim_down",
            4000: "short_press_turn_off",
            4002: "short_release_turn_off",
            4001: "long_press_turn_off",
            4003: "long_release_turn_off",
        }

        self.action_map = {
            "short_release_turn_on": "light_on",
            "long_press_turn_on": "light_on_full",
            "short_release_dim_up": "light_dim_up_step",
            "long_press_dim_up": "light_dim_up_hold",
            "long_release_dim_up": "light_stop_dim",
            "short_release_dim_down": "light_dim_down_step",
            "long_press_dim_down": "light_dim_down_hold",
            "long_release_dim_down": "light_stop_dim",
            "short_release_turn_off": "light_off",
        }


class XiaomiWXKG01LM(SwitchBase):
    """Define a base feature for Xiaomi Mi Round Wireless Switch."""

    def initialize(self) -> None:
        """Configure."""
        super().initialize()
        self.button_map = {
            1000: "short_press",
            1002: "short_release",
            1001: "long_press",
            1003: "long_press_release",
            1004: "double_press",
            1005: "triple_press",
            1006: "quadruple_press",
            1010: "many_press",
        }

        self.action_map = {
            "short_release": "light_toggle",
            "double_press": "light_on_full",
            "long_press": "light_dim_up_hold",
            "long_press_release": "light_stop_dim",
        }


class XiaomiWXKG11LM2016(SwitchBase):
    """Define a base feature for Xiaomi Aqara Wireless Switch 2016 version."""

    def initialize(self) -> None:
        """Configure."""
        super().initialize()
        self.button_map = {
            1002: "short_press",
            1004: "double_press",
            1005: "triple_press",
            1006: "quadruple_press",
        }

        self.action_map = {
            "short_press": "light_toggle",
            "double_press": "light_on_full",
        }


class IKEATradfriE1743(SwitchBase):
    """Define a base feature for IKEA Tradfri E1743 Switch."""

    def initialize(self) -> None:
        """Configure."""
        super().initialize()

        self.button_map = {
            1002: "short_release_turn_on",
            1001: "long_press_turn_on",
            1003: "long_release_turn_on",
            2002: "short_release_turn_off",
            2001: "long_press_turn_off",
            2003: "long_release_turn_off",
        }

        self.action_map = {
            "short_release_turn_on": "light_on",
            "long_press_turn_on": "light_dim_up_hold",
            "long_release_turn_on": "light_stop_dim",
            "short_release_turn_off": "light_off",
            "long_press_turn_off": "light_dim_down_hold",
            "long_release_turn_off": "light_stop_dim",
        }


class IKEASymfonisk(SwitchBase):
    """Define a base feature for IKEA Symfonisk Sound Controller."""

    def initialize(self) -> None:
        """Configure."""
        super().initialize()

        self.button_map = {
            1002: "short_press",
            1004: "double_press",
            1005: "triple_press",
            2001: "rotate_right",
            2003: "rotate_right_stop",
            3001: "rotate_left",
            3003: "rotate_left_stop",
        }

        self.action_map = {
            "short_press": "light_toggle",
            "double_press": "light_on_full",
        }
