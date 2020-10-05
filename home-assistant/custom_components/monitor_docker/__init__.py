"""Monitor Docker main component."""

import asyncio
import logging
import threading
import voluptuous as vol

from datetime import timedelta

import homeassistant.helpers.config_validation as cv

from .helpers import DockerAPI

from homeassistant.const import (
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_URL,
)

from .const import (
    API,
    CONF_CERTPATH,
    CONF_CONTAINERS,
    CONF_RENAME,
    CONF_SENSORNAME,
    CONF_SWITCHENABLED,
    CONF_SWITCHNAME,
    CONFIG,
    CONTAINER_INFO_ALLINONE,
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_SENSORNAME,
    DEFAULT_SWITCHNAME,
    MONITORED_CONDITIONS_LIST,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(seconds=10)

DOCKER_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_URL, default=None): vol.Any(cv.string, None),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
        vol.Optional(
            CONF_MONITORED_CONDITIONS, default=MONITORED_CONDITIONS_LIST
        ): vol.All(
            cv.ensure_list,
            [vol.In(MONITORED_CONDITIONS_LIST + list([CONTAINER_INFO_ALLINONE]))],
        ),
        vol.Optional(CONF_CONTAINERS, default=[]): cv.ensure_list,
        vol.Optional(CONF_RENAME, default={}): dict,
        vol.Optional(CONF_SENSORNAME, default=DEFAULT_SENSORNAME): cv.string,
        vol.Optional(CONF_SWITCHENABLED, default=True): cv.boolean,
        vol.Optional(CONF_SWITCHNAME, default=DEFAULT_SWITCHNAME): cv.string,
        vol.Optional(CONF_CERTPATH, default=""): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.All(cv.ensure_list, [vol.Any(DOCKER_SCHEMA)])}, extra=vol.ALLOW_EXTRA
)


#################################################################
async def async_setup(hass, config):
    """Will setup the Monitor Docker platform."""

    def RunDocker(hass, entry):
        """Wrapper around function for a separated thread."""

        # Create out asyncio loop, because we are already inside
        # a def (not main) we need to do create/set
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Create docker instance, it will have asyncio threads
        hass.data[DOMAIN][entry[CONF_NAME]] = {}
        hass.data[DOMAIN][entry[CONF_NAME]][CONFIG] = entry
        hass.data[DOMAIN][entry[CONF_NAME]][API] = DockerAPI(hass, entry)

        # Now run forever in this separated thread
        loop.run_forever()

    # Create domain monitor_docker data variable
    hass.data[DOMAIN] = {}

    # Now go through all possible entries, we support 1 or more docker hosts (untested)
    for entry in config[DOMAIN]:
        # Check if CONF_MONITORED_CONDITIONS has only ALLINONE, then expand to all
        if (
            len(entry[CONF_MONITORED_CONDITIONS]) == 1
            and CONTAINER_INFO_ALLINONE in entry[CONF_MONITORED_CONDITIONS]
        ):
            entry[CONF_MONITORED_CONDITIONS] = list(MONITORED_CONDITIONS_LIST) + list(
                [CONTAINER_INFO_ALLINONE]
            )

        if entry[CONF_NAME] in hass.data[DOMAIN]:
            _LOGGER.error(
                "Instance %s is duplicate, please assign an unique name",
                entry[CONF_NAME],
            )
            return False

        # Each docker hosts runs in its own thread. We need to pass hass too, for the load_platform
        thread = threading.Thread(
            target=RunDocker, kwargs={"hass": hass, "entry": entry}
        )
        thread.start()

    return True
