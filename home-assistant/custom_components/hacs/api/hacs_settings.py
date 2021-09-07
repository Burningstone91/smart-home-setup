"""API Handler for hacs_settings"""
from homeassistant.components import websocket_api
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from custom_components.hacs.share import get_hacs
from custom_components.hacs.utils.logger import getLogger

_LOGGER = getLogger()


@websocket_api.async_response
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacs/settings",
        vol.Optional("action"): cv.string,
        vol.Optional("categories"): cv.ensure_list,
    }
)
async def hacs_settings(hass, connection, msg):
    """Handle get media player cover command."""
    hacs = get_hacs()

    action = msg["action"]
    _LOGGER.debug("WS action '%s'", action)

    if action == "set_fe_grid":
        hacs.configuration.frontend_mode = "Grid"

    elif action == "onboarding_done":
        hacs.configuration.onboarding_done = True

    elif action == "set_fe_table":
        hacs.configuration.frontend_mode = "Table"

    elif action == "set_fe_compact_true":
        hacs.configuration.frontend_compact = False

    elif action == "set_fe_compact_false":
        hacs.configuration.frontend_compact = True

    elif action == "clear_new":
        for repo in hacs.repositories:
            if repo.data.new and repo.data.category in msg.get("categories", []):
                _LOGGER.debug(
                    "Clearing new flag from '%s'",
                    repo.data.full_name,
                )
                repo.data.new = False
    else:
        _LOGGER.error("WS action '%s' is not valid", action)
    hass.bus.async_fire("hacs/config", {})
    await hacs.data.async_write()
    connection.send_message(websocket_api.result_message(msg["id"], {}))
