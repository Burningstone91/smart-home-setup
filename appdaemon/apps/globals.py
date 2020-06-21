"""Define persons in household and house itself."""

PERSONS = {
    "Dimitri": {
        "person": "person.dimitri",
        "sensor_room_presence": "sensor.dimitri_room_presence",
        "topic_room_device_tracker": "location/dimitri_room_presence",
        "input_select_non_binary_state": "input_select.dimitri_non_binary_presence",
    },
    "Sabrina": {
        "person": "person.sabrina",
        "sensor_room_presence": "sensor.sabrina_room_presence",
        "topic_room_device_tracker": "location/sabrina_room_presence",
        "input_select_non_binary_state": "input_select.sabrina_non_binary_presence",
    },
}

HOUSE = {
    "input_select_presence": "input_select.house_presence_state"
}