from hamsclient import meteoSwissClient

import datetime
import logging


import voluptuous as vol
import re
import sys

import  homeassistant.core as hass

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    WeatherEntity,
)
from homeassistant.const import (
    TEMP_CELSIUS,
    CONF_LATITUDE, 
    CONF_LONGITUDE,
)
import homeassistant.util.dt as dt_util

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv
import async_timeout
from homeassistant.helpers.entity import Entity

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    SENSOR_TYPE_CLASS,
    SENSOR_TYPE_ICON,
    SENSOR_TYPE_NAME,
    SENSOR_TYPE_UNIT,
    SENSOR_TYPES,
    SENSOR_DATA_ID,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config, async_add_entities):
    _LOGGER.info("Starting asnyc setup platform")
    client = hass.data[DOMAIN]['client']
  

    async_add_entities(
        [
            MeteoSwissSensor(sensor_type, client)
            for sensor_type in SENSOR_TYPES
        ],
        True,
    )

class MeteoSwissSensor(Entity):

    def __init__(self,sensor_type,client:meteoSwissClient):
        self._client = client
        if client is None:
            _LOGGER.error("Error empty client")
        self._state = None 
        self._type = sensor_type

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._data['name']} {SENSOR_TYPES[self._type][SENSOR_TYPE_NAME]}"
    
    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return self.name
    @property
    def state(self):
        
        dataId = SENSOR_TYPES[self._type][SENSOR_DATA_ID]
        try:
            return self._data['condition'][0][dataId]
        except:
            _LOGGER.debug("Unable to return data for : %s"%(self._data['condition'][0][dataId]))
            return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][SENSOR_TYPE_UNIT]
    

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES[self._type][SENSOR_TYPE_ICON]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][SENSOR_TYPE_CLASS]

    def update(self):
        #self._client.update()
        self._data = self._client.get_data()
        
