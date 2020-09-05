# Burningstone's Smart Home Journey
Installation and Configuration of my Smart Home Setup

## Introduction
I discovered Home Assistant around 2 years ago, installed it, played a bit with it, but didn't really have a need for it at that time. Some Philips Hue bulbs and Dimmers later, I gave Home Assistant another try. This time it got me hooked. I became addicted immediately. This was a bit more than 1 year ago. In this time I started to learn Python, YAML, wrote my own code for automations, etc. and setup a system that works pretty stable and covers my current needs. You can find my current setup [here](https://github.com/Burningstone91/smart-home).

This is the diagram of all the devices and how they connect and communicate with Home Assistant from my current setup. This will be adjusted during this journey as I'm trying to optimize and streamline a few things or use other software/hardware for other things.

![Alt text](/git-pictures/smart_home_diagram.png?raw=true "Smart Home Diagram")

And here is the diagram of my network incl. VLANs. I may do a write-up on this as well at a later stage.

![Alt text](/git-pictures/network_diagram.png?raw=true "Network Diagram")

Now I will build my whole setup from scratch, add some new features and hardware and you can follow me on this journey. I will keep adding my new configuration and the corresponding documentation continuously to this repo. You may ask, why I do this when I have a stable, running system? 
First, this will be a documentation that I can use to give me an overview of my system and in worst case (house burnt down + wife lost USB stick attached to key + I lost USB stick attached to key + I lost external drive that I always carry in my backpack, yes I know I'm paranoid :P) help me to setup everything again. 
Second, I hope that other people can profit from this, learn from my journey, use parts of my config in their own system or at least it helps them to solve one of their issues. 
And third, my current setup grew quite a lot in complexity. Due to my skills evolving and learning new tricks or methods to do certain things, it became inconsistent in regards to naming and in how and where things are configured and the documentation is lacking heavily. 

!!!WARNING!!! I'm by no means a programmer and I don't work as a professional in IT or something IT related. I'm just passionate about home automation, programming, IoT and technology in general.

If you find any information here useful feel free to buy me a coffee :)

<a href="https://www.buymeacoff.ee/u89Ao5n" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee" style="height: 19px !important;width: 68px !important;" ></a>

## Overview
I will explain here the different parts of my home automation system and how I set them up. For each part, I will talk about the hardware involved and how I integrated it into the system and I will also give an explanation on the automations and the corresponding code related to this part. 

* <a href="https://github.com/Burningstone91/smart-home-setup#start">
      Start of my Journey and Basic Setup
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#mqtt">
      Setup MQTT Broker
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#appdaemon">
      Setup AppDaemon - Automation Engine
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#presence-detection">
      Presence Detection
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#bed-occupancy">
      Bed Occupancy
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#zigbee-zwave">
      ZigBee(deCONZ) /Z-Wave (OZW Daemon)
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#lighting">
      Lighting
  </a>

## Start of my Jouney and Basic Setup <a name="start" href="https://github.com/Burningstone91/smart-home-setup#start"></a>

