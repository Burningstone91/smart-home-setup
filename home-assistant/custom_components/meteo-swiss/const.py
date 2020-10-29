from homeassistant.const import (
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
    TIME_MINUTES,
    PERCENTAGE,
    TIME_MINUTES,
    PRESSURE_HPA,
    DEGREE,
    IRRADIATION_WATTS_PER_SQUARE_METER,
)

DOMAIN = "meteo-swiss"
CONF_POSTCODE = "postcode"
CONF_STATION = "station"
CONF_DISPLAYNAME = "displayname"
CONF_ENABLESENSORS = "enablesensors"
CONF_FORECASTTYPE= "forecasttype"

#Mapping for conditions vs icon ID of meteoswiss
#ID < 100 for day icons
#ID > 100 for night icons
#Meteo swiss has more lvl for cloudy an rainy than home assistant
CONDITION_CLASSES = {
    "clear-night": [101],
    "cloudy": [5,35,105,135],
    "fog": [27,28,127,128],
    "hail": [],
    "lightning": [12,112],
    "lightning-rainy": [13,23,24,25,32,113,123,124,125,132],
    "partlycloudy": [2,3,4,102,103,104],
    "pouring": [20,120],
    "rainy": [6,9,14,17,29,33,106,109,114,117,129,133],
    "snowy": [8,11,16,19,22,30,34,108,111,116,119,122,130,134],
    "snowy-rainy": [7,10,15,18,21,31,107,110,115,118,121,131],
    "sunny": [1,26,126],
    "windy": [],
    "windy-variant": [],
    "exceptional": [],
}

SENSOR_TYPE_NAME = "name"
SENSOR_TYPE_UNIT = "unit"
SENSOR_TYPE_ICON = "icon"
SENSOR_TYPE_CLASS = "device_class"
SENSOR_DATA_ID = "msDataId"
SENSOR_TYPES = {
    "temperature": {
        SENSOR_TYPE_NAME: "Temperature",
        SENSOR_TYPE_UNIT: TEMP_CELSIUS,
        SENSOR_TYPE_ICON: "mdi:thermometer",
        SENSOR_TYPE_CLASS: "temperature",
        SENSOR_DATA_ID: "tre200s0"
    },
    "10minrain": {
        SENSOR_TYPE_NAME: "10minrain",
        SENSOR_TYPE_UNIT: "mm",
        SENSOR_TYPE_ICON: "mdi:water",
        SENSOR_TYPE_CLASS: None,
        SENSOR_DATA_ID: "rre150z0"
    },
    "10minsun": {
        SENSOR_TYPE_NAME: "10minsun",
        SENSOR_TYPE_UNIT: TIME_MINUTES,
        SENSOR_TYPE_ICON: "mdi:weather-sunny",
        SENSOR_TYPE_CLASS: None,
        SENSOR_DATA_ID: "sre000z0"
    },
    "sun_radiant": {
        SENSOR_TYPE_NAME: "sun_radiant",
        SENSOR_TYPE_UNIT: IRRADIATION_WATTS_PER_SQUARE_METER,
        SENSOR_TYPE_ICON: "mdi:weather-sunny",
        SENSOR_TYPE_CLASS: None,
        SENSOR_DATA_ID: "gre000z0"
    },
    "humidity": {
        SENSOR_TYPE_NAME: "humidity",
        SENSOR_TYPE_UNIT: PERCENTAGE,
        SENSOR_TYPE_ICON: "mdi:water-percent",
        SENSOR_TYPE_CLASS: None,
        SENSOR_DATA_ID: "ure200s0"
    },
    "dew_point": {
        SENSOR_TYPE_NAME: "dew_point",
        SENSOR_TYPE_UNIT: TEMP_CELSIUS,
        SENSOR_TYPE_ICON: "mdi:weather-fog",
        SENSOR_TYPE_CLASS: None,
        SENSOR_DATA_ID: "tde200s0"
    },
    "wind_direction": {
        SENSOR_TYPE_NAME: "wind_direction",
        SENSOR_TYPE_UNIT: DEGREE,
        SENSOR_TYPE_ICON: "mdi:compass-rose",
        SENSOR_TYPE_CLASS: None,
        SENSOR_DATA_ID: "dkl010z0"
    },
    "wind_speed": {
        SENSOR_TYPE_NAME: "wind_speed",
        SENSOR_TYPE_UNIT: SPEED_KILOMETERS_PER_HOUR,
        SENSOR_TYPE_ICON: "mdi:weather-windy",
        SENSOR_TYPE_CLASS: None,
        SENSOR_DATA_ID: "fu3010z0"
    },
    "wind_speed_max": {
        SENSOR_TYPE_NAME: "wind_speed_max",
        SENSOR_TYPE_UNIT: SPEED_KILOMETERS_PER_HOUR,
        SENSOR_TYPE_ICON: "mdi:weather-windy",
        SENSOR_TYPE_CLASS: None,
        SENSOR_DATA_ID: "fu3010z1"
    },
    "pressure": {
        SENSOR_TYPE_NAME: "pressure",
        SENSOR_TYPE_UNIT: PRESSURE_HPA,
        SENSOR_TYPE_ICON: "mdi:gauge",
        SENSOR_TYPE_CLASS: None,
        SENSOR_DATA_ID: "prestas0"
    }
}