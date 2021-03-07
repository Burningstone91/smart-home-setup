"Config flow for Mopidy." ""
import re
import logging
from typing import Optional

from mopidyapi import MopidyAPI
import voluptuous as vol
from requests.exceptions import ConnectionError as reConnectionError

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST, CONF_ID, CONF_NAME, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers.typing import DiscoveryInfoType
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_NAME, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)


def _validate_input(host, port):
    """Validate the user input."""
    client = MopidyAPI( host=host, port=port, use_websocket=False )
    t = client.rpc_call("core.get_version")
    return True

class MopidyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Mopidy Servers."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize flow"""
        self._host: Optional[str] = None
        self._port: Optional[int] = None
        self._name: Optional[str] = None
        self._uuid: Optional[str] = None

    @callback
    def _async_get_entry(self):
        return self.async_create_entry(
            title=self._name,
            data={
                CONF_NAME: self._name,
                CONF_HOST: self._host,
                CONF_PORT: self._port,
                CONF_ID: self._uuid,
            },
        )

    async def _set_uid_and_abort(self):
        await self.async_set_unique_id(self._uuid)
        self._abort_if_unique_id_configured(
            updates={
                CONF_HOST: self._host,
                CONF_PORT: self._port,
                CONF_NAME: self._name,
            }
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._port = user_input[CONF_PORT]
            self._name = user_input[CONF_NAME]
            self._uuid = re.sub(r"[.-]+", "_", self._host)+"_"+str(self._port)

            try:
                await self.hass.async_add_executor_job(_validate_input, self._host, self._port)
            except reConnectionError as error:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if not errors:
                await self._set_uid_and_abort()
                return self._async_get_entry()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): cv.string,
                    vol.Required(CONF_HOST): cv.string,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.positive_int,
                }
            ),
            errors=errors,
        )