First some preparations and the install of [Home Assistant](https://www.home-assistant.io/), which will be the core of the home automation system.

### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:20%;">
Intel NUC
</td>
</tr>

<tr>
<td align="center" style="width:20%;">
<img src="git-pictures/device_pictures/nuc.jpg" raw=true height="100" alt="NUC" />
</td>
</tr>

<tr><td colspan="1">
My "Server" is an Intel NUC with an i3-7100U CPU, 8 GB of RAM and a 1 TB SSD (I use it for other virtual machines as well). The Smart Home runs inside an Ubuntu virtual machine in Proxmox. I'm using Home Assistant Container in my setup.
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

### Preparations
Install Docker and Docker-Compose on the host machine following the official instructions online.

Create the docker-compose file and a directory which will contain the Home Assistant configuration:

```
touch docker-compose.yml
mkdir home-assistant
```

The docker-compose file contains the configuration for the different docker containers that will be running in the stack.

### Configure Home Assistant Docker container
Add the following to docker-compose.yml to configure the Home Assistant Core docker container:

```yaml
version: "3"
services:
  hass:
    container_name: hass
    image: homeassistant/home-assistant:0.114.0
    network_mode: host
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - ./home-assistant:/config
```

### Start Docker Stack for the First Time
Enter the following command while you are in the same directory as the docker-compose.yml file:

```
docker-compose up -d
```

This will read the config from the docker-compose.yml file and start the docker stack in the background. This will take some time as it will now download and install Home Assistant Core.

After the install is finished, Home Assistant should be available under http://ip-of-host:8123

### Initial Home Assistant Configuration
Follow the instructions on the screen to setup the first user, your home location, elevation, time zone and unit system. 

### Structuring the Home Assistant Configuration
Packages allow to split up the configuration.yaml. Like this, all configuration such as ```switch:```, ```input_boolean:```, etc. that belong to the same logical group (e.g. room) can be put inside a separate file instead of defining everything in the designated block inside configuration.yaml. You can also easily share your configuration for e.g. an alarm clock, including all input_selects, input_booleans, sensors and whatever else you need to setup an alarm clock. 

Enable the usage of packages by adding the following to configuration.yaml:

```yaml
homeassistant:
  packages: !include_dir_named packages/
```

And create a directory "packages" in the same directory as configuration.yaml:

```
mkdir packages
```

Due to this the following lines from configuration.yaml can be removed:

```yaml
group: !include groups.yaml
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
```

And the corresponding files groups.yaml, automations.yaml, scripts.yaml and scenes.yaml can be removed as well. 

The following lines can be removed as well:

```yaml
# http:
#   base_url: example.duckdns.org:8123

# Text to speech
tts:
  - platform: google_translate
```

Remove default_config: from configuration.yaml and instead add the following lines:

```yaml
config:
frontend:
person:
sun:
system_health:
```

The final file should look something like this:

```yaml
homeassistant:
  packages: !include_dir_named packages/

config:
frontend:
person:
sun:
system_health:
```

Restart the Home Assistant container with:

```
docker restart hass
```

Now the initial configuration is done and Home Assistant is up and running.

</p>
</details>

## Setup MQTT Broker <a name="mqtt" href="https://github.com/Burningstone91/smart-home-setup#mqtt"></a>
The MQTT broker is the server that hosts the MQTT network. It provides the infrastructure for devices to publish/subscribe to topics. In this setup [Mosquitto](https://mosquitto.org/) is the broker of choice.

<details><summary>Step-by-step Guide</summary>
<p>

On the host machine create a directory that will contain the configuration for Mosquitto:

```
mkdir mosquitto
```

Create sub directories, that will contain the configuration, persistence storage and the logs:

```
cd mosquitto
mkdir config
mkdir data
mkdir log
```

Create a file called mosquitto.conf inside the config directory:

```
cd config
touch mosquitto.conf
```

and add the following to the file:


```
pid_file /var/run/mosquitto.pid

persistence true
persistence_location /mosquitto/data/

log_dest file /mosquitto/log/mosquitto.log
log_dest stdout

password_file /mosquitto/config/passwd
allow_anonymous false
```

Stop the docker stack:

```
docker-compose down
```

Add the following to the docker-compose.yml to configure the Mosquitto docker container:

```yaml
  mqtt:
    container_name: mqtt
    image: eclipse-mosquitto
    ports:
      - "1883:1883"
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./mosquitto/config:/mosquitto/config
      - ./mosquitto/log:/mosquitto/log
      - ./mosquitto/data:/mosquitto/data
```

Start the docker stack again:

```
docker-compose up -d
```

Bash into the mosquitto container:

```
docker exec -it mqtt /bin/sh
```

Enter the following command to create a password file:

```
mosquitto_passwd -c /mosquitto/config/passwd [username]
```

You will be promted to enter your password twice.
Restart the mqtt broker with:

```
docker restart mqtt
```

To test the MQTT broker, install mosquitto-clients on any other machine:

```
sudo apt-get install mosquitto-clients
```

Subscribe to the topic "test" in one terminal:

```
mosquitto_sub -h localhost -t "test" -u "[username]" -P "[password]"
```

Publish to the same topic in another terminal:

```
mosquitto_pub -h localhost -t "test" -m "Hello World" -u "[username]" -P "[password]"
```

You should now see "Hello World" showing up on the first terminal.

### Configure MQTT Broker in Home Assistant
#### Configure via UI
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on the orange plus in the bottom right corner, search for "MQTT" and click on it.
Enter "127.0.0.1" in the field "broker".
Enter your username and password. Tick the box next to "Enable Discovery". If Discovery is enabled, Home Assistant will automatically detect certain devices. The device needs to send a specific payload when it first connects to MQTT, this message contains the information that Home Assistant needs to create the device and the corresponding entities. Lots of integrations have this specific payload built-in and therefore your devices should be detected automatically.

#### Configure via Configuration Files
Create a file called "core.yaml" inside the directory config/packages. This file will be used for all config relating to the core. Add the following to the file:

```yaml
mqtt:
  broker: 127.0.0.1
  username: [username]
  password: [password]
  discovery: true
```

</p>
</details>

## Setup AppDaemon - Automation Engine <a name="appdaemon" href="https://github.com/Burningstone91/smart-home-setup#appdaemon"></a>
[AppDaemon](https://appdaemon.readthedocs.io/en/latest/) can be used to write Home Automation apps for Home Assistant in Python. It's an alternative to Home Assistant's inbuilt automations. You can create more complicated automations and reuse the same code for multiple apps. The official AppDaemon documentation provides a [detailed explanation](https://appdaemon.readthedocs.io/en/latest/APPGUIDE.html) on how to create your first app. I use AppDaemon for all my automations for multiple reasons such as overcoming limitations of Home Assistant automations (which got a lot more powerful starting from 0.113.0!), creating automations and entities that persist reboot, remove code redundancy, learn python etc. It just better fits my way of thinking, connecting automations together instead of separating each and everything into a separate automations.

<details><summary>Step-by-step Guide</summary>
<p>

Now to the setup. First create a long-lived access token for authentication with Home Assistant.

In Home Assistant on the sidebar click on the username in the bottom left corner. In the section "Long-Lived Access Tokens", click on "Create Token", give it a meaningful and save the token somewhere.

On the host machine create a directory that will contain the configuration for AppDaemon:

```
mkdir appdaemon
```

Create sub directories, that will contain the apps and the logs:

```
cd appdaemon
mkdir apps
mkdir logs
```

Create a file called appdaemon.yaml:

```
touch appdaemon.yaml
```

and add the following to the file:

```yaml
logs:
  main_log:
    filename: /conf/logs/appdaemon.log
  error_log:
    filename: /conf/logs/error.log
  access_log:
    filename: /conf/logs/access.log
appdaemon:
  app_dir: /conf/apps
  elevation: 12
  latitude: 234
  longitude: 567
  missing_app_warnings: 1
  production_mode: False
  time_zone: 'Europe/Zurich'
  plugins:
    HASS:
      type: hass
      namespace: hass
      token: ey123-...g789ft790 # token generated in previous step
      ha_url: http://ip-of-host:8123 
    MQTT:
      type: mqtt
      namespace: mqtt
      client_id: AD_4
      client_host: ip-of-host
      client_user: mqtt_username
      client_password: super_secret_mqtt_password
http:
  url: http://ip-of-host:5050
api:
admin:
  title: AppDaemon
  stats_update: realtime
```

Create a file called requirements.txt:

```
touch requirements.txt
```

and add the following to the file:
```
voluptuous==0.11.5
```
This will install Voluptuous, which is used for config validation later on.

Stop the docker stack:

```
docker-compose down
```

Add the following to the docker-compose.yml to configure the AppDaemon docker container:

```yaml
  appdaemon:
    container_name: appdaemon
    image: acockburn/appdaemon:4.0.3
    depends_on:
      - hass
    ports:
      - "5050:5050"
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./appdaemon:/conf
```

Start the docker stack again:

```
docker-compose up -d
```
Now we are going to create a kind of "Base App", from which all other apps can inherit from. I got this idea from [this](https://github.com/bachya/smart-home/blob/master/appdaemon/settings/apps/core.py) repo of Aaron Bach.

Create a file called appbase.py inside the apps directory of AppDaemon.

Add the following to the file:

```python
"""Define a generic object which  all apps/automations inherit from."""
from datetime import datetime as dt
from typing import Union, Optional
import adbase as ad
import voluptuous as vol

from helpers import voluptuous_helper as vol_help


APP_SCHEMA = vol.Schema(
    {
        vol.Required("module"): str,
        vol.Required("class"): str,
        vol.Optional("dependencies"): vol_help.ensure_list,
    },
    extra=vol.ALLOW_EXTRA,
)


class AppBase(ad.ADBase):
    """Define a base automation object."""

    APP_SCHEMA = APP_SCHEMA

    def initialize(self) -> None:
        """Initialize."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")

        # Validate app configuration
        try:
            self.APP_SCHEMA(self.args)
        except vol.Invalid as err:
            self.adbase.log(f"Invalid configuration: {err}", log="error_log")
            return

        # Define holding place for timers
        self.handles = {}

        # Create a reference to every dependency in the configuration
        for app in self.args.get("dependencies", {}):
            if not getattr(self, app, None):
                setattr(self, app, self.adbase.get_app(app))

        # Run the app configuration if specified
        if hasattr(self, "configure"):
            self.configure()
```

In addition create a folder called utils and put a file called config_validation.py inside this folder with the following content:

```python
"""Define methods to validate configuration for voluptuous."""

import datetime
from typing import Any, Sequence, TypeVar, Union

import voluptuous as vol

T = TypeVar("T")  # pylint: disable=invalid-name


def ensure_list(value: Union[T, Sequence[T]]) -> Sequence[T]:
    """Validate if a given object is a list."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def entity_id(value: Any) -> str:
    """Validate if a given object is an entity ID."""
    value = str(value).lower()
    if "." in value:
        return value

    raise vol.Invalid("Invalid entity ID: {0}".format(value))


def valid_date(value: Any) -> datetime.date:
    """Validate if a given object is a date."""
    try:
        return datetime.datetime.strptime(value, "%d.%m.%Y")
    except ValueError:
        raise vol.Invalid(f"Invalid Date: {value}")


def valid_time(value: Any) -> datetime.datetime:
    """Validate if a given object is a time."""
    try:
        return datetime.datetime.strptime(value, "%H:%M:%S")
    except ValueError:
        raise vol.Invalid(f"Invalid Time: {value}")
```

Now when we create an app that usese the AppBase, it will automatically create a reference to every dependency in the app configuration. This way way we can use the methods and variables of the apps that our app depends on, to avoid redundant code. It will also do some basic config validation with Voluptuous and raise an error when you wrote "modle" instead of "module" for example. As we have multiple namespaces (HASS and MQTT), there are some variables that represent the MQTT and HASS namespace. This way you don't need to put "namespace=hass" when you call a method, instead you start the function call with "self.hass", if you want to do something in HASS namespace. Start it with "self.mqtt" to do something in MQTT namespace and start it with "self.adbase" to do something in the AppDaemon namespace (logging etc.).

This file is going to be extended later on with more functionality.

</p>
</details>


## Presence Detection <a name="presence-detection" href="https://github.com/Burningstone91/smart-home-setup#presence-detection"></a>

### Basic Explanation of Setup
I use the [person integration](https://www.home-assistant.io/integrations/person/) from Home Assistant to combine a bluetooth device tracker (device attached to my keys) and a gps device tracker (my phone). The docs give a detailed explanation on how the location is determined when multiple device trackers are used. Long story short, when I'm at home, my position is determined first by keys and then by phone. When I'm not home, my position is determined first by phone then by keys.

I use the phone device tracker together with the [zone integration](https://www.home-assistant.io/integrations/zone/) from Home Assistant to show in which place (work, grocery store, etc.) we are, when we are not home. This is reflected in the state of the person.

And I use the bluetooth device tracker together with [Room Assistant](https://www.room-assistant.io/) to show in which room we are when we are home. This is not reflected in the state of the person.

I'm using the bluetooth device trackers now for around 2 years and I did not have a single false trigger in this time. Home Assistant marks us as home before we open the front door and marks us as left 3 min after we left the house.

I adapted the method from Phil Hawthorne for [making presence detection not so binary](https://philhawthorne.com/making-home-assistants-presence-detection-not-so-binary/) in an AppDaemon app. This is used for example when we leave the house and come back a few minutes later, that it will not trigger any arrival automations.

I also have a presence state for the house which can be "someone home", "everyone home", "no one home" or "vacation". 

I'm going to explain each part of the presence detection system in detail including Hardware and Software used and how to set it up.

### Bluetooth Device Tracker - Presence on Room Level
#### Hardware used
<table align="center" border="0">

<tr>
<td align="center" style="width:50%;">
6x Raspberry Pi Zero W
</td>
<td align="center" style="width:50%;">
2x Nut Mini
</td>
</tr>

<tr>
<td align="center" style="width:50%;">
<img src="git-pictures/device_pictures/pi_zero_w.jpg" raw=true height="250" alt="Pi Zero W"/>
</td>
<td align="center" style="width:50%;">
<img src="git-pictures/device_pictures/nut_mini.jpg" raw=true height="250" alt="Nut mini" />
</td>
</tr>

<tr><td colspan="2">
The Nut Mini's are attatched to our keys and I'm soon going to buy some Fitness Bands to replace them. They send a Bluetooth Low Energy (BLE) signal every 3 seconds. There's one Raspberry Pi's as central as possible in every room that I want to automate and one close to the entrance door. The Pi's run <a href="https://companion.home-assistant.io/">Room Assistant</a>, which catches these signals and determines the location of the Nut Mini based on the strength of the signal. It talks to Home Assistant through MQTT and if discovery is enabled it will be detected automatically.
Due to the fact that only device tracker entities can be linked to a person, I use an AppDaemon app that updates the status of an MQTT device tracker whenever the state of the keys changes.
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

#### Room Assistant Setup
Now we are going to install and configure Room-Assistant on the Pi's. There are excellent guides on how to install it on Pi 3/4 or Pi Zero W on the page of the creator (https://www.room-assistant.io/). Because I have 6 Pi Zero W's in total and didn't want to install and configure each one separately, I use [Ansible](https://www.ansible.com/) to deploy it on all machines at once from my desktop (there's a tutorial as well for this on the site of the creator). 

Install Raspbian Buster Lite on each Raspberry Pi Zero W with SSH enabled.

On the host that runs Ansible, add the following to the file "/etc/ansible/hosts":

```yaml
[room_assistant]
10.10.70.7
10.10.70.8
10.10.70.9
10.10.70.10
10.10.70.11
10.10.70.12
```
This creates a group containing the ip-adresses of the room-assistant instances.

Create a public ssh key on the host that runs Ansible with:

```bash
ssh-keygen
```

Copy the public key to a Pi with:

```bash
ssh-copy-id pi@10.10.70.7
```

Repeat this for each Pi.

Login to each Pi with:

ssh pi@10.10.70.7

Confirm the promt about RSA key fingerprint by typing "yes" and pressing "Enter".

Create a directory that will contain the configuration for Room Assistant.

In this directory execute the following:

```bash
git clone https://github.com/mKeRix/ansible-playbooks.git
```

This will download the ansible playbook from the room-assistant creator. Change to the newly created directory and install the requirements with:

```bash
ansible-galaxy install -r requirements.yml
```

Create a file called "hosts.yaml", which will hold the configuration for Room Assistant. 
Add the following to the file:

```yaml
all:
  hosts:
    10.10.70.7:
      room_assistant_config: 
        global:
          instanceName: buero
    10.10.70.8:
      room_assistant_config: 
        global:
          instanceName: ankleidezimmer
    10.10.70.9:
      room_assistant_config: 
        global:
          instanceName: wohnzimmer
    10.10.70.10:
      room_assistant_config: 
        global:
          instanceName: schlafzimmer
    10.10.70.11:
      room_assistant_config: 
        global:
          instanceName: kueche
    10.10.70.12:
      room_assistant_config: 
        global:
          instanceName: garderobe
  vars:
    room_assistant_global_config:
      global:
        integrations:
          - homeAssistant
          - bluetoothLowEnergy
      homeAssistant:
        mqttUrl: 'mqtt://ip-of-home-assistant-machine:1883'
        mqttOptions:
          username: mqtt_username
          password: super_secret_mqtt_password
      bluetoothLowEnergy:
        whitelist:
          - ab6dg90dg0fg
          - ig8daf7s0dfd
        tagOverrides:
          ble-ab6dg90dg0fg:
            name: dimitri
          ble-ig8daf7s0dfd:
            name: sabrina
```

In the "homeAssistant" part we configure the user credentials for the MQTT broker we configured before.
The "tagOverrides" are used to give the tags a human readable name, this name will also be used for the sensor created in Home Assistant. Here the sensor in Home Assistant for my tag will be called "sensor.dimitri_room_presence".
The strings whitelisted under "bluetoothLowEnergy" are the mac adresses (lowercase and without colons) of the Nut Mini key tags. To get the mac adress of the Nut Mini's run the following commands on a machine that has a bluetooth adapter and bluetoothctl is installed (you can also do this from the Pi Zero W):

```bash
sudo bluetoothctl
scan on
```
It'll show the mac adress of any detected bluetooth device nearby.

Now run the Ansible playbook with:

```bash
ansible-playbook -i hosts.yml -u pi room-assistant.yml
```

And wait until the process is completed, it takes quite some time on the Pi Zero W.

SSH into each Pi and execute the following command:

```bash
sudo setcap cap_net_raw+eip $(eval readlink -f `which node`)
```

There should be one new sensor in Home Assistant for each device configured in Room-Assistant. This sensor will show the name of the room that istance that is closest to the Bluetooth tag. If none of the Room-Assistant instances sees the Bluetooth tag, it will show "not_home".

As of now, the sensor will probably often change state, depending on the strenght of the BLE signal. For example for me it jumps between 3 rooms in certain places. To eliminate this we set the parameter "maxDistance" in the different rooms. To get the value, I took the BLE tag and walked to multiple places in each room and stood there for a few seconds. I then look at the distances sent in MQTT with [MQTT explorer](http://mqtt-explorer.com/). I take the largest of these values and add a bit more for safety. Repeat for every room and then add them like this:

```yaml
all:
  hosts:
    10.10.70.7:
      room_assistant_config: 
        global:
          instanceName: buero
        bluetoothLowEnergy:
          maxDistance: 7.2
        cluster:
          weight: 6
    10.10.70.8:
      room_assistant_config: 
        global:
          instanceName: ankleidezimmer
        bluetoothLowEnergy:
          maxDistance: 4
        cluster:
          weight: 5
    10.10.70.9:
      room_assistant_config: 
        global:
          instanceName: wohnzimmer
        bluetoothLowEnergy:
          maxDistance: 8
        cluster:
          weight: 2
    10.10.70.10:
      room_assistant_config: 
        global:
          instanceName: schlafzimmer
        bluetoothLowEnergy:
          maxDistance: 7
        cluster:
          weight: 3
    10.10.70.11:
      room_assistant_config: 
        global:
          instanceName: kueche
        bluetoothLowEnergy:
          maxDistance: 6
        cluster:
          weight: 4
    10.10.70.12:
      room_assistant_config: 
        global:
          instanceName: garderobe
        cluster:
          weight: 1 
  vars:
    room_assistant_global_config:
      global:
        integrations:
          - homeAssistant
          - bluetoothLowEnergy
      homeAssistant:
        mqttUrl: 'mqtt://ip-of-home-assistant-machine:1883'
        mqttOptions:
          username: mqtt_username
          password: super_secret_mqtt_password
      bluetoothLowEnergy:
        timeout: 8
        whitelist:
          - cd1381f62e7d
          - f913395bc892
        tagOverrides:
          cd1381f62e7d:
            name: dimitri
          f913395bc892:
            name: sabrina
```

I also added weights for the different instances. If two instances send that they see a tag, the instance with the higher weight will win.

Now run the Ansible playbook again to update the configuration with:

```bash
ansible-playbook -i hosts.yml -u pi room-assistant.yml
```

#### Base Apps for Presence Detection (AppDaemon)
Now that we have sensors in place, which show in which room a person is in. We are going to use this to create a room presence detection app. I use AppDaemon a lot to create entities that only exist in AppDaemon, not in Home Assistant as I only use them for automations. If I still need access to this information in Home Assistant, I create a sensor in AppDaemon and feed it with the missing information. Thanks @Odianosen25 for showing me this feature approach.
For the room presence detection, we are going to create one app for areas, one app for persons, one app for the house and multiple apps to set different attributes of the persons, areas and the house based on the changes of the room presence sensors.

In the AppDaemon directory should be a folder called "apps". All the following apps need to be created inside this directory. 

We are going to start with the area app. The are app creates area entities that will have attributes for the persons (list of persons in area), the occupied state(True | False), the friendly name and the identifier.

Create a new file called "area.py". Add the following to this file:

```python
"""Define automations for areas."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv


class Area(AppBase):
    """Representation of an Area."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("area"): str,
            vol.Optional("attributes"): vol.Schema(
                {vol.Optional("friendly_name"): str}
            ),
            vol.Optional("occupancy"): vol.Schema(
                {vol.Optional(cv.entity_id): str}
            ),
        }
    )

    def configure(self) -> None:
        """Configure an area."""
        areas = self.adbase.get_state("area")
        area = self.args["area"]
        area_id = area.lower().replace(" ", "_")
        attributes = self.args["attributes"]
        self.area_entity = f"area.{area_id}"

        # Create an entity for the area if it doesn't already exist
        if self.area_entity not in areas.keys():
            if "friendly_name" not in attributes:
                attributes.update({"friendly_name": area.title()})

            attributes.update(
                {"id": area_id, "persons": [], "occupied": None, "occupancy": {}}
            )

            self.adbase.set_state(self.area_entity, state="idle", attributes=attributes)

        # Listen for no changes in area state for 30 seconds
        self.adbase.listen_state(self.on_state_change, self.area_entity, duration=30)

    def on_state_change(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when area doesn't change state for 30s."""
        # Set area to idle
        self.adbase.set_state(entity, state="idle")
```
Now we are going to create a configuration file to set up the areas in the house. Create a file for each area e.g. "bedroom.yaml".

The configuration parameters are as follows:

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | area | The module name of the app.
`class` | False | string | Area | The name of the Class.
`area` | False | string | | The identifier for the area.
`attributes` | True | dict | | The attributes for the area.

Attributes configuration:
key | optional | type | default | description
-- | -- | -- | -- | --
`friendly_name` | True | string | | The friendly name of the area.


Example:

```yaml
bedroom:
  module: area
  class: Area
  area: bedroom
  attributes:
    friendly_name: Schlafzimmer
```
Now we have an entity for each area configured this way, which exist only in AppDaemon and which we are going to use later in other apps and automations.

Next the "person" app. The person app creates person entities that will have attributes for the home state (True | False), the non-binary-presence state (just_left | away | just_arrived | home | extended_away), the full name, the identifier and notifiers belonging to this person. 

Create a new file called "person.py". Add the following to this file:

```python
"""Define automations for persons."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv

class Person(AppBase):
    """Representation of a Person."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("person"): str,
            vol.Required("attributes"): vol.Schema(
                {
                    vol.Required("full_name"): str,
                    vol.Optional("notifiers"): vol.All(cv.ensure_list, [str]),
                }
            )
        }
    )

    def configure(self) -> None:
        """Configure a person."""
        person = self.args["person"].lower()
        attributes = self.args["attributes"]
        entity_id = f"person.{person}"

        attributes.update(
            {
                "id": person,
                "home": None,
                "non_binary_presence": None
            }
        )

        self.adbase.set_state(entity_id, attributes=attributes)
```

Now we are going to create a configuration file to set up the persons in the household. Create a file called "persons.yaml".

The configuration parameters are as follows:

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | person | The module name of the app.
`class` | False | string | Person | The name of the Class.
`person` | False | string | | The short name of the person.
`attributes` | False | dict | | The attributes for the person.

Attributes configuration:
key | optional | type | default | description
-- | -- | -- | -- | --
`full_name` | False | string | | The full name of the person.
`notifiers` | True | list | | List of notifier entities belonging to this person.


Example:

```yaml
dimitri:
  module: person
  class: Person
  person: Dimitri
  attributes:
    full_name: Dimitri Li 
```

Now you have one entity for each person configured this way, which exists only in AppDaemon and which we are going to use later in other apps and automations.

Next the "house" app. The house app creates house entities that will have attributes for the persons (list of persons in house), presence state (someone_home | nobody_home | vacation | everyone_home), the occupied state(True | False), the friendly name and the identifier.

Create a new file called "house.py". Add the following to this file:

```python
"""Define automations for the house."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA


class House(AppBase):
    """Representation of a House."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("id"): str,
            vol.Optional("attributes"): vol.Schema(
                {
                    vol.Optional("friendly_name"): str,
                }
            )
        }
    )

    def configure(self) -> None:
        """Configure an area."""
        houses = self.adbase.get_state("house")
        house_id = self.args["id"]
        attributes = self.args.get("attributes")
        entity_id = f"house.{house_id}"

        # Create an entity for the house if it doesn't already exist
        if entity_id not in houses.keys():
            if "friendly_name" not in attributes:
                attributes.update({"friendly_name": area.title()})

            attributes.update(
                {
                    "id": house_id,
                    "persons": [],
                    "occupied": None,
                    "presence_state": None,
                }
            )

            self.adbase.set_state(entity_id, state="idle", attributes=attributes) 

        # Listen for no changes in house state for 30 seconds
        self.adbase.listen_state(
            self.state_changed, entity_id, duration=30
        )

    def state_changed(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when house doesn't change state for 30s."""
        # Set area to idle
        self.adbase.set_state(entity, state="idle")
```

Now we are going to create a configuration file to set up the persons in the household. Create a file called "house.yaml".

The configuration parameters are as follows:

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | house | The module name of the app.
`class` | False | string | House | The name of the Class.
`id` | False | string | | The identifier for the house.
`attributes` | True | dict | | The attributes for the house.

Attributes configuration:
key | optional | type | default | description
-- | -- | -- | -- | --
`friendly_name` | True | string | | The friendly name of the house.


Example:

```yaml
house:
  module: house
  class: House
  id: home
  attributes:
    friendly_name: Wohnung
  
```
Now we have an entity for the house, which exists only in AppDaemon and which we are going to use later in other apps and automations.

Next the presence apps, which set the different attributes of the areas, persons and the house.
The room presence app sets the area for each person entity and sets the person in the corresponding area entity whenever the room presence sensor changes state to a new state for 5 seconds. 

Create a file called "presence.py" and add the following:

```python
"""Define an automation for updating a device tracker from the state of a sensor."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv


class RoomPresence(AppBase):
    """Define a base class for room presence."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {vol.Required("sensors"): vol.Schema({vol.Optional(str): cv.entity_id})}
    )

    def configure(self) -> None:
        """Configure."""
        room_presence_sensors = self.args["sensors"]

        for person, sensor in room_presence_sensors.items():

            # Listen for person changing area
            self.hass.listen_state(
                self.on_sensor_change, sensor, duration=5, person_id=person
            )

    def on_sensor_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when room presence sensor changes state."""
        if new != old:
            person_id = kwargs["person_id"]
            person_entity = f"person.{person_id}"
            areas = self.adbase.get_state("area")
            area_entity = f"area.{new}"

            # Remove person from other areas
            for area in areas.keys():
                if area != area_entity:
                    persons = self.adbase.get_state(area, attribute="persons")
                    if person_id in persons:
                        persons.remove(person_id)
                        self.adbase.set_state(area, persons=persons)

            # Add person to new area
            if new != "not_home":
                persons = self.adbase.get_state(area_entity, attribute="persons")
                if person_id not in persons:
                    persons.append(person_id)
                    self.adbase.set_state(area_entity, persons=persons)

            # Set area for person
            self.adbase.set_state(person_entity, area=new)
            self.adbase.log(f"{person_id.capitalize()} Area: {new}")
```

Create a corresponding configuration file called "presence.yaml" and add the following:

```yaml
room_presence_app:
  module: presence
  class: RoomPresence
  sensors:
    dimitri: sensor.room_presence_dimitri
    sabrina: sensor.room_presence_sabrina
```

In the sensor section put the person_id (configured in the person app) and the corresponding room presence sensor. 

The person presence app sets the home state of the person to True or False based on the area the person is currently in. If the area is "not_home" for 3 minutes, the home state is set to False.

Add another class in the "presence.py" file:

```python
class PersonPresence(AppBase):
    """Define a base class for binary person presence."""

    def configure(self) -> None:
        """Configure."""
        persons = self.adbase.get_state("person")

        for person in persons.keys():
            # Listen for person entering the house
            self.adbase.listen_state(
                self.on_person_arrival,
                person,
                attribute="area",
            )

            # area 3 minutes "not_home" -> person left
            self.adbase.listen_state(
                self.on_person_leave,
                person,
                attribute="area",
                new="not_home",
                duration=3 * 60
            )

    def on_person_arrival(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when person enters house."""
        # Set person to "home"
        not_home_states = ["not_home", "undefined", "unknown", None]
        if new != old and old in not_home_states and new not in not_home_states:
            self.adbase.set_state(entity, home=True)
            self.adbase.log(f"{entity.split('.')[1].capitalize()}: home")
            
    def on_person_leave(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when person left house for 3 minutes."""
        # Set person to "not home"
        self.adbase.set_state(entity, home=False)
        self.adbase.log(f"{entity.split('.')[1].capitalize()}: not home")
```

In the corresponding configuration file called "presence.yaml" and add the following:

```yaml
person_presence_app:
  module: presence
  class: PersonPresence
```

The non binary presence state and the presence state of the house are coverd in a later topic.

#### MQTT Device Tracker
Because the sensor can not be used with the person integration, we use the [MQTT device tracker integration](https://www.home-assistant.io/integrations/device_tracker.mqtt/) and bind the resulting device tracker to the person integration. 

To add an MQTT device tracker, create a file called "persons.yaml" in the folder "packages". This file will be used for all configuration related to persons.

Add the following to the file:

```yaml
device_tracker:
  platform: mqtt
  devices:
    room_presence_dimitri: 'location/dimitri_room_presence'
    room_presence_sabrina: 'location/sabrina_room_presence'
  source_type: bluetooth_le
```

This will create two device trackers. By publishing "home" or "not_home" to the MQTT topic 'location/dimitri_room_presence', the state of "device_tracker.room_presence_dimitri" will be updated accordingly.

Restart Home Assistant. There should be two new device_trackers under "Developer Tools" -> "States".

#### Device Tracker Update App (AppDaemon)
Create a python dictionary that contains the base configuration of the home. Such as the presence state of the house, the notifiers of the phones etc. This dictionary will be appended later on when more apps are added.

In the AppDaemon directory should be a folder called "apps". Create a new file called "globals.py" inside this folder. Add the following to this file:

```python
PERSONS = {
    "Dimitri": {
        "sensor_room_presence": "sensor.dimitri_room_presence",
        "topic_room_device_tracker": "location/dimitri_room_presence",
    },
    "Sabrina": {
        "sensor_room_presence": "sensor.sabrina_room_presence",
        "topic_room_device_tracker": "location/sabrina_room_presence",
    },
}
```
where keys_presence is the sensor that shows the location of the keys (sensor created by room-assistant) and keys_topic is the MQTT topic that controls the MQTT device tracker that has been created in the previous step.

Now add a file called "presence.py" to the same directory and add the following:

```python
from appbase import AppBase, APP_SCHEMA
from globals import PERSONS

class BleDeviceTrackerUpdater(AppBase):
    """Define a base class for the BLE updater."""

    def configure(self):
        """Configure."""
        for person, attribute in PERSONS.items():
            presence_sensor = attribute['sensor_room_presence']
            topic = attribute['topic_room_device_tracker']

            # set initial state of device tracker
            if self.hass.get_state(presence_sensor) =="not_home":
                self.update_device_tracker(topic, "not_home")
            else:
                self.update_device_tracker(topic, "home")

            # set device tracker to not_home after 5 minutes of no activity
            self.hass.listen_state(
                self.on_presence_change, 
                presence_sensor,
                new="not_home",
                duration=5*60,
                target_state="not_home",
                topic=topic,
            )

            # update state of device tracker whenever presence sensor changes
            self.hass.listen_state(
                self.on_presence_change, 
                presence_sensor,
                topic=topic,
            )

    def on_presence_change(self, entity, attribute, old, new, kwargs):
        """Take action on presence change."""
        if kwargs.get("target_state") == "not_home":
            self.update_device_tracker(kwargs["topic"], "not_home")
        elif new != "not_home":
            self.update_device_tracker(kwargs["topic"], "home")

    def update_device_tracker(self, topic, target_state):
        """Update the location of the MQTT device tracker."""
        self.mqtt.mqtt_publish(
            topic,
            target_state,
            namespace="mqtt",
        )
```
This looks complicated for such a simple task, however the app is prepared to be extended later on.

At the top we import the person information we created in the globals.py file with:

```python
from globals import PERSONS
```

In the configure section it loops through the dictionary of each person and checks the presence sensor and the topic. Then it initially sets the state of the MQTT device tracker by checking the state of the presence sensor. Afterwards there's one listener that triggers the "on_presence_change" method when the presence sensor is "not_home" for 5 minutes (duration=5*60) and there's another listener that triggers the "on_presence_change" method whenever the presence sensor changes state.
The "on_presence_change" method checks if the target_state "not_home" has been provided. In this case it updates the MQTT device tracker to "not_home", otherwise it checks the value of the presence sensor and if it is something else than "not_home" it updates the MQTT device tracker to "home"

Finally create a file called "presence.yaml" in the apps directory and add the following:

```yaml
ble_tracker_app:
  module: presence
  class: BleDeviceTrackerUpdater
```
This will create an app called "ble_tracker_app" using the presence module we just created.

At the end of all this we should now have for each person a device tracker that shows whether the person is home or not and a sensor that shows in which room the person is in case the person is home.

</p>
</details>

### GPS Device Tracker - Presence Outside Home
#### Hardware used
<table align="center" border="0">

<tr><td align="center" colspan="1">
2x Samsung Galaxy S20
</td></tr>

<tr><td align="center" colspan="1">
<img src="git-pictures/device_pictures/galaxy_s20.jpg" raw=true height="250" alt="Galaxy S 20" style="margin-right: 10px;"/>
</td></tr>

<tr><td colspan="1">
      We use the official <a href="https://companion.home-assistant.io/">Home Assistant Companion app</a> on our phones. In order to connect remotely to Home Assistant, we use <a href="https://www.nabucasa.com/">Nabu Casa</a> (I actually use NGINX as a reverse proxy in my production environment and I'll eventually explain this setup at a later stage).
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

#### Creating Additional Users
I have one user per device that access Home Assistant in order to serve different frontends based on the used device. To create an additional user click on "Configuration" in the sidebar of Home Assistant and then click on "Users". Press the orange plus sign at the bottom right. Enter the name of the person and press "CREATE". Enter the Name (name shown in the frontend), Username (name used to login) and a Password. Toggle if the user should be in the Administrator group or not.

#### Remote Access Setup (Nabu Casa)
Setup Nabu Casa by following the official instructions [here](https://www.nabucasa.com/config/) and [here](https://www.nabucasa.com/config/remote/). Home Assistant should now be accessible outside the network through the address that has been generated in the setup of Nabu Casa, e.g. https://abcdefghijklmnopqrstuvwxyz.ui.nabu.casa


#### Configure separate internal and external URL
UPDATE: Since version 0.110.x an internal and extenal url can be configured separately. This allows for easier configuration for certain more complex integrations.
##### Configure via UI
First enable "advanced mode" by clicking on your username in the sidebar. Toggle the setting "Advanced Mode".
Now go to "Configuration" then to "General". Enter the internal and external url respectively e.g.

```
Internal URL: http://192.168.0.30:8123
External URL: https://abcdefghijklmnopqrstuvwxzy.ui.nabu.casa
```

##### Configure via configuration files
Add the following to the file "core.yaml":

```yaml
homeassistant:
  internal_url: http://192.168.0.30.3123
  external_url: https://abcdefghijklmnopqrstuvwxzy.ui.nabu.casa
```

#### Phone App Setup
Add the following to persons.yaml to enable the [mobile_app integration](https://www.home-assistant.io/integrations/mobile_app/), which is needed to connect the phone app to Home Assistant.

```yaml
mobile_app:
```

Download and install the official Home Assistant Companion app. Give the app all the necessary permissions, like location etc. If you are connected to your home network, it should automatically detect your instance. Otherwise enter the Nabu Casa address from above manually. Login with the user credentials you created for this phone. In the app open the sidebar by swiping from the left edge to the right. Click on "App configuration". Enable the toggles for zone based and location based tracking. Optionally choose a name for the device (highly recommended as two phones of the same model will have the same name, but the second one has _2 appended). Restart Home Assistant.

You should now see a bunch of new entities, a device_tracker and some sensors such as battery_level and location (different depending on whether you use iOS or Android). When you are in the home zone (defined during onboarding process) the device_tracker shows "home", otherwise it shows "not_home" or the name of the zone (see next step) the phone is currently in.

#### Zone Setup
The [zone integration](https://www.home-assistant.io/integrations/zone/) is used to define different zones outside your home such as workplace or shopping mall. This way if the phone is inside the radius of one of the defined zones, the device tracker will show the name of this zone. This enables automations like "Send notification when Husband leaves work". 
To configure a zone go to the Sidebar in Home Assistant and click on "Configuration" and then click on "Zones". You should see a map with your home in a circle. To add a new zone, press the orange plus sign at the bottom right. Enter a name for the zone, move the pin to the desired location (or enter longitude and latitude) and choose a radius. Press create. Repeat for as many zones as needed.

</p>
</details>

### Customizing Entities
This does not belong to the presence detection system, it's more a general thing, however it's the first time during this journey that I use it, so I'll quickly explain it. 
I use the entity_id to identify my entities and the friendly_name for the name that should be shown in the frontend. 

I structure the name of my entities like this, domain.what_where or domain.what_owner. E.g. "switch.tv_livingroom", "sensor.temperature_kitchen", "sensor.battery_level_phone_dimitri". I do this for easier maintenance and consistency reasons.

You can [customize](https://www.home-assistant.io/docs/configuration/customizing-devices/) entities through the UI or through YAML. For lots of entites, especially similar entities, it's way easier and faster to do this through customization  in YAML. I use this for setting a friendly_name, icon, device_class and entity_picture where applicable. 

Here's my customization section for all entities that are part of the presence detection setup. I put this in the package persons.yaml:

```yaml
homeassistant:
  customize:
    zone.home:
      friendly_name: Zu Hause
      icon: mdi:home
    person.dimitri:
      friendly_name: Dimitri
      entity_picture: /local/person_pictures/dimitri_home.jpg
      icon: mdi:account
    sensor.battery_level_phone_dimitri:
      friendly_name: Handy Dimitri
    sensor.charging_phone_dimitri:
      friendly_name: Handy Dimitri
      icon: mdi:cellphone-charging
    device_tracker.gps_presence_dimitri:
      friendly_name: Standort Dimitri
      icon: mdi:map-marker
    device_tracker.room_presence_dimitri:
      friendly_name: Schlüssel Dimitri
      icon: mdi:key
    zone.work_dimitri:
      friendly_name: Arbeit
      icon: mdi:office-building
    person.sabrina:
      friendly_name: Sabrina
      entity_picture: /local/person_pictures/sabrina_home.jpg
      icon: mdi:account
    device_tracker.room_presence_sabrina:
      friendly_name: Schlüssel Sabrina
      icon: mdi:key
```

### Combining Device Trackers

#### Creating a Person
After the onboarding process Home Assistant will automatically create a person with the details you entered in the onboarding process.
To create an additional person, click on "Configuration" in the sidebar of Home Assistant and then click on "Persons". Press the orange plus sign at the bottom right. Enter the name of the person and press "CREATE".

#### Binding Device Trackers to Persons
To bind a device tracker to a person, click on "Configuration" in the sidebar of Home Assistant and then click on "Persons". Click on the person you want to assign the device trackers to. In the field below "Select the devices that belong to this person" pick one of the device trackers, a second field to choose a device will appear, choose the second device tracker and then press "Update" in the bottom right.

### Make Presence Detection not so binary (AppDaemon)
This is based on a method of Phil Hawthorne, more details can be found in his tutorial [Making Home Assistant's Presence Detection not so Binary](https://philhawthorne.com/making-home-assistants-presence-detection-not-so-binary/). At the end of this part the state of the person entities is going to have the states "just left", "away" "extended away", "just arrived" and "home", instead of just "home" and "not_home". Like this we can avoid an arriving home automation getting triggered, when a person just left quickly for getting some bread at the bakery.

<details><summary>Step-by-step Guide</summary>
<p>

The non binary presence app sets the state of the person to "just_left", "just_arrived", "home", "away" or "extended away" based on the room persons home state. 

Add another class in the "presence.py" file:

```python
class NonBinaryPresence(AppBase):
    """Define a base class for non binary person presence."""

    def configure(self) -> None:
        """Configure."""
        persons = self.adbase.get_state("person")

        for person in persons.keys():
            # away/extended away -> just arrived
            self.adbase.listen_state(
                self.on_presence_change,
                person,
                attribute="home",
                new=1,
                non_binary_state="just_arrived",
            )

            # home -> just left
            self.adbase.listen_state(
                self.on_presence_change,
                person,
                attribute="home",
                new=0,
                non_binary_state="just_left",
            )

            # just arrived -> home, after 5 min
            self.adbase.listen_state(
                self.on_presence_change,
                person,
                attribute="non_binary_presence",
                new="just_arrived",
                duration=5 * 60,
                non_binary_state="home",
            )

            # just left -> away, after 5 min
            self.adbase.listen_state(
                self.on_presence_change,
                person,
                attribute="non_binary_presence",
                new="just_left",
                duration=5 * 60,
                non_binary_state="away",
            )

            # away -> extended away, after 24 hours
            self.adbase.listen_state(
                self.on_presence_change,
                person,
                attribute="non_binary_presence",
                new="away",
                duration=24 * 60 * 60,
                non_binary_state="extended_away",
            )

    def on_presence_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when person changes presence state."""
        # just left -> just arrived = home
        if old == "just_left" and new == "just_arrived":
            non_binary_state = "home"
        else:
            non_binary_state = kwargs["non_binary_state"]

        # Set non binary presence state for person
        self.adbase.set_state(entity, non_binary_presence=non_binary_state)
        self.adbase.log(
            f"{entity.split('.')[1].capitalize()}: {non_binary_state.replace('_',' ')}"
        )
```

In the corresponding configuration file called "presence.yaml" and add the following:

```yaml
non_binary_presence_app:
  module: presence
  class: NonBinaryPresence
```

The house presence app sets the state of the house to "someone_home", "nobody_home", "everyone_home" or "vacation" based on the persons peresence state.

Add another class in the "presence.py" file:

```python
class HousePresence(AppBase):
    """Define a base class for house presence."""

    APP_SCHEMA = APP_SCHEMA.extend({vol.Required("house_id"): str})

    def configure(self) -> None:
        """Configure."""
        house_id = self.args["house_id"]
        self.house_entity_id = f"house.{house_id}"
        persons = self.adbase.get_state("person")

        # Listen for person changing home state
        for person in persons.keys():
            self.adbase.listen_state(self.on_presence_change, person, attribute="home")

    def on_presence_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when person changes presence state."""
        person_id = entity.split(".")[1]
        persons = self.adbase.get_state("person")
        
        persons_home = self.adbase.get_state(self.house_entity_id, attribute="persons")
        persons_extended_away = [
            person
            for person, attributes in persons.items()
            if attributes["attributes"]["non_binary_presence"] == "extended_away"
        ]

        # Add/remove person from the house
        if new == True:
            persons_home.append(person_id)
        elif person_id in persons_home:
            persons_home.remove(person_id)

        # Set occupancy of the house
        if not persons_home:
            occupied = False
        else:
            occupied = True

        # Set presence state of the house
        if len(persons.keys()) == len(persons_home):
            presence_state = "everyone_home"
        elif len(persons.keys()) == len(persons_extended_away):
            presence_state = "vacation"
        elif not persons_home:
            presence_state = "nobody_home"
        else:
            presence_state = "someone_home"

        self.adbase.set_state(
            self.house_entity_id,
            presence_state=presence_state,
            occupied=occupied,
            persons=persons_home,
        )
        self.adbase.log(f"House Presence: {presence_state.replace('_',' ')}")

```

In the corresponding configuration file called "presence.yaml" and add the following:

```yaml
house_presence_app:
  module: presence
  class: HousePresence
  house_id: home
```

Where "house_id" is the id you configured in the house app previously.

Now the the state of the persons non-binary presence and the presence state of the house will behave as follows:

**Person Presence Input Selects:**
* Person entity changes to home
    * old non-binary state = "just left" -> non-binary presence state = "home" (this avoids retriggering just arrived automations when the person just left quickly, in this example less than 5 minutes)
    * old non-binary state != "just left" -> non-binary presence state = "just arrived"
* Person entity changes from "home" to anything else-> non-binary presence state = "just left"
* Non-binary presence state = "just arrived" for 5 minutes -> non-binary presence state = "home"
* Non-binary presence state = "just left" for 5 minutes -> non-binary presence state = "away"
* Non-binary presence state = "away" for 24 hours -> non-binary presence state = "extended "away"

**House Presence Input Selects:**
* At least one persons' non-binary presence state = "home" or "just arrived"
    * All -> house presence state = "everyone home"
    * At least one but not all -> house presence state = "someone home"
* All persons' non-binary presence state neither "home" nor just arrived -> house presence state = "noone home"
* All persons' non-binary presence state = "extended away" -> house presence state = "vacation"

</p>
</details>

### Room Occupancy (AppDaemon)
This app combines different factors to determine the occupancy of the room. I use this to turn off lights/devices once a room is not occupied anymore. A motion sensor alone is not sufficient, as it fails to detect motion when sitting/lying still. The app checks the persons in the room, whether motion has been detected (this is set by the motion light app later on) and whether any of the specified "occupancy" entities is "on". I still use the motion detector to turn the lights on because if I stay in the hallway close to a room, sometimes the room sensor shows me inside the room, even though I might just be standing there playing with the dog or whatever and then I don't want the lights to turn on. 

<details><summary>Step-by-step Guide</summary>
<p>

Extend the "area.py" file to look like this:

```python
"""Define automations for areas."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv


class Area(AppBase):
    """Representation of an Area."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("area"): str,
            vol.Optional("attributes"): vol.Schema(
                {vol.Optional("friendly_name"): str}
            ),
            vol.Optional("occupancy"): vol.Schema(
                {vol.Optional(cv.entity_id): str}
            ),
        }
    )

    def configure(self) -> None:
        """Configure an area."""
        areas = self.adbase.get_state("area")
        area = self.args["area"]
        area_id = area.lower().replace(" ", "_")
        attributes = self.args["attributes"]
        self.area_entity = f"area.{area_id}"

        # Create an entity for the area if it doesn't already exist
        if self.area_entity not in areas.keys():
            if "friendly_name" not in attributes:
                attributes.update({"friendly_name": area.title()})

            attributes.update(
                {"id": area_id, "persons": [], "occupied": None, "occupancy": {}}
            )

            self.adbase.set_state(self.area_entity, state="idle", attributes=attributes)

        # Listen for no changes in area state for 30 seconds
        self.adbase.listen_state(self.on_state_change, self.area_entity, duration=30)

        # Listen for changes in occupancy entities of area
        if "occupancy_entities" in self.args:
            occupancy_entities = self.args.get("occupancy_entities")
            for entity, state in occupancy_entities.items():
                self.hass.listen_state(
                    self.on_occupancy_entity_change,
                    entity,
                    occupied_state=state,
                )

        # Listen for changes in occupancy of area
        self.adbase.listen_state(
            self.on_occupancy_change, self.area_entity, attribute="occupancy"
        )

        # Listen for changes in persons in area
        self.adbase.listen_state(
            self.on_occupancy_change, self.area_entity, attribute="persons"
        )

    def on_state_change(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when area doesn't change state for 30s."""
        # Set area to idle
        self.adbase.set_state(entity, state="idle")

    def on_occupancy_entity_change(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None: 
        """Respond when occupancy factor changes."""
        occupied_state = kwargs["occupied_state"]
        # Determine occupancy state of entity
        occupancy = self.adbase.get_state(self.area_entity, attribute="occupancy")
        if new == occupied_state:
            occupancy[entity] = True
        else:
            occupancy[entity] = False
        
        # Set state of occupancy entity
        self.adbase.set_state(self.area_entity, occupancy=occupancy)
        
    def on_occupancy_change(
        self, entity: str, attribute: dict, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when occupancy factor changes."""
        occupied = self.is_occupied(entity)
        # Set occupancy of area
        self.adbase.set_state(entity, occupied=occupied)
        self.adbase.log(f"{entity.split('.')[1].capitalize()} Occupied: {occupied}")

    def is_occupied(self, area: str) -> bool:
        """Return occupancy of given area."""
        """Return True if area is occupied."""
        # Get state of occupancy entities
        area_attr = self.adbase.get_state(area, attribute="attributes")
        occupancy = area_attr["occupancy"]
        # Check if persons in area
        persons = len(area_attr["persons"]) > 0
        return persons or any(value == True for key, value in occupancy.items())
```

You can now add entities and their corresponding "on" state in the config for an area. These will then be included when determining the occupancy of the room.

E.g. I want the area to be occupied when the TV (switch.tv_office) in the office is on.
So I add the following to the area config for the office:

```yaml
  occupancy_entities:
    switch.tv_office: "on"
```

The complete office area config then looks like this:

```yaml
office:
  module: area
  class: Area
  area: office
  attributes:
    friendly_name: Büro
  occupancy_entities:
    switch.tv_office: "on"
```

</p>
</details>


## Bed Occupancy <a name="bed-occupancy" href="https://github.com/Burningstone91/smart-home-setup#bed-occupancy"></a>

### Basic Explanation of Setup

I used the following awesome guide [5$ Can Get You a Smart Bed](https://medium.com/the-smarter-home/smart-bed-7de9ad55276e) to create a sensor for our bed. This sensor is then used to set the "bed" state of the persons and the house.

### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:50%;">
NodeMCU ESP32
</td>
<td align="center" style="width:50%;">
4x DIY "pressure" mats
</td>
</tr>

<tr>
<td align="center" style="width:50%;">
<img src="git-pictures/device_pictures/esp32.jpg" raw=true height="100" alt="ESP32" />
</td>
<td align="center" style="width:50%;">
<img src="git-pictures/device_pictures/pressure_mats.jpg" raw=true height="100" alt="Pressure Mats" />
</td>
</tr>

<tr><td colspan="5">
Two pressure mats are at the top and the bottom of "my" side of the bed and two pressure mats on her side of the bed.
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

### Build Sensor
Follow the instructions from the [guide](https://medium.com/the-smarter-home/smart-bed-7de9ad55276e). I adapted the ESPHome configuration to create 6 binary sensors, one for each pressure mat and one for each side of the bed. The two sensors for the sides of the bed are "on" when one or both of the pressure mat sensors are "on".

The final ESPHome config:

```yaml
esphome:
  name: bed_sensor_bedroom
  platform: ESP32
  board: nodemcu-32s

wifi:
  ssid: "NoT WiFi_2GHz"
  password: "wifi-password"
  use_address: 10.10.70.22
  ap:
    ssid: "Bed Sensor Bedroom"
    password: "fallback-ap-password"

captive_portal:

logger:

api:
  password: "api-password"

ota:
  password: "ota-password"

esp32_touch:

binary_sensor:
   - platform: esp32_touch
     name: "Bed top Dimitri"
     pin: GPIO12
     threshold: 5
     id: bed_top_dimitri
   - platform: esp32_touch
     name: "Bed bottom Dimitri"
     pin: GPIO4
     threshold: 4
     id: bed_bottom_dimitri
   - platform: template
     id: bed_dimitri
     name: "Bed Dimitri"
     lambda: |-
       if (id(bed_top_dimitri).state ||
           id(bed_bottom_dimitri).state) {
         return true;
       } else {
         return false;
       }
   - platform: esp32_touch
     name: "Bett top Sabrina"
     pin: GPIO33
     threshold: 5
     id: bed_top_sabrina
   - platform: esp32_touch
     name: "Bed bottom Sabrina"
     pin: GPIO27
     threshold: 4
     id: bed_bottom_dimitri
   - platform: template
     id: bed_sabrina
     name: "Bed Sabrina"
     lambda: |-
       if (id(bed_top_sabrina).state ||
           id(bed_bottom_sabrina).state) {
         return true;
       } else {
         return false;
       }

```

### Configure Sensor into Home Assistant
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on the orange plus in the bottom right corner, search for "ESPHome" and click on it.
Enter the IP or hostname of the ESP32 Sensor in the field "host", "port" can be left as it is at 6053. Click "SUBMIT". Enter the password set in the section "api" of the ESPHome config file. Click "SUBMIT" again. You should now see the binary sensors configured on the ESP.

### Make Bed Occupancy not so binary (AppDaemon)
Same as the [not so binary presence detection](#make-presence-detection-not-so-binary-appdaemon) (just left, just arrived, home, etc.), we're going to create a not so binary bed occupancy state. The app sets the following states for the person entities' sleep state: "just laid down", "sleeping", "just got up", "awake", and "back to bed" for the "I quickly need to go to the toilet" situations. The app also sets the sleep state of the house entity to "somone in bed", "nobody in bed" and "everyone in bed".

Create a file called "sleep.py" and add the following:

```python
"""Define automations for Sleeping."""
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv


class Sleep(AppBase):
    """Defina a class for Sleep automations."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("house_id"): str,
            vol.Required("sensors"): vol.Schema({vol.Optional(str): cv.entity_id}),
        }
    )

    def configure(self) -> None:
        """Configure."""
        bed_sensors = self.args["sensors"]
        self.house_entity = f"house.{self.args['house_id']}"

        for person, sensor in bed_sensors.items():
            person_entity = f"person.{person}"
            # bed not occupied -> occupied
            self.hass.listen_state(
                self.on_sensor_change,
                sensor,
                new="on",
                person=person_entity,
                target_state="just_laid_down",
            )
            # bed occupied -> not occupied
            self.hass.listen_state(
                self.on_sensor_change,
                sensor,
                new="off",
                person=person_entity,
                target_state="just_got_up",
            )
            # just got up -> just laid down = back_to_bed
            self.adbase.listen_state(
                self.on_person_change,
                person_entity,
                attribute="sleep_state",
                old="just_got_up",
                new="just_laid_down",
                target_state="back_to_bed",
            )
            # just laid down -> sleeping, after 5 min
            self.adbase.listen_state(
                self.on_person_change,
                person_entity,
                attribute="sleep_state",
                new="just_laid_down",
                duration=5 * 60,
                target_state="sleeping",
            )
            # back to bed -> sleeping, after 5 min
            self.adbase.listen_state(
                self.on_person_change,
                person_entity,
                attribute="sleep_state",
                new="back_to_bed",
                duration=5 * 60,
                target_state="sleeping",
            )
            # just got up -> awake, after 5 min
            self.adbase.listen_state(
                self.on_person_change,
                person_entity,
                attribute="sleep_state",
                new="just_got_up",
                duration=5 * 60,
                target_state="awake",
            )
            # Listen to changes in persons' sleep state
            self.adbase.listen_state(
                self.on_person_change_house, person_entity, attribute="sleep_state"
            )

    def on_sensor_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when bed occupancy sensor changes state."""
        if new != old:
            # Set sleep state for person
            person = kwargs["person"]
            old_state = self.adbase.get_state(person, attribute="sleep_state")
            target_state = kwargs["target_state"]

            if old_state == "just_got_up" and target_state == "just_laid_down":
                target_state = "back_to_bed"

            self.adbase.set_state(person, sleep_state=target_state)
            self.adbase.log(
                f"{person.split('.')[1].capitalize()}: {target_state.replace('_',' ')}"
            )

    def on_person_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when person changes sleep state."""
        if new != old:
            # Set sleep state for person
            target_state = kwargs["target_state"]
            self.adbase.set_state(entity, sleep_state=target_state)
            self.adbase.log(
                f"{entity.split('.')[1].capitalize()}: {target_state.replace('_',' ')}"
            )

    def on_person_change_house(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Update the sleep state of the house."""
        persons_home = self.adbase.get_state(self.house_entity, attribute="persons")
        old_state = self.adbase.get_state(self.house_entity, attribute="sleep_state")
        if set(persons_home) == set(self.persons_in_bed()):
            target_state = "everyone_in_bed"
        elif self.persons_in_bed():
            target_state = "someone_in_bed"
        else:
            target_state = "nobody_in_bed"
        if old_state != target_state:
            self.adbase.set_state(self.house_entity, sleep_state=target_state)
            self.adbase.log(f"House Sleep State: {target_state.replace('_', ' ')}")

    def who_in_state(self, *states) -> list:
        """Return list of persons in given states."""
        persons = self.adbase.get_state("person")
        return [
            attributes["attributes"]["id"]
            for attributes in persons.values()
            if attributes["attributes"]["sleep_state"] in states
        ]

    def persons_in_bed(self) -> list:
        """Return list of persons in bed."""
        return self.who_in_state(
            "just_got_up" "just_laid_down", "back_to_bed", "sleeping"
        )

```

Create a corresponding configuration file called "sleep.yaml" and add the following:

```yaml
room_presence_app:
  module: sleep
  class: Sleep
  sensors:
    dimitri: binary_sensor.bed_dimitri
    sabrina: binary_sensor.bed_sabrina
```

In the sensors section put the person_id (configured in the person app) and the corresponding bed occupancy sensor from the previous step.

These sleep states are going to be used later in other automations, e.g. lighting control, sleep/wakeup scenes etc.

</p>
</details>

## ZigBee(deCONZ) / Z-Wave(OZW Daemon) <a name="zigbee-zwave" href="https://github.com/Burningstone91/smart-home-setup#zigbee-zwave"></a>

### Hardware used
<table align="center" border="0">

<tr>
<td align="center" style="width:33%;">
Raspberry Pi 3
</td>
<td align="center" style="width:33%;">
ConBee II
</td>
<td align="center" style="width:34%;">
Aeotec Z-Stick Gen 5
</td>
</tr>

<tr>
<td align="center" style="width:33%;">
<img src="git-pictures/device_pictures/pi_3.jpg" raw=true height="250" alt="Pi 3"/>
</td>
<td align="center" style="width:33%;">
<img src="git-pictures/device_pictures/conbee_stick.jpg" raw=true height="250" alt="ConBee" />
</td>
<td align="center" style="width:34%;">
<img src="git-pictures/device_pictures/aeotec_stick.jpg" raw=true height="250" alt="Philips Hue" />
</td>

</tr>

<tr><td colspan="3">
All ZigBee devices are integrated into Home Assistant through a ConBee II ZigBee stick together with the software [DeCONZ](https://phoscon.de/en/conbee/install). I ditched the Hue hub (have lots of hue lights and dimmer switches) because the Home Assistant integration needs to poll the state from the Hue hub, whereas with the ConBee stick information is pushed to Home Assistant. This means that e.g. button presses from Hue Dimmer Switches will be seen immediately and each button press is recognized. With polling it can happen that button presses are missed because the button has been pressed multiple times between the polling interval. In addition to this, I can integrate (and I will later) lots of other ZigBee devices such as Xiaomi door sensors or the Ikea plug when using the ConBee stick.
The Z-Wave devices are integrated into Home Assistant through an Aeotec Z-Stick Gen 5 with the software [OZWDaemon](https://github.com/OpenZWave/qt-openzwave). 
My Home Assistant server is in the office and can't reach some ZigBee/Z-Wave devices, that's why I attached both sticks to a separate Pi 3 and put the Pi in a better location. This has an added bonus, the ZigBee and Z-Wave network don't need to be restarted whenever I restart Home Assistant. The ZigBee stick communicates through a websocket connection and the OZWDaemon through MQTT.
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>


### Setup ZigBee Hub (ConBee II)
The ConBee II stick is attached to a separate Raspberry Pi 3 in the living room, because the server lives in a place with a very limited range to reach other ZigBee devices. We are going to install a software called [DeCONZ](https://phoscon.de/en/conbee/install) from the company [Dresden Elektronik](https://www.dresden-elektronik.de/) inside a docker container. 
Install Raspbian Lite on the Raspberry Pi.

Give user access to serial devices to controll the ConBee II stick:

```bash
sudo usermod -aG dialout pi
restart
```

Now we are going to create a Symlink for the stick, this way it doesn't matter when the device changes the device path (/dev/ttyACM0 instead of /dev/ttyACM1) due to detaching and reattaching the stick or when we add another stick.

Get the product and vendor id of the stick by listing all usb devices:

```bash
lsusb
```

Note the 8 digit number of the stick e.g. 0658:0200

create a file "99-usb-serial.rules" in the folder /etc/udev/rules.d

```bash
sudo nano /etc/udev/rules.d/99-usb-serial.rules
```

Add the following content, where ABCD is the first 4 digits of the previously noted number and 1234 is the last 4 digits.

```bash
SUBSYSTEM=="tty", ATTRS{idVendor}=="ABCD", ATTRS{idProduct}=="1234", SYMLINK+="zigbee"
```

Restart.

Now the stick is available under /dev/zigbee.

Install docker and docker-compose:

Docker:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi
rm get-docker.sh
```

Docker-compose:
```bash
sudo apt-get install -y python python-pip
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
sudo apt-get install -y libffi-dev libssl-dev
sudo apt-get remove python-configparser
sudo pip3 install docker-compose
```

Create docker-compose.yml file and directory deconz to store the config:

Create docker-compose.yml file:

```bash
sudo nano docker-compose.yml
```

Add the following content:

```yaml
version: "3"
services:
  deconz:
    container_name: deconz
    devices:
      - /dev/zigbee
    environment:
      - DECONZ_WEB_PORT=8080
      - DECONZ_WS_PORT=443
      - DECONZ_VNC_MODE=1
      - DECONZ_VNC_PORT=5900
      - DECONZ_VNC_PASSWORD=yoursupersecretpassword
      - DECONZ_DEVICE=/dev/zigbee
      - TZ=Europe/Zurich
    image: marthoc/deconz
    network_mode: host
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./deconz:/root/.local/share/dresden-elektronik/deCONZ
```

Start the docker stack as a background daemon:

```bash
docker-compose up -d
```

This way you can view the ZigBee mesh through VNC on port 5900 and with the password you set in DECONZ_VNC_PASSWORD. The Web Portal (Phoscon) and the REST API (which will be used to connect to Home Assistant) are available under port 8080.

### Configure deCONZ integration in Home Assistant
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on the orange plus in the bottom right corner, search for "deconz" and click on it.
Choose "Manually define gateway".
Enter the ip of the Pi in the field "host" and in the field port enter "8080".
Hit "Submit".
In another browser tab go to http://ip-of-your-pi:8080/pwa in the sidebar go to Settings -> Gateway. Click on "Advanced" at the bottom. Hit the "Authenticate App" button. Go back to Home Assistant and press "Submit" again. Now all your devices that you connected to the ConBee II stick should show up in Home Assistant.

### Setup Z-Wave Hub (Aeotec Z-Stick Gen 5)
The Aeotec stick is attached to the same Raspberry Pi 3 as the ConBee II. We are going to install a software called [OZWDaemon](https://github.com/OpenZWave/qt-openzwave) inside a docker container. The OZWDaemon acts as a Z-Wave to MQTT bridge. This means that MQTT must be running somewhere on your network and in order to use the devices with Home Assistant the MQTT must be configured inside Home Assistant. If you followed this guide from the beginning you covered this already. 

To use the Aeotec stick with the Pi, create an additional Symlink for the stick, the same way as described above and name the symlink "zwave".

Restart.

Now the stick is available under /dev/zwave.


Add the following content to the docker-compose.yml file:

```yaml
version: "3"
services:
  ozwdaemon:
    container_name: ozwdaemon
    devices:
      - /dev/zwave
    environment:
      MQTT_SERVER: ip-of-home-assistant-machine
      MQTT_PORT: 1883
      MQTT_USERNAME: mqtt_username
      MQTT_PASSWORD: your-secret-mqtt-password
      USB_PATH: /dev/zwave
    image: openzwave/ozwdaemon:allinone-latest
    network_mode: host
    restart: unless-stopped
    security_opt:
      - seccomp:unconfined
    volumes:
      - ./ozwdaemon:/opt/ozw/config

```

Start the docker stack as a background daemon:

```bash
docker-compose up -d
```

This will enable the ozw-admin through port 1983, VNC Server through port 5900 and HTML VNC Client through port 7800.

This will 
You can add the following to the environment variables if you want to include devices securely:

```yaml
OZW_NETWORK_KEY: "network_key"
```
If you already paired devices securely to your Aeotec stick, put the network key you used to configure the stick in the past.

### Configure OpenZWave integration in Home Assistant
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on the orange plus in the bottom right corner, search for "openzwave" and click on "OpenZWave (Beta).
Hit "Submit".

If you already had devices paired to the Aeotec stick previously your devices should appear under "Configuration" -> "Integrations" -> "OpenZWave (Beta)". 

To add devices, access the web interface through http://ip-op-the-pi:7800. Click on "Open" in the top left corner. Press "Start" in the bottom box called "Remote OZWDaemon". Bring the device close to the Aeotec stick for pairing. Click on "Add Node" in the second line at the top. If you want to include the device securely, press "Yes" in the pop-up box, otherwise press "No". Put the device into pairing mode (For the Aeotec Multisensors I use press on the button at the back, for secure mode press twice extremly fast). Your device should appear under "Node List" if it was successful. Put the device into the final location and press "Heal Network". Check in Home Assistant if the devices appeared.

The web interface can also be used to change device specific configuration such as motion sensor sensitivity for the Aeotec Multisensor. There is also a service in home assistant (Developer Tools -> Services) called "ozw.set_config_parameter", which also enables changing device specific configuration.

</p>
</details>


## Lighting <a name="lighting" href="https://github.com/Burningstone91/smart-home-setup#lighting"></a>
### Basic Explanation of Setup

The lighting behaviour is determined by motion, occupancy and light level in the area, sleep state of the house and circadian rhythm. The details are explained in the section [Area Lighting (AppDaemon)](#area-lighting-appdaemon).

### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:20%;">
Philips Hue Bulbs (8x Color E27, 3x White Ambiance GU10, 1x LED strip 5m)
</td>
<td align="center" style="width:20%;">
1x IKEA Tradfri Plug
</td>
<td align="center" style="width:20%;">
1x Philips Hue Motion Sensor
</td>
<td align="center" style="width:20%;">
4x Aeotec Multisensor 6
</td>
<td align="center" style="width:20%;">
1x Xiaomi Lux Sensor
</td>
</tr>

<tr>
<td align="center" style="width:20%;">
<img src="git-pictures/device_pictures/philips_hue.jpg" raw=true height="100" alt="Philips Hue" />
</td>
<td align="center" style="width:20%;">
<img src="git-pictures/device_pictures/ikea_plug.jpg" raw=true height="100" alt="IKEA Plug" />
</td>
<td align="center" style="width:20%;">
<img src="git-pictures/device_pictures/hue_motion.jpg" raw=true height="100" alt="Hue Motion" />
</td>
<td align="center" style="width:20%;">
<img src="git-pictures/device_pictures/aeotec_multi.jpg" raw=true height="100" alt="Aeotec Multisensor" />
</td>
<td align="center" style="width:20%;">
<img src="git-pictures/device_pictures/xiaomi_lux.jpg" raw=true height="100" alt="Xiaomi Lux" />
</td>
</tr>

<tr><td colspan="5">
The Hue bulbs are distributed in the different rooms of our apartment and on the balcony is a light strip attached to an IKEA Tradfri Smart Plug. The motion and lux sensors are also placed around the house and are used to control lighting behaviour
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

### Adding light bulbs to the ZigBee network (Philips Hue)
The Phoscon Web UI should be available under http://ip-of-your-pi:8080/pwa. Initially you need to supply a username and a password. The process for adding Philips Hue bulbs, which were previously connected to a Hue hub is as follows:

* Delete bulb within the Hue hub.
* Cut the power to the bulb for 10 seconds.
* In Phoscon go to Devices -> Lights and press "Add new lights" at the bottom of the page.
* Take a Hue Dimmer Remote close to bulb and press and hold the "ON" and "Off" button for 10 seconds until the bulb starts to blink and the Hue Dimmer Remote shows a green light.
* The light should now show up in Phoscon.

### Creating groups in Phoscon
I create light groups in Phoscon. Each group defined in Phoscon will later show as a separate entity. This has a huge advantage over [Home Assistant Light Groups](https://www.home-assistant.io/integrations/light.group/) because if you send for example a command to turn off 5 lights in a light group that you configured in Home Assistant, it will one command for each bulb to the ConBee stick, which will in turn send 5 single commands to the ZigBee network. This can lead to delays and something called the "popcorn" effect, where lights turn on in random order. If you create a group in Phoscon, it will only send one command to the ZigBee network and all the lights will turn on/off at the same time. The disadvantage of Phoscon group is that you can't include lights/switches from other systems. You can still create a group in Home Assistant to do this and just include the group from Phoscon in there with the other devices that you want to control with this group.

### Adding motion sensors to the ZigBee network (Philips Hue)
Head over to the Phoscon Web UI under http://ip-of-your-pi:8080/pwa. And execute the following steps to integrate a Philips Hue motion sensor:

* Reset the device by pressing and holding the setup button (small holle at the back) for 10 seconds, the LED should blink orange
* In Phoscon go to Devices -> Sensors and press "Add new sensor" at the bottom of the page.
* The sensor should now show up in Phoscon.

### Adding motion sensors to the Z-Wave network (Aeotec Multisensor 6)
Head over to Home Assistant to and execute the following steps to integrate a Aeotec Multisensor 6:

* On the Sidebar click on "Developer Tools".
* At the top choose the tab "Services".
* In the field "Service" enter "ozw.add_node".
* Press the button on the back of the Aeotec Multisensor 6.
* The device should now show up under the OpenZWave (beta) integration.

### Adding lux sensors to the ZigBee network (Xiaomi)
Head over to the Phoscon Web UI under http://ip-of-your-pi:8080/pwa. And execute the following steps to integrate a Xiaomi Lux sensor:

* In Phoscon go to Devices -> Sensors and press "Add new sensor" at the bottom of the page.
* Choose "Other".
* Press and hold the button at the top of the sensor until the blue LED starts to blink.
* The sensor should now show up in Phoscon.

### Setup Circadian Lighting
I use the custom component [Circadian Ligting](https://github.com/claytonjn/hass-circadian_lighting) to calculate the brightness value for some lights. I mainly use it in the office when I'm working from home. The repo contains some explanations and articles about the benefits of Circadian Lighting. 

### Area Lighting (AppDaemon)
The area lighting app controls the lighting in the different areas based on conditions such as light levels, occupancy, etc.
The lights are turned on through motion and turned off through room occupancy. I didn't want to turn on lights on occupancy, as sometimes someone may be standing close to a room for a few seconds and make the room occupied, even though the person has no intention to enter the room.

The app consists of 3 parts, one for turning on the light on motion, one for adjusting the brightness of the lights to create a circadian rhythm and one for turning off the lights when everyone left the room.

Motion Detection:
Below is the flow for the motion detection part:

![Alt text](/git-pictures/flowcharts/motion_light_flow.jpg?raw=true "Motion Light Flow")

Adjust Brightness:
Brightness is adjusted to match circadian values at the specified interval. The automation is started whenever lights have turned on and stopped whenever lights have been turned off.

Room Occupancy:
When the occupancy of the area changes to "False", all the lights in the area are turned off. The Room Occupancy is determined by the [Room Occupancy App](#room-occupancy-appdaemon) from a previous step.

Now to the app. Add a file called "lighting.py" and add the following:

```python
"""Define automations for lighting."""
from color import color_temperature_to_rgb, color_temperature_kelvin_to_mired
from enum import Enum
from itertools import chain
from typing import Union, Tuple
import math
import voluptuous as vol

from appbase import AppBase, APP_SCHEMA
from utils import config_validation as cv


class AreaLighting(AppBase):
    """Define a class for Area Lighting."""

    APP_SCHEMA = APP_SCHEMA.extend(
        {
            vol.Required("area"): str,
            vol.Required("motion_sensors"): cv.entity_ids,
            vol.Optional("delay_off", default=600): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=3600)
            ),
            vol.Optional("lights"): cv.entity_ids,
            vol.Optional("lights_ct"): cv.entity_ids,
            vol.Optional("lights_rgb"): cv.entity_ids,
            vol.Optional("default_brightness", default=80): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("lux_sensor"): cv.entity_id,
            vol.Optional("lux_threshold", default=100): vol.Coerce(int),
            vol.Optional("sleep_lights"): cv.entity_ids,
            vol.Optional("sleep_lights_ct"): cv.entity_ids,
            vol.Optional("sleep_brightness"): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("circadian_sensor"): cv.entity_id,
            vol.Optional("min_brightness", default=1): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("max_brightness", default=100): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=100)
            ),
            vol.Optional("min_colortemp", default=2500): vol.All(
                vol.Coerce(int), vol.Range(min=1000, max=12000)
            ),
            vol.Optional("max_colortemp", default=5500): vol.All(
                vol.Coerce(int), vol.Range(min=1000, max=12000)
            ),
            vol.Optional("transition", default=60): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=3600)
            ),
            vol.Optional("update_interval", default=300): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=3600)
            ),
        }
    )

    def configure(self) -> None:
        """Configure."""
        self.area_id = self.args["area"]
        self.motion_sensors = self.args["motion_sensors"]
        self.delay_off = self.args.get("delay_off")
        self.lights = self.args.get("lights")
        self.lights_ct = self.args.get("lights_ct")
        self.lights_rgb = self.args.get("lights_rgb")
        self.default_brightness = self.args.get("default_brightness")
        self.lux_sensor = self.args.get("lux_sensor")
        self.lux_threshold = self.args.get("lux_threshold")
        self.sleep_lights = self.args.get("sleep_lights")
        self.sleep_lights_ct = self.args.get("sleep_lights_ct")
        self.sleep_brightness = self.args.get("sleep_brightness")
        self.circadian_sensor = self.args.get("circadian_sensor")
        self.min_brightness = self.args.get("min_brightness")
        self.max_brightness = self.args.get("max_brightness")
        self.min_colortemp = self.args.get("min_colortemp")
        self.max_colortemp = self.args.get("max_colortemp")
        self.transition = self.args.get("transition")
        self.update_interval = self.args.get("update_interval")

        # Build area entity and get friendly name
        self.area_entity = f"area.{self.area_id}"
        self.area_name = self.adbase.get_state(
            self.area_entity, attribute="friendly_name"
        )

        # Create a list of all lights in the area
        lights = [
            self.lights,
            self.lights_ct,
            self.lights_rgb,
            self.sleep_lights,
            self.sleep_lights_ct,
        ]
        lights = [light for light in lights if light]
        self.all_lights = set(chain(*lights))

        # Listen for motion detected
        for sensor in self.motion_sensors:
            self.hass.listen_state(self.on_motion, sensor, new="on")

        # Listen for changes in light state
        if self.circadian_sensor:
            for light in self.all_lights:
                self.hass.listen_state(self.on_light_change, light)

        # Listen for occupancy changes of area
        self.adbase.listen_state(
            self.on_occupancy_change, self.area_entity, attribute="occupied", new=False
        )

    def on_motion(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when motion is detected."""
        self.adbase.log(f"Motion detected: {self.area_name}")
        # Turn lights on if not already on
        if not self.lights_on():
            self.turn_lights_on()

        # Set motion state of room to True
        self.set_area_motion(True)

        # Start/Restart timer to turn motion state to False
        self.restart_motion_timer()

    def on_light_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when light changes state."""
        if new != old:
            if new == "on":
                if "circadian_timer" in self.handles:
                    self.adbase.cancel_timer(self.handles["circadian_timer"])
                    self.handles.pop("circadian_timer")
                self.handles["circadian_timer"] = self.adbase.run_every(
                    self.turn_lights_on,
                    f"now+{self.update_interval}",
                    self.update_interval,
                    transition=self.transition,
                )
            elif new == "off":
                if "motion_timer" in self.handles:
                    self.adbase.cancel_timer(self.handles["motion_timer"])
                    self.handles.pop("motion_timer")
                if "circadian_timer" in self.handles:
                    self.adbase.cancel_timer(self.handles["circadian_timer"])
                    self.handles.pop("circadian_timer")

    def on_occupancy_change(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Respond when occupancy of area changed to False."""
        for light in self.all_lights:
            self.hass.turn_off(light)

    def turn_lights_on(self, *args: list, **kwargs: dict) -> None:
        """Turn on lights."""
        if not self.lux_above_threshold():
            if self.is_sleep():
                lights = self.sleep_lights if self.sleep_lights else self.lights
                lights_ct = (
                    self.sleep_lights_ct if self.sleep_lights_ct else self.lights_ct
                )
            else:
                lights = self.lights
                lights_ct = self.lights_ct
                lights_rgb = self.lights_rgb

            brightness_pct = int(self.calc_brightness_pct())
            colortemp = int(self.calc_colortemp(brightness_pct))
            mired = color_temperature_kelvin_to_mired(colortemp)
            rgb = (
                tuple(map(int, self.calc_rgb(colortemp)))
                if self.lights_rgb is not None
                else None
            )

            transition = args[0]["transition"] if args else 0

            if lights is not None:
                for light in lights:
                    self.hass.turn_on(
                        light, brightness_pct=brightness_pct, transition=transition
                    )
            if lights_ct is not None:
                for light in lights_ct:
                    self.hass.turn_on(
                        light,
                        brightness_pct=brightness_pct,
                        color_temp=mired,
                        transition=transition,
                    )
            if lights_rgb is not None:
                for light in lights_rgb:
                    self.hass.turn_on(
                        light,
                        brightness_pct=brightness_pct,
                        color_temp=mired,
                        rgb_color=rgb,
                        transition=transition,
                    )

    def set_area_motion(self, motion: bool) -> None:
        """Set motion of area."""
        occupancy = self.adbase.get_state(self.area_entity, attribute="occupancy")
        occupancy["motion"] = motion
        self.adbase.set_state(self.area_entity, occupancy=occupancy)

    def restart_motion_timer(self) -> None:
        """Set/Reset timer to set occupany of are to False."""
        if "motion_timer" in self.handles:
            self.adbase.cancel_timer(self.handles["motion_timer"])
            self.handles.pop("motion_timer")
        self.handles["motion_timer"] = self.adbase.run_in(
            self.disable_area_motion, self.delay_off
        )

    def disable_area_motion(self, *args: list) -> None:
        """Set area motion to False."""
        self.set_area_motion(False)

    def calc_brightness_pct(self) -> float:
        """Calculate brightness percentage."""
        if self.is_sleep() and self.sleep_brightness:
            return self.sleep_brightness
        else:
            if self.circadian_sensor:
                brightness_pct = self.hass.get_state(self.circadian_sensor)
                if float(brightness_pct) > 0:
                    return self.max_brightness
                else:
                    return (
                        (self.max_brightness - self.min_brightness)
                        * ((100 + float(brightness_pct)) / 100)
                    ) + self.min_brightness
            else:
                return self.default_brightness

    def calc_colortemp(self, brightness_pct: float) -> float:
        if brightness_pct > 0:
            return (
                (self.max_colortemp - self.min_colortemp) * (brightness_pct / 100)
            ) + self.min_colortemp
        else:
            return self.min_colortemp

    def calc_rgb(self, colortemp: int) -> list:
        return color_temperature_to_rgb(colortemp)

    def lux_above_threshold(self) -> bool:
        """Return true if lux is above threshold."""
        if self.lux_sensor:
            value = float(self.hass.get_state(self.lux_sensor))
            return value > self.lux_threshold
        else:
            return False

    def lights_on(self) -> list:
        """Return lights currently on."""
        return [
            entity for entity in self.all_lights if self.hass.get_state(entity) == "on"
        ]

    def is_sleep(self) -> bool:
        """Return true if someone is asleep."""
        sleep_state = self.adbase.get_state(self.area_entity, attribute="sleep_state")
        return sleep_state != "nobody_in_bed"

```

Now add the configuration for the app to the individual area yaml files. 

The configuration parameters are as follows:

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | lighting | The module name of the app.
`class` | False | string | AreaLighting | The name of the Class.
`area` | False | string | | The identifier for the area.
`motion_sensors` | False | str, list | | List of motion sensor entity_ids.
`delay_off` | True | int | 600 | Time in seconds until motion is turned off.
`lights` | True | str, list | | List of light entity_ids for which only brightness should be set.
`lights_ct` | True | str, list | | List of light entity_ids for which brightness and color temperature should be set.
`lights_rgb` | True | str, list | | List of light entity_ids for which brightness, color temperature and RGB color should be set.
`default_brightness` | True | int | 80 | Brightness in % to set light to. Needed if circadian sensor is not used.
`lux_sensor` | True | str | | Entity_id of the light level sensor.
`lux_threshold` | True | int | 100 | Lux level below which light will not be turned on.
`sleep_lights` | True | str, list | | List of light entity_ids to be used in sleep mode for which only brightness should be adjusted.
`sleep_lights_ct` | True | str, list | | List of light entity_ids to be used in sleep mode for which brightness and color temperature should be adjusted.
`sleep_brightness` | True | int | | Brightness in % to be used in sleep mode. If not configured sleep mode will be ignored.
`circadian_sensor` | True | str | | Entity_id of the circadian lighting sensor. If not configured lights will be turned on to default brightness and no periodical adjustment will take place.
`max_brightness` | True | int | 100 | Maximum brightness in %. Used in conjunction with circadian sensor.
`min_brightness` | True | int | 1 | Minimum brightness in %. Used in conjunction with circadian sensor.
`max_colortemp` | True | int | 12000 | Maximum color temperature. Used in conjunction with circadian sensor.
`min_colortemp` | True | int | 1000 | Minimum color temperature. Used in conjunction with circadian sensor.
`transition` | True | int | 60 | Time in seconds for transition of light to new state. Used in conjunction with circadian sensor.
`update_interval` | True | int | 300 | Time in seconds between adjustments of brightness according to circadian lighting sensor.


Full example:

```yaml
bedroom_lights:
  module: lighting
  class: AreaLighting
  area: bedroom
  motion_sensors: binary_sensor.motion_bedroom
  delay_off: 600
  lights_rgb: light.bedroom_ceiling
  sleep_lights_ct: light.bedroom_bed
  sleep_brightness: 10
  circadian_sensor: sensor.circadian_values
  min_brightness: 10
  max_brightness: 80
  min_colortemp: 2000
  max_colortemp: 6500
  transition: 120
  update_interval: 900
```

</p>
</details>


