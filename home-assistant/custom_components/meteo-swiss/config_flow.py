"""Config flow to configure the Meteo-Swiss integration."""
import logging

import re
import voluptuous as vol
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN,CONF_POSTCODE,CONF_STATION,CONF_ENABLESENSORS
from hamsclient import meteoSwissClient



_LOGGER = logging.getLogger(__name__)



class MeteoSwissFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Init FlowHandler."""
        self._errors = {}
    
    async def validate_config(self,config):

        #check if the station id is found in stastion list
        stationNameChk =  await self.hass.async_add_executor_job(self._client.get_station_name,config[CONF_STATION])
        if(stationNameChk is None):
            self._errors[CONF_STATION] = "invalid_station_id"
            _LOGGER.warning("%s not found in meteo swiss station list"%(config[CONF_STATION]))

        #check if the station name is 3 character
        if(not re.match(r"^\w{3}$",config[CONF_STATION])):
            self._errors[CONF_STATION] = "invalid_station_name"
            _LOGGER.warning("%s is not a valid station ID"%config[CONF_STATION])
            
        if(not re.match(r"^\d{4}$",str(config[CONF_POSTCODE]))):
            self._errors[CONF_POSTCODE] = "invalid_postcode"
            _LOGGER.warning("%s is not a valid post code"%config[CONF_POSTCODE])

        
            
        if(len(self._errors) == 0):
            _LOGGER.info("Configuration for meteo swiss intergration validated")
            return True     
        else:
            _LOGGER.error("Configuration error for meteo suisse integration")
            return False
    
    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        self._errors = {}
        
        lat = self.hass.config.latitude
        lon = self.hass.config.longitude
        self._client = await self.hass.async_add_executor_job(meteoSwissClient)
        self._postCode = await self.hass.async_add_executor_job(self._client.getPostCode,lat,lon)
        _LOGGER.debug("Get closest station for Lon : %s - Lat : %s",lon,lat)
        self._station =await self.hass.async_add_executor_job(self._client.get_closest_station,lat,lon) 
        
        if(self._station is not None):
            self._stationName = await self.hass.async_add_executor_job(self._client.get_station_name,self._station)
        else:
            self._stationName = None

        _LOGGER.debug("Lon : %s - Lat : %s - PostCode %s Station %s Name: %s"%(lon,lat,self._postCode,self._station,self._stationName))
        if user_input is not None:
            _LOGGER.debug("User input is set")
            if(await self.validate_config(user_input)):
                return self.async_create_entry(title=user_input[CONF_NAME],data=user_input)
            else:
                
                return  self._show_config_form(user_input)
            
        else:
            _LOGGER.debug("User input is set value is not set: ")
            return  self._show_config_form(user_input)
        
        
    @callback
    def _show_config_form(self,user_input):
        """Show the setup form to the user."""
       
        if user_input is None:
            user_input = {}
       
        data_schema = {
            vol.Required(CONF_NAME,default=self._stationName): str,
            vol.Required(CONF_POSTCODE,default=self._postCode): int,
            vol.Required(CONF_STATION,default=self._station): str,
            vol.Required(CONF_ENABLESENSORS,default=True):bool
        }

        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=self._errors
        )

   
    async def async_step_import(self, user_input):
        """Import a config entry."""
        print(user_input)
        return await self.async_step_user(user_input)        