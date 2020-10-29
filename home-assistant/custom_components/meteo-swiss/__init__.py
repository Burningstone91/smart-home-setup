import requests
import logging
import asyncio
import datetime
from homeassistant.core import Config, HomeAssistant
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from hamsclient import meteoSwissClient
from .const import CONF_DISPLAYNAME,CONF_POSTCODE,CONF_STATION,CONF_ENABLESENSORS
from homeassistant.util import Throttle

DOMAIN = 'meteo-swiss'
_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=1)


async def async_setup(hass: HomeAssistant, config: Config):
    _LOGGER.debug("Async setup meteo swiss")
    
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, 
                context={"source": SOURCE_IMPORT}, 
                data=conf
            )
    )
    _LOGGER.debug("END Async setup meteo swiss")
    return True

async def async_setup_entry(hass: HomeAssistant, config: Config):
    hass.data.setdefault(DOMAIN, {})

    client = await hass.async_add_executor_job(meteoSwissClient,config.data['name'],config.data[CONF_POSTCODE],config.data[CONF_STATION])
    _LOGGER.debug("Current configuration : %s"%(config.data))

    hass.data[DOMAIN]['client'] = MeteoSwissUpdater(client)
    await hass.async_add_executor_job(hass.data[DOMAIN]['client'].update)

    if config.data['enablesensors']:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config, "sensor")
        )
        _LOGGER.debug("Starting entry sensor")

    hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config, "weather")
        )
    _LOGGER.debug("Start entry weather")

    #await 
    return True

async def async_unload_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, "weather")
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.data)

    return unload_ok

class MeteoSwissUpdater:
    def __init__(self,client:meteoSwissClient):
        self._client = client
    
    def get_data(self):
        return self._client.get_data()

    def get_client(self):
        return self._client

    @Throttle(SCAN_INTERVAL)
    def update(self):
        _LOGGER.debug("MS Updater update start")
        try:
            self._client.update()
        except :
            _LOGGER.error("Unexpected error ")
        _LOGGER.debug("MS Updater update end")