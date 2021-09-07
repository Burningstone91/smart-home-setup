"""Monitor Docker switch component."""

import asyncio
import logging
import voluptuous as vol

from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchEntity
from homeassistant.const import CONF_NAME
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.util import slugify

from .const import (
    API,
    ATTR_NAME,
    CONF_CONTAINERS,
    CONF_RENAME,
    CONF_SWITCHENABLED,
    CONF_SWITCHNAME,
    CONFIG,
    CONTAINER,
    CONTAINER_INFO_STATE,
    DOMAIN,
    SERVICE_RESTART,
)

SERVICE_RESTART_SCHEMA = vol.Schema({ATTR_NAME: cv.string})

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Monitor Docker Switch."""

    async def async_restart(parm):

        cname = parm.data[ATTR_NAME]
        if len(config[CONF_CONTAINERS]) == 0:
            api = hass.data[DOMAIN][name][API]
            if api.get_container(cname):
                await api.get_container(cname).restart()
            else:
                _LOGGER.error(
                    "Service restart failed, container '%s'does not exist", cname
                )
        elif cname in config[CONF_CONTAINERS]:
            _LOGGER.debug("Trying to restart container '%s'", cname)

            api = hass.data[DOMAIN][name][API]
            if api.get_container(cname):
                await api.get_container(cname).restart()
            else:
                _LOGGER.error(
                    "Service restart failed, container '%s'does not exist", cname
                )
        else:
            _LOGGER.error(
                "Service restart failed, container '%s' is not configured", cname
            )

    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    api = hass.data[DOMAIN][name][API]
    config = hass.data[DOMAIN][name][CONFIG]
    prefix = config[CONF_NAME]

    # Don't create any switch if disabled
    if not config[CONF_SWITCHENABLED]:
        _LOGGER.debug("Switch(es) are disabled")
        return True

    _LOGGER.debug("Setting up switch(es)")

    switches = []

    # We support add/re-add of a container
    if CONTAINER in discovery_info:
        clist = [discovery_info[CONTAINER]]
    else:
        clist = api.list_containers()

    for cname in clist:
        if cname in config[CONF_CONTAINERS] or not config[CONF_CONTAINERS]:
            _LOGGER.debug("%s: Adding component Switch", cname)

            switches.append(
                DockerContainerSwitch(
                    api.get_container(cname),
                    prefix,
                    cname,
                    config[CONF_RENAME].get(cname, cname),
                    config[CONF_SWITCHNAME],
                )
            )

    if not switches:
        _LOGGER.info("No containers set-up")
        return False

    async_add_entities(switches, True)

    # platform = entity_platform.current_platform.get()
    # platform.async_register_entity_service(SERVICE_RESTART, {}, "async_restart")
    hass.services.async_register(
        DOMAIN, SERVICE_RESTART, async_restart, schema=SERVICE_RESTART_SCHEMA
    )

    return True


class DockerContainerSwitch(SwitchEntity):
    def __init__(self, container, prefix, cname, alias, name_format):
        self._loop = asyncio.get_running_loop()
        self._container = container
        self._prefix = prefix
        self._cname = cname
        self._state = False
        self._entity_id = ENTITY_ID_FORMAT.format(
            slugify(self._prefix + "_" + self._cname)
        )
        self._name = name_format.format(name=alias)

    @property
    def entity_id(self):
        """Return the entity id of the switch."""
        return self._entity_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self):
        return False

    @property
    def icon(self):
        return "mdi:docker"

    @property
    def device_state_attributes(self):
        return {}

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self):
        await self._container.start()
        self._state = True
        self.async_schedule_update_ha_state()

    async def async_turn_off(self):
        await self._container.stop()
        self._state = False
        self.async_schedule_update_ha_state()

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._container.register_callback(self.event_callback, "switch")

        # Call event callback for possible information available
        self.event_callback()

    def event_callback(self, name="", remove=False):
        """Callback for update of container information."""

        if remove:
            _LOGGER.info("%s: Removing switch entity", self._cname)
            self._loop.create_task(self.async_remove())
            return

        state = None

        try:
            info = self._container.get_info()
        except Exception as err:
            _LOGGER.error("%s: Cannot request container info", str(err))
        else:
            if info is not None:
                state = info.get(CONTAINER_INFO_STATE) == "running"

        if state is not self._state:
            self._state = state
            self.async_schedule_update_ha_state()
