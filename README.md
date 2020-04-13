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

My "Server" is an Intel NUC with an i3-7100U CPU, 8 GB of RAM and a 1 TB SSD (I use it for other virtual machines as well). The Smart Home runs inside an Ubuntu virtual machine in Proxmox.

If you find any information here useful feel free to buy me a coffee :)

<a href="https://www.buymeacoff.ee/u89Ao5n" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee" style="height: 19px !important;width: 68px !important;" ></a>

## Overview
I will explain here the different parts of my home automation system and how I set them up. For each part, I will talk about the hardware involved and how I integrated it into the system and I will also give an explanation on the automations and the corresponding code related to this part. 

* <a href="https://github.com/Burningstone91/smart-home-setup#start">
      Start of my Journey and Basic Setup
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#mqtt">
      Setup of MQTT Broker
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#appdaemon">
      Setup AppDaemon - Automation Engine
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#presence-detection">
      Presence Detection
  </a>

## Start of my Jouney and Basic Setup <a name="start" href="https://github.com/Burningstone91/smart-home-setup#start"></a>

First some preparations and the install of [Home Assistant](https://www.home-assistant.io/), which will be the core of the home automation system.

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
    image: homeassistant/home-assistant:0.108.0
    network_mode: host
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - ./home-assistant:/config
```

### Start the docker stack for the first time
Enter the following command while you are in the same directory as the docker-compose.yml file:

```
docker-compose up -d
```

This will read the config from the docker-compose.yml file and start the docker stack in the background. This will take some time as it will now download and install Home Assistant Core.

After the install is finished, Home Assistant should be available under http://ip-of-host:8123

### Initial Home Assistant Configuration
Follow the instructions on the screen to setup the first user, your home location, elevation, time zone and unit system. 

### Structuring the Home Assistant configuration
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
Enter your username and password. Tick the box next to "Enable Discovery".

#### Configure via configuration files
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
[AppDaemon](https://appdaemon.readthedocs.io/en/latest/) can be used to write Home Automation apps for Home Assistant in Python. It's an alternative to Home Assistant's inbuilt automations. You can create more complicated automations and reuse the same code for multiple apps. The official AppDaemon documentation provides a [detailed explanation](https://appdaemon.readthedocs.io/en/latest/APPGUIDE.html) on how to create your first app.

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
        vol.Optional("manager"): str,
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

        # Create a reference to the manager app
        if self.args.get("manager"):
            self.manager = getattr(self, self.args["manager"])

        # Run the app configuration if specified
        if hasattr(self, "configure"):
            self.configure()
```
In addition create a folder called helpers and put a file called voluptuous_helper.py inside this folder with the following content:

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


class existing_entity_id(object):
    """Validate if a given object is an existing HA entity"""

    def __init__(self, hass):
        """Init."""
        self._hass = hass

    def __call__(self, value: Any) -> str:
        value = str(value).lower()
        if '.' not in value:
            raise vol.Invalid(f'Invalid entity-id: {value}')
        if not self._hass.entity_exists(value):
            raise vol.Invalid(f'Entity-id {value} does not exist')
        return value
```

Now when we create an app that usese the AppBase, it will automatically create a reference to every dependency in the app configuration. This way way we can use the methods and variables of the apps that our app depends on, to avoid redundant code. It will also do some basic config validation with Voluptuous and raise an error when you wrote "modle" instead of "module" for example. As we have multiple namespaces (HASS and MQTT), there are some variables that represent the MQTT and HASS namespace. This way you don't need to put "namespace=hass" when you call a method, instead you start the function call with "self.hass", if you want to do something in HASS namespace. Start it with "self.mqtt" to do something in MQTT namespace and start it with "self.adbase" do do something in the AppDaemon namespace (logging etc.).

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

<tr><td align="center" colspan="1">
Raspberry Pi Zero W
</td><td align="center" colspan="1">
Nut Mini
</td></tr>

<tr><td align="center" colspan="1"><a target="_blank"  href="https://www.amazon.de/gp/product/B072TN5KFN/ref=as_li_tl?ie=UTF8&camp=1638&creative=6742&creativeASIN=B072TN5KFN&linkCode=as2&tag=burningstone9-21&linkId=c90a64f7b56fce952882d81753e27a5b"><img border="0" src="//ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=DE&ASIN=B072TN5KFN&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL160_&tag=burningstone9-21" ></a><img src="//ir-de.amazon-adsystem.com/e/ir?t=burningstone9-21&l=am2&o=3&a=B072TN5KFN" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />
</td><td align="center" colspan="1"><a target="_blank"  href="https://www.amazon.de/gp/product/B07MFBL64S/ref=as_li_tl?ie=UTF8&camp=1638&creative=6742&creativeASIN=B07MFBL64S&linkCode=as2&tag=burningstone9-21&linkId=91360e22a9b0f592f54d7bccde154e4d"><img border="0" src="//ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=DE&ASIN=B07MFBL64S&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL160_&tag=burningstone9-21" ></a><img src="//ir-de.amazon-adsystem.com/e/ir?t=burningstone9-21&l=am2&o=3&a=B07MFBL64S" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />
</td></tr>

<tr><td colspan="2">
The Nut Mini's are attatched to our keys and I'm soon going to buy some Fitness Bands to replace them. They send a Bluetooth Low Energy (BLE) signal every 3 seconds. There's one Raspberry Pi's as central as possible in every room that I want to automate and one close to the entrance door. The Pi's run [Room Assistant](https://www.room-assistant.io/), which catches these signals and determines the location of the Nut Mini based on the strength of the signal. It talks to Home Assistant through MQTT and if discovery is enabled it will be detected automatically.
Due to the fact that only device tracker entities can be linked to a person, I use an AppDaemon app that updates the status of an MQTT device tracker whenever the state of the keys changes.
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

#### Creating a person
After the onboarding process Home Assistant will automatically create a person with the details you entered in the onboarding process.
To create an additional person click on "Configuration" in the sidebar of Home Assistant and then click on "Persons". Press the orange plus sign at the bottom right. Enter the name of the person and press "CREATE".

#### Room assistant Setup
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
          instanceName: balkon
  vars:
    room_assistant_global_config:
      global:
        integrations:
          - homeAssistant
          - bluetoothLowEnergy
      homeAssistant:
        mqttUrl: 'mqtt://ip-of-host:1883'
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
        mqttUrl: 'mqtt://10.10.40.6:1884'
        mqttOptions:
          username: mosquitto
          password: kCL5*RkP
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

#### MQTT device tracker
Because the sensor can not be used with the person integration, we use the[MQTT device tracker integration](https://www.home-assistant.io/integrations/device_tracker.mqtt/) and bind the resulting device tracker to the person integration. 

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

#### Device Tracker Update App
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

### GPS Device Tracker - Presence outside Home
