"""Monitor Docker switch component."""

import asyncio
import logging

from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchEntity
from homeassistant.const import CONF_NAME
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    API,
    CONFIG,
    CONF_CONTAINERS,
    CONF_RENAME,
    CONF_SWITCHENABLED,
    CONF_SWITCHNAME,
    CONTAINER,
    CONTAINER_INFO_STATE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Monitor Docker Switch."""

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

    def event_callback(self, remove=False):
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
