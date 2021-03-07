"""The mopidy component."""
from mopidyapi import MopidyAPI
import logging
from requests.exceptions import ConnectionError as reConnectionError
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.const import CONF_HOST, CONF_ID, CONF_NAME, CONF_PORT

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the mopidy component."""
    return True

def _test_connection(host, port):
    client = MopidyAPI(
        host=host, port=port, use_websocket=False
    )
    i = client.rpc_call("core.get_version")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the mopidy from a config entry."""
    try:
        r = await hass.async_add_executor_job(_test_connection, entry.data[CONF_HOST], entry.data[CONF_PORT])

    except reConnectionError as error:
        raise ConfigEntryNotReady from error

    hass.data.setdefault(DOMAIN, {})

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, MEDIA_PLAYER_DOMAIN)
    )

    return True
