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
* <a href="https://github.com/Burningstone91/smart-home-setup#network-setup">
      Network Setup
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
* <a href="https://github.com/Burningstone91/smart-home-setup#switches">
      Switches
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#system-monitoring">
      System Monitoring
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#history-databases">
      History & Databases
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#climate">
      Climate
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#household-tasks">
      Household Tasks
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#security">
      Security
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#home-cinema">
      Home Cinema
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#multiroom-audio">
      Multiroom Audio
  </a>
* <a href="https://github.com/Burningstone91/smart-home-setup#applicances">
      Appliances
  </a>

## Start of my Jouney and Basic Setup <a name="start" href="https://github.com/Burningstone91/smart-home-setup#start"></a>

First some preparations and the install of [Home Assistant](https://www.home-assistant.io/), which will be the core of the home automation system.

### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:50%;">
Intel NUC
</td>
</tr>

<tr>
<td align="center" style="width:50%;">
<img src="git-pictures/device_pictures/nuc.jpg" raw=true height="200" alt="NUC" />
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

## Network Setup <a name="mqtt" href="https://github.com/Burningstone91/smart-home-setup#network-setup"></a>

Below I explain how I use the Unifi Controller to configure VLANs to separate devices and firewall rules to control the traffic between the VLANs. 

![Alt text](/git-pictures/lovelace_views/network_diagram.png?raw=true "Network Diagram View")

<details><summary>Step-by-step Guide</summary>
<p>

### Install Unifi Controller

The Unifi Controller is used to configure the Unifi devices, to setup VLANs, configure firewall rules, etc.
The software can be installed on a variety of operating systems. There's also the Unifi Cloud Key which includes the software and can be attached directly to a switch. I installed the Unifi Controller on a VM running Ubuntu Server (which is also used for all my other networking stuff) following the below procedure.

1. Install required packages
```shell
sudo apt-get update && sudo apt-get install ca-certificates apt-transport-https
```

2. Add new source list
```shell
echo 'deb https://www.ui.com/downloads/unifi/debian stable ubiquiti' | sudo tee /etc/apt/sources.list.d/100-ubnt-unifi.list
```

3. Add trusted key
```shell
sudo wget -O /etc/apt/trusted.gpg.d/unifi-repo.gpg https://dl.ui.com/unifi/unifi-repo.gpg 
```

4. Install Java 8
```shell
sudo apt-get install openjdk-8-jre
```

5. Switch to Java 8
```shell
sudo update-alternatives --config java
```

choose number of java 8 and confirm with 
```shell
java -version
```

6. Install UniFi Controller
```shell
sudo apt-get update && sudo apt-get install unifi -y
```

7. Start UniFi Controller
```shell
sudo service unifi start
```

### VLANs what are they and why use them?

To separate devices into separate LANs, one can buy multiple switches etc. to physically separate the devices into different networks. However, this can become quite expensive and is also impractical for home use. The solution is Virtual Local Area Networks (VLANs). A VLAN can also separate devices into different networks, but it does so virtually, meaning you don't need to buy additional routers, switches, etc. to separate devices.

There are many use cases for VLANs, personally I use them to put devices into separate networks to easily manage, which devices are allowed to communicate with which devices. E.g. I don't want my Roomba vacuum cleaner to phone home to China or my Harmony Remote to make automatic updates, so I completely restrict access to the internet for the VLAN I put them in. Another example is to allow guests to use your WiFi for internet access, but restrict access to your home network.

### Setup VLANs in Unifi

Create a separate network for each VLAN you need. E.g. one for IoT stuff, one for private devices and one for servers.

1. In the Unifi Controller go to Settings -> Networks -> press "+ CREATE NEW NETWORK"
2. Choose any name you want for the network.
3. Choose "Corporate" (choose "Guest" for a guest network which doesn't have access to the other VLANs)
4. Enter an ID (1-4095) for your VLAN.
5. Define a Gateway IP/Subnet, I always use the VLAN ID to define the subnet. E.g. VLAN ID **80** -> Gateway IP/Subnet 10.10.**80**.1/24
6. Press "SAVE"
7. Repeat 1-6 for other VLANs.

Create a Wireless Network for each SSID. I created two sets of wireless networks, one for each Access Point. I do this so that devices can stick to one Access Point, by connecting it to the respective SSID. Without the separation, devices would roam between the Access Points, and some devices have trouble with roaming or lose connectivity shortly, which is not a desired behaviour for Home Automation devices. I also created separate 2GHz and 5GHz wireless networks for some of the networks. Lots of IoT devices work with 2GHz and some of them have a hard time connecting to a Dualband (2GHz/5GHz) network.

1. In the Unifi Controller go to Settings -> Wireless Networks -> press "+CREATE WIRELESS NETWORK"
2. Choose any name. This will also be the SSID that you'll see when you want to connect from a wireless client.
3. Choose a security level and enter a strong security key.
4. Choose the VLAN (created in the previous step) that this WLAN should be part of.
5. Choose which WiFi Band should be used.
6. Choose the AP Group (you need to create a separate group for each AP if you want to separate networks by AP) that should broadcast this network.
7. Press "SAVE"

Now connect the devices to the respective networks.
For wireless devices, connect to the SSID that is connected to the desired network.
For wired devices, in the Unifi Controller go to Devices and choose the Switch that the device is connected to. A menu pops up on the right. Press on the port that the device is connected to, then edit the port by pressing the small pencil. Under "Switch Port Profile" choose the desired network, then press "Apply" in the bottom right.

### Put NAS in multiple VLANs

I put my Main NAS (Synology DS920+) that is used as a media server for multiple devices from different VLANs (private VLAN, entertainment VLAN, etc.) into multiple VLANs. If it would be only in one VLAN, then all the traffic from a device in a different VLAN would need to be routed through the USG 3 Router, put an unecessary burden on the little thing and reduce transfer speeds, which negatively effects media playback. I restrict access to the different data on the NAS side.

Create VLAN interface on the Synology NAS:

1. Configure first VLAN
Login to the Synology UI -> Control Panel -> Network and edit the interface. Configure it for one of the needed VLANs (e.g. VLAN 10).
2. Additional VLAN
2.1. SSH into NAS then change to the network-scripts directory:
	```shell
	cd /etc/sysconfig/network-scripts
	```
	2.2. Copy one of the existing VLAN (e.g. VLAN 10) configs `ifcfg-bond0.x` or `ifcfg-eth0.x`, e.g. for VLAN 30
	```shell
	sudo cp ifcfg-bond0.10 ifcfg-bond0.30
	```

	2.3. Edit file and change DEVICE, VLAN_ID and IPADDR accordingly, e.g.
	```shell
	sudo vi ifcfg-eth0.30
	```
	```shell
	DEVICE=eth0.30
	VLAN_ROW_DEVICE=eth0
	VLAN_ID=30
	ONBOOT=yes
	BOOTPROTO=static
	IPADDR=10.10.30.15
	NETMASK=255.255.255.0
	IPV6INIT=off
	```
3. Reboot the NAS

On the Unifi side you need to set up a new port profile group under Settings -> Profiles and then choose SWITCH PORTS at the top and press "+ADD NEW PORT PROFILE".

Choose a name for this profile, e.g. NAS VLANs. Choose "None" for the Native Network and choose all the VLANs that the NAS should be part of. Press "SAVE". Now go to Devices and choose the Switch that the device is connected to. A menu pops up on the right. Press on the port that the device is connected to, then edit the port by pressing the small pencil. Under "Switch Port Profile" choose the newly created port profile, then press "Apply" in the bottom right.

### DNS Server (Pi-hole)

I use [Pi-hole](https://pi-hole.net/) as my DNS Server, this way I can block ads and also easily setup local DNS entries to e.g. not route the traffic from the internal network through the internet when accessing the services I exposed remotely (e.g. Home Assistant or my Book Library) with their remote address from a device that is connected to the home network currently. I run it on the same Ubuntu Server VM that also hosts the Unifi Controller.

1. Install Pi-hole
```shell
curl -sSL https://install.pi-hole.net | bash
```
2. Configure Network to use PiHole as DNS
In Unifi for each VLAN choose manual DHCP Name Server and enter the IP of the machine running Pi-hole.

### Firewall Rules

Unifi by default allows all VLANs to communicate with each other in both directions, except for networks configured as a "Guest" network. Guest networks are only allowed to connect to the Internet through your router, but not to other VLANs.

To restrict communication betwenn certain VLANs, block Internet access for some VLANs, etc. we need to setup firewall rules in the Unifi Controller.

Go to Settings -> Routing & Firewall -> Choose the "Firewall" tab at the top.

The order of the firewall rules is important. They are evaluated from top to bottom. This means you need to put rules that allow access at the top and rules that block access at the bottom, otherwise the blocking rule will be evaluated first and the allow rule is ignored, because it has already been decided what happens with the traffic.

#### Block access to the Internet for a VLAN
I use this to block devices from automatically updating or trying to phone home to China.

1. Choose the tab "WAN OUT" and press "+CREATE NEW RULE".
2. Give the rule a name, e.g. `Drop NoT to Internet`
3. Make sure Enabled is set to "ON".
4. Choose "Drop" for the Action.
5. Choose "All" for the IPv4 Protocol.
6. Under SOURCE choose "Network" as Source Type.
7. Under Network choose the VLAN for which access should be blocked.
8. Press "SAVE".

You should now not be able to access the Internet from a device connected to this VLAN.

#### Allow all VLANs access to Pi-hole (DNS Server)
All devices need to be able to make DNS requests to resolve IP addresses and I do this with Pi-hole, which has an Ad-Blocker built-in as well. To allow these requests create a rule as follows.

1. Choose the tab "LAN IN" and press "+CREATE NEW RULE".
2. Give the rule a name, e.g. `Allow all DNS requests to Pi-hole`
3. Make sure Enabled is set to "ON".
4. Choose "Accept" for the Action.
5. Choose "TCP and UDP" for the IPv4 Protocol.
6. Under Advanced choose "New", "Established" and "Related" in the States section.
7. Under SOURCE choose "Address/Port Group" as Source Type.
8. Under IPv4 Address Group press "CREATE IPV4 ADDRESS GROUP".
8.1. Choose a name for the group containing all your local IP address ranges.
8.2. Choose "Address IPv4" as Type.
8.3. Add the IP ranges of your VLANs, e.g. 10.10.90.0/24
9. Under DESTINATION choose "Address/Port Group" as Source Type.
10. Repeat the steps from point 7 to create a group for the machine running the DNS Server.
11. Under Port Group press "CREATE PORT GROUP".
11.1. Repeat steps from point 7, but choose "Port" as Type.
11.2. Enter 53 under Port.
12. Press "SAVE".

#### Block access for a VLAN to other VLANs
I configured on of these rules for each VLAN. So that the devices can only communicate within their VLAN or through any of the allow rules defined. 

1. Choose the tab "LAN IN" and press "+CREATE NEW RULE".
2. Give the rule a name, e.g. `Drop NoT to other VLANs`
3. Make sure Enabled is set to "ON".
4. Choose "Drop" for the Action.
5. Choose "All" for the IPv4 Protocol.
6. Under Advanced choose "New" and "Invalid" in the States section.
7. Under SOURCE choose "Network" as Source Type.
8. Choose the VLAN for which access to other VLANs should be blocked under Network.
9. Under DESTINATION choose "Address/Port Group" as Source Type.
10. Under IPv4 Address Group press "CREATE IPV4 ADDRESS GROUP".
10.1. Choose a name for the group containing all the IP address ranges of the VLANs to be blocked, e.g. `NoT Blocked VLAN`.
10.2. Choose "Address IPv4" as Type.
10.3. Add the IP ranges of the VLANs, e.g. 10.10.90.0/24
13. Press "SAVE".

These rules should explain the basic concept and you should be able to adapt them to your needs and add other rules.

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
```

Create a file called mosquitto.conf inside the config directory:

```
nano config/mosquitto.conf
```

and add the following to the file:


```
listener 1883

log_dest stdout

password_file /mosquitto/config/passwd
allow_anonymous false
```

Add the following to the docker-compose.yml to configure the Mosquitto docker container:
git 
```yaml
  mqtt:
    container_name: mqtt
    image: eclipse-mosquitto
    ports:
      - "1883:1883"
      - "9001:9001"
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - ./mosquitto/config/passwd:/mosquitto/config/passwd
```

Enter the following command to create a password file (replace USERNAME and PASSWORD with your respective details):

```
docker-compose run mqtt /bin/sh -c "touch /tmp/passwd && mosquitto_passwd -b /tmp/passwd USERNAME PASSWORD && cat /tmp/passwd && rm /tmp/passwd" > /mosquittoconfig/passwd

```

Download the image and run the container:

```
docker-compose up -d mqtt
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
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "MQTT" and click on it.
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

In addition create a folder called utils and put a file called config_validation.py inside this folder -> [config_validation.py](appdaemon/apps/utils/config_validation.py)

Now when we create an app that usese the AppBase, it will automatically create a reference to every dependency in the app configuration. This way way we can use the methods and variables of the apps that our app depends on, to avoid redundant code. It will also do some basic config validation with Voluptuous and raise an error when you wrote "modle" instead of "module" for example. As we have multiple namespaces (HASS and MQTT), there are some variables that represent the MQTT and HASS namespace. This way you don't need to put "namespace=hass" when you call a method, instead you start the function call with "self.hass", if you want to do something in HASS namespace. Start it with "self.mqtt" to do something in MQTT namespace and start it with "self.adbase" to do something in the AppDaemon namespace (logging etc.).

This file is going to be extended later on with more functionality.

</p>
</details>


## Presence Detection <a name="presence-detection" href="https://github.com/Burningstone91/smart-home-setup#presence-detection"></a>

### Basic Explanation of Setup
I use the [person integration](https://www.home-assistant.io/integrations/person/) from Home Assistant to combine a bluetooth device tracker (FitBit), a magnet attached to the keys in combination with a Xiaomi Door sensor (awesome idea I got from James Callaghan [Smart key hook](https://github.com/jcallaghan/home-assistant-config/issues/141) and a GPS device tracker (my phone). The docs give a detailed explanation on how the location is determined when multiple device trackers are used. Long story short, when I'm at home, my position is determined first by keys and the bluetooth device trackers and then by the GPS location of the phone. When I'm not home, my position is determined first by the GPS location of the phone, then by keys and the bluetooth device trackers.

I use the phone device tracker together with the [zone integration](https://www.home-assistant.io/integrations/zone/) from Home Assistant to show in which place (work, grocery store, etc.) we are, when we are not home. This is reflected in the state of the person.

And I use the bluetooth device tracker together with [Room Assistant](https://www.room-assistant.io/) to show in which room we are when we are home. This is not reflected in the state of the person.

I'm using the bluetooth device trackers now for around 2 years and I did not have a single false trigger in this time. Home Assistant marks us as home before we open the front door and marks us as left 3 min after we left the house.

I adapted the method from Phil Hawthorne for [making presence detection not so binary](https://philhawthorne.com/making-home-assistants-presence-detection-not-so-binary/). This is used for example when we leave the house and come back a few minutes later, that it will not trigger any arrival automations.

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
Due to the fact that only device tracker entities can be linked to a person, I use an automation that updates the status of an MQTT device tracker whenever the state of the keys changes.
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

#### MQTT Device Tracker
Because the only device trackers can be used with the person integration, we use the [MQTT device tracker integration](https://www.home-assistant.io/integrations/device_tracker.mqtt/) and bind the resulting device tracker to the person integration. 

To add an MQTT device tracker, create a file called "persons.yaml" in the folder "packages". This file will be used for all configuration related to persons.

Add the following to the file:

```yaml
device_tracker:
  - platform: mqtt
    devices:
      room_presence_dimitri: 'room_presence_device_tracker/him'
      room_presence_sabrina: 'room_presence_device_tracker/her'
      keys_dimitri: 'keys_device_tracker/him'
      keys_sabrina: 'keys_device_tracker/her'
    source_type: bluetooth_le
```

This will create four device trackers. The device tracker can be updated by publishing "home" or "not_home" to the respective MQTT topic

Restart Home Assistant. There should be four new device_trackers under "Developer Tools" -> "States".

#### Device Tracker Update Automation
We need one automation to update the device tracker for the keys and one automation to update the device tracker for the FitBits (Room Presence Tracker).

The automation to update the MQTT device tracker when the keys are attached/detached to/from the hook.

[Update Keys Device Tracker](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/persons.yaml#L59)

The second automation to update the device tracker for the room presence trackers.

[Update Room Presence Device Tracker](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/persons.yaml#L76)

This automation will mark the device as not home when the sensor shows "not_home" for 3 minutes and home otherwise. I added a condition that the previous state should not be the same as the new state, in order to avoid continuously send the home message when the distance attribute of the room presence sensor changes state.

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
I have one user per device that access Home Assistant in order to serve different frontends based on the used device. To create an additional user click on "Configuration" in the sidebar of Home Assistant and then click on "Users". Press the "+ ADD INTEGRATION" at the bottom right. Enter the name of the person and press "CREATE". Enter the Name (name shown in the frontend), Username (name used to login) and a Password. Toggle if the user should be in the Administrator group or not.

#### Remote Access Setup (Nabu Casa)
Setup Nabu Casa by following the official instructions [here](https://www.nabucasa.com/config/) and [here](https://www.nabucasa.com/config/remote/). Home Assistant should now be accessible outside the network through the address that has been generated in the setup of Nabu Casa, e.g. https://abcdefghijklmnopqrstuvwxyz.ui.nabu.casa

#### Remote Access Setup (NGINX Reverse Proxy)
I use a reverse proxy for Home Assistant, mainly because I also want to expose other services to the outside world without exposing any additional ports on my router. 

First you need to forward port 443 (HTTPS) (depending on the challenge you use for the SSL certificates, you may also need to temporarily forward port 80 to generate the certificates) from your router to the machine running NGINX (we're going to install NGINX as a docker container on the same host as Home Assistant). How you do this depends on your router.

Next install the [SWAG](https://hub.docker.com/r/linuxserver/swag) docker container, it includes NGINX (Reverse Proxy), Let's Encrypt (for SSL) and Fail2Ban. 

Create a folder called "swag", which later holds the configuration data for the container.
Get your GID and UID by issuing the following command on the host:

```bash
id yourusername
```
Add the follwoing to docker-compose.yaml:

```yaml
  swag:
    cap_add:
      - NET_ADMIN
    container_name: swag
    environment:
      - PUID=1000
      - PGID=1004
      - TZ=Europe/Zurich
      - URL=yourdomain.com
      - VALIDATION=http
      - EMAIL=yourmailaddress@blabla.com
    image: ghcr.io/linuxserver/swag
    ports:
      - "80:80"
      - "443:443"
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./swag:/config  
```

Replace the PUID and PGID values with the ones you got in the previous step. Replace `yourdomain.com` with your domain (I registered my own domain in combination with a DynamicDNS service from my ISP, but you can use DuckDNS or any other DynamicDNS provider) and replace `yourmailaddress@blabla.com` with your E-mail address.

Start the docker container:

```bash
docker-compose up -d
```

Some files should show up in the `swag` directory created before. Go to nginx -> site-confs and edit the file `default` to look like this:

```
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

# redirect all traffic to https
server {
	listen 80;
	server_name *.yourdomain.com;
	return 301 https://$host$request_uri;
}

############### Home Assistant ####################
server {
	listen 443 ssl default_server;

	server_name ha.yourdomain.com;

	# enable subfolder method reverse proxy confs
	include /config/nginx/proxy-confs/*.subfolder.conf;

	# all ssl related config moved to ssl.conf
	include /config/nginx/ssl.conf;

	proxy_buffering off;

	location / {
		proxy_set_header Host $host;
		proxy_redirect http:// https://;
		proxy_http_version 1.1;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "upgrade";
		proxy_pass http://ip-of-ha-instance:8123;
	}

}


# enable subdomain method reverse proxy confs
include /config/nginx/proxy-confs/*.subdomain.conf;
# enable proxy cache for auth
proxy_cache_path cache/ keys_zone=auth_cache:10m;
```

Replace `ha.yourdomain.com` with the subdomain that HA should be accessible from and `ip-of-ha-instance` with the IP of your Home Assistant instance. 

In Home Assistant add the following to configuration.yaml:

```yaml
http:
  use_x_forwarded_for: true
  trusted_proxies: 
    - 172.19.0.7
```
This is needed in order to show the correct IP-address when you get a notification about a failed login attempt. Without setting the reverse proxy as a trusted proxy, you'll always see the IP of the NGINX reverse proxy instead of the real IP address. 

You should now be able to access your Home Assistant instance remotely by going to https://ha.youromain.com and locally with http://ip-of-ha:8123.


#### Configure separate internal and external URL
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
To configure a zone go to the Sidebar in Home Assistant and click on "Configuration" and then click on "Zones". You should see a map with your home in a circle. To add a new zone, press the "+ ADD INTEGRATION" at the bottom right. Enter a name for the zone, move the pin to the desired location (or enter longitude and latitude) and choose a radius. Press create. Repeat for as many zones as needed.

</p>
</details>

### Customizing Entities
This does not belong to the presence detection system, it's more a general thing, however it's the first time during this journey that I use it, so I'll quickly explain it. 
I use the entity_id to identify my entities and the friendly_name for the name that should be shown in the frontend. 

I structure the name of my entities like this, domain.what_where or domain.what_owner. E.g. "switch.tv_livingroom", "sensor.temperature_kitchen", "sensor.battery_level_phone_dimitri". I do this for easier maintenance and consistency reasons.

You can [customize](https://www.home-assistant.io/docs/configuration/customizing-devices/) entities through the UI or through YAML. For lots of entites, especially similar entities, it's way easier and faster to do this through customization  in YAML. I use this for setting a friendly_name, icon, device_class and entity_picture where applicable. 

Here's an example from the customization section for some entities that are part of the presence detection setup. I put this in the package persons.yaml:

```yaml
homeassistant:
  customize:
    zone.home:
      friendly_name: Zu Hause
      icon: mdi:home
    person.dimitri:
      friendly_name: Dimitri
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
      icon: mdi:account
    device_tracker.room_presence_sabrina:
      friendly_name: Schlüssel Sabrina
      icon: mdi:key
```

### Combining Device Trackers

#### Creating a Person
After the onboarding process Home Assistant will automatically create a person with the details you entered in the onboarding process.
To create an additional person, click on "Configuration" in the sidebar of Home Assistant and then click on "Persons". Press the "+ ADD INTEGRATION" at the bottom right. Enter the name of the person and press "CREATE".

#### Binding Device Trackers to Persons
To bind a device tracker to a person, click on "Configuration" in the sidebar of Home Assistant and then click on "Persons". Click on the person you want to assign the device trackers to. In the field below "Select the devices that belong to this person" pick one of the device trackers, a second field to choose a device will appear, choose the second device tracker and then press "Update" in the bottom right.

### Make Presence Detection not so binary
This is based on a method of Phil Hawthorne, more details can be found in his tutorial [Making Home Assistant's Presence Detection not so Binary](https://philhawthorne.com/making-home-assistants-presence-detection-not-so-binary/). At the end of this part the state of the person entities is going to have the states "just left", "away" "extended away", "just arrived" and "home", instead of just "home" and "not_home". Like this we can avoid an arriving home automation getting triggered, when a person just left quickly for getting some bread at the bakery.

<details><summary>Step-by-step Guide</summary>
<p>

The non binary presence automation sets the state of the person to "just_left", "just_arrived", "at home", "away" or "extended away" based on the room persons home state. 

First create an input_select for each person for the non binary states.

```yaml
input_select:
  presence_state_him:
    name: Presence Him
    options:
      - just arrived
      - just left
      - at home
      - away
      - extended away
  presence_state_her:
    name: Presence Her
    options:
      - just arrived
      - just left
      - at home
      - away
      - extended away
```

And the automation [Set Person Non-Binary Presence State](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/persons.yaml#L113)

The house presence automation sets the state of the house to "someone_home", "nobody_home", "everyone_home" or "vacation" based on the persons peresence state.

Create an input_select for the house.

```yaml
  presence_state_house:
    name: Präsenz zu Hause
    options:
      - someone home
      - nobody home
      - everyone home
      - vacation
```
And groups for all persons and all non-binary presence input selects.

```yaml
group:
  family:
    name: Familie
    entities:
      - person.him
      - person.her
  presence_input_selects:
    name: Präsenz Input Selektoren
    entities:
      - input_select.presence_state_him
      - input_select.presence_state_her

```

And the automation to set it [Set House Non Binary Presence State](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/persons.yaml#L163)

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

### Turn everything off when last person left
I have an automation that turns all lights and devices off when everyone has left the house.
For this I use a script that turns everything off and call the script from the automation. I do it like this in order to also be able to call the same script from other automations.

Simple script to turn everything off [Turn All Off](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/house.yaml#L15)

The automation to run the script when everyone left [Turn Everything Off Everyone Gone](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/house.yaml#L3)


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
<img src="git-pictures/device_pictures/esp32.jpg" raw=true height="150" alt="ESP32" />
</td>
<td align="center" style="width:50%;">
<img src="git-pictures/device_pictures/pressure_mats.jpg" raw=true height="150" alt="Pressure Mats" />
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
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "ESPHome" and click on it.
Enter the IP or hostname of the ESP32 Sensor in the field "host", "port" can be left as it is at 6053. Click "SUBMIT". Enter the password set in the section "api" of the ESPHome config file. Click "SUBMIT" again. You should now see the binary sensors configured on the ESP.

### Make Bed Occupancy not so binary
Same as the [not so binary presence detection](#make-presence-detection-not-so-binary) (just left, just arrived, home, etc.), we're going to create a not so binary bed occupancy state. The app sets the following states for the person entities' sleep state: "just laid down", "sleeping", "just got up", "awake", and "back to bed" for the "I quickly need to go to the toilet" situations. The app also sets the sleep state of the house entity to "somone in bed", "nobody in bed" and "everyone in bed".

Everything related to the sleeping can be found in [sleep.yaml](home-assistant/packages/sleep.yaml).

One `input_boolean` for the the global sleep mode.

```yaml
input_boolean:
  sleep_mode:
    name: Schlafmodus
    icon: mdi:sleep
```

One `input_select` per person for the non binary sleep states.

```yaml
input_select:
  sleep_state_him:
    name: Sleep State Him
    options:
      - just laid down
      - just got up
      - awake
      - sleeping
      - back to bed
  sleep_state_her:
    name: Sleep State Her
    options:
      - just laid down
      - just got up
      - awake
      - sleeping
      - back to bed
```

An automation to set the non-binary input_select, which works as follows:
* Someone entered the bed AND previous state was NOT "just got up" -> select "just laid down"
* Someone entered the bed AND previous state was "just got up" -> select "back to bed"
* Someone left the bed -> select "just got up"
* Someone was "just got up" for 5 minutes -> select "awake"
* Someone was "just laid down" or "back to bed" for 5 minutes -> select "sleeping"

[Set Person Sleep State](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/sleep.yaml#L32)

These sleep states are going to be used later in other automations, e.g. lighting control, sleep/wakeup scenes etc.

A second automation to set the global sleep state based on the persons' sleep states [Set Sleep Mode Based on Bed Occupancy](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/sleep.yaml#L76)

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
<img src="git-pictures/device_pictures/pi_3.jpg" raw=true height="200" alt="Pi 3"/>
</td>
<td align="center" style="width:33%;">
<img src="git-pictures/device_pictures/conbee_stick.jpg" raw=true height="200" alt="ConBee" />
</td>
<td align="center" style="width:34%;">
<img src="git-pictures/device_pictures/aeotec_stick.jpg" raw=true height="200" alt="Philips Hue" />
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
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "deconz" and click on it.
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
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "openzwave" and click on "OpenZWave (Beta).
Hit "Submit".

If you already had devices paired to the Aeotec stick previously your devices should appear under "Configuration" -> "Integrations" -> "OpenZWave (Beta)". 

To add devices, access the web interface through http://ip-op-the-pi:7800. Click on "Open" in the top left corner. Press "Start" in the bottom box called "Remote OZWDaemon". Bring the device close to the Aeotec stick for pairing. Click on "Add Node" in the second line at the top. If you want to include the device securely, press "Yes" in the pop-up box, otherwise press "No". Put the device into pairing mode (For the Aeotec Multisensors I use press on the button at the back, for secure mode press twice extremly fast). Your device should appear under "Node List" if it was successful. Put the device into the final location and press "Heal Network". Check in Home Assistant if the devices appeared.

The web interface can also be used to change device specific configuration such as motion sensor sensitivity for the Aeotec Multisensor. There is also a service in home assistant (Developer Tools -> Services) called "ozw.set_config_parameter", which also enables changing device specific configuration.

</p>
</details>


## Lighting <a name="lighting" href="https://github.com/Burningstone91/smart-home-setup#lighting"></a>
### Basic Explanation of Setup

The lighting behaviour is determined by motion, occupancy and light level in the area, sleep state of the house and circadian rhythm.

### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:20%;">
Philips Hue Bulbs (8x Color E27, 3x White GU10, 1x LED strip 5m)
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
<img src="git-pictures/device_pictures/philips_hue.jpg" raw=true height="150" alt="Philips Hue" />
</td>
<td align="center" style="width:20%;">
<img src="git-pictures/device_pictures/ikea_plug.jpg" raw=true height="120" alt="IKEA Plug" />
</td>
<td align="center" style="width:20%;">
<img src="git-pictures/device_pictures/hue_motion.jpg" raw=true height="150" alt="Hue Motion" />
</td>
<td align="center" style="width:20%;">
<img src="git-pictures/device_pictures/aeotec_multi.jpg" raw=true height="120" alt="Aeotec Multisensor" />
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

* In Phoscon go to Devices -> Sensors and press "Add new sensor" at the bottom of the page.
* Reset the device by pressing and holding the setup button (small holle at the back) for 10 seconds, the LED should blink orange
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

### Setup Adaptive Lighting
I use the the [Adaptive Ligting integration](......) to calculate the brightness and color temperature for the lights. I mainly use the periodical adjustment in the office, when I'm working from home. Otherwise I "only" use the integration to turn on the lights at the correct brightness and color temperature. 

### Area Lighting
The lights are turned on through motion and turned off through room occupancy. I didn't want to turn on lights on occupancy, as sometimes someone may be standing close to a room for a few seconds and make the room occupied, even though the person has no intention to enter the room.

There's two automations and one binary sensor for each room.

The binary sensor is used to determine room occupancy. Here's an example from the office:

```yaml
binary_sensor:
  - platform: template
    sensors:
      occupancy_office:
        friendly_name: Büro besetzt
        device_class: occupancy
        value_template: >-
          {% set motion = is_state('binary_sensor.motion_office', 'on') %}
          {% set deskhim = is_state('device_tracker.desktop_dimitri', 'home') %}
          {% set deskher = is_state('device_tracker.desktop_sabrina', 'home') %}
          {% set laptopwork = is_state('device_tracker.laptop_work', 'home') %}
          {{ motion or deskhim or deskher or laptopwork }}
        delay_off:
          minutes: 15
```

This will make the room occupied when at least one of the following conditons is met:
* Motion detected
* Desktop of my wife is on (Unifi device tracker)
* My Desktop is on (Unifi device tracker)
* My Work Laptop is on (Unifi device tracker)
When none of the above conditions is met for 15 minutes, the room will be marked as not occupied.

The first automation will turn the light on when motion (binary_sensor.motion_office) is detected. The lights will only be turned on when the lights are not already on and the lux level (sensor.lux_office) is below 200.

```yaml
automation:
  - id: motion_light_on_office
    alias: "Licht an bei Bewegung - Büro"
    mode: single
    trigger:
      platform: state
      entity_id: binary_sensor.motion_office
      to: "on"
    condition:
      - "{{ is_state('light.office', 'off') }}"
      - condition: numeric_state
        entity_id: sensor.lux_office
        below: 200
    action:
      service: light.turn_on
      entity_id: light.office
```

The second automation turns the lights off when the room is not occupied (binary_sensor.occupancy_office) anymore. The lights will only be turned off, if they are already on.

```yaml
automation:
- id: no_occupancy_light_off_office
    alias: "Licht aus Büro nicht besetzt"
    mode: single
    trigger:
      platform: state
      entity_id: binary_sensor.occupancy_office
      to: "off"
    condition: "{{ is_state('light.office', 'on') }}"
    action:
      service: light.turn_off
      entity_id: light.office
```

</p>
</details>


## Switches/Remotes <a name="switches" href="https://github.com/Burningstone91/smart-home-setup#switches"></a>
### Basic Explanation of Setup

We use multiple switches/remotes around the house to control different things, mostly lights. The [Switches app](#switches-appdaemon) is used to contorl the behaviour of the switches/remotes. A remote can be configured as a light switch to automatically set certain light related behaviour, e.g. press ON button -> turn light on, hold DIM UP button -> increase brightness etc. 

### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:25%;">
6x Philips Hue Dimmer Switch
</td>
<td align="center" style="width:25%;">
2x IKEA Tradfri Switch
</td>
<td align="center" style="width:25%;">
1x IKEA Symfonisk Controller
</td>
<td align="center" style="width:25%;">
1x Xiaomi Mi Round Switch
</td>
</tr>

<tr>
<td align="center" style="width:25%;">
<img src="git-pictures/device_pictures/hue_dimmer.jpg" raw=true height="100" alt="Hue Dimmer" />
</td>
<td align="center" style="width:25%;">
<img src="git-pictures/device_pictures/ikea_tradfri_switch.png" raw=true height="100" alt="IKEA Switch" />
</td>
<td align="center" style="width:25%;">
<img src="git-pictures/device_pictures/ikea_symfonisk_controller.png" raw=true height="100" alt="IKEA Symfonisk" />
</td>
<td align="center" style="width:25%;">
<img src="git-pictures/device_pictures/xiaomi_round_switch.jpg" raw=true height="100" alt="Xiaomi Round Switch" />
</td>
</tr>

<tr><td colspan="5">
The Hue Dimmer Switches are used to replace the dumb light switches and as a master control for me and my wife next to the bed on the respective side. The IKEA Symfonisk Controller is used to control music volume and lights in the office for when I'm doing Home Office. The IKEA Tradfri Switches are used to control some basic lights on the balcony and the Xiaomi Switch is currently looking for a job :)
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

### Adding switches/remotes to the ZigBee network (Xiaomi, Philips, IKEA)
Head over to the Phoscon Web UI under http://ip-of-your-pi:8080/pwa. And execute the following steps to integrate a switch/remote control:

* In Phoscon go to Devices -> Switches and press "Add new switch" at the bottom of the page.
* Choose "Philips" for the Hue Dimmer Switch and "Other" for the Xiaomi switch and IKEA switch/symfonisk.
* Enable Pairing Mode on the device:
  * Philips Hue Dimmer: Press and hold the small button in the hole on the back until the LED on the front blinks orange.
  * IKEA Tradfri Switch: Loosen the screw on the back and remove the cover, press the button 4 times within 5 seconds.
  * IKEA Symfonisk Controller: Loosen the screw on the back and remove the cover, press the button for approx. 10 seconds.
  * Xiaomi Round Switch: Press and hold the small button in the hole on the back of the switch until the blue LED starts to blink.

The switch should now show up in Phoscon. Switches will only show up as a battery entity within Home Assistant, the button presses are handled through events rather than entities. You can see what event occurs on which button press by going to (within Home Assistant) Developer Tools and then choose the events tab. In the Box "Listen to events" enter "deconz_event" in the field "Event to subscribe to" and press "START LISTENING". You should now see events like this, whenever you press a button on a remote.

```json
{
    "event_type": "deconz_event",
    "data": {
        "id": "hue_dimmer_light_bedroom",
        "unique_id": "00:15:8d:00:04:02:37:01",
        "event": 1002
    },
    "origin": "LOCAL",
    "time_fired": "2020-09-14T17:54:15.489321+00:00",
    "context": {
        "id": "4de8a92df6b311eaad170977b70ca3b3",
        "parent_id": null,
        "user_id": null
    }
}
```

In the above example the switch can be identified by `hue_dimmer_light_bedroom` and the event was `1002`. In the AppDaemon app created in the next section, these events are translated to button presses and the buttons can easily be configured to call a service or execute a script. 

### Switches (AppDaemon)
The app can be used with switches/remotes from different manufacturares like Xiaomi, IKEA and Philips. The currently implemented switches/remotes and their default behaviour is listed in the below section. Each switch is configured to have a default light behaviour, e.g. when you press turn on button it turns on the light.

Now to the app. Add a file called "switches.py" -> [switches.py](appdaemon/apps/switches.py)

Now add the configuration for the app to the individual area yaml files. There is a separate class for each type of switch/remote, this way it's easy to add new switches and configure default behaviour for them. Below are the currently implemented switches/remotes, the name of the the corresponding class and their default light behaviour.

* Philips Hue Dimmer Switch -> Class: HueDimmerSwitch
  * Short release Turn On -> Turn light on
  * Long press Turn On -> Turn light on at 100%
  * Short release Dim Up -> Increase brightness by 10%
  * Long press Dim Up -> Smoothly increase brightness until released
  * Long release Dim Up -> Stop light dimming
  * Short release Dim Down -> Decrease brightness by 10%
  * Long press Dim Down -> Smoothly decrease brightness until released
  * Long release Dim Down -> Stop light dimming
  * Short release Turn Off -> Turn light off
* Xiaomi Mi Round Wireless Switch -> Class: XiaomiWXKG01LM
  * Short release -> Toggle light
  * Double press -> Turn light on at 100%
  * Long press -> Smoothly increase brightness until released
  * Long release -> Stop light dimming
* Xiaomi Aqara Wireless Button 2016 version -> Class: XiaomiWXKG11LM2016
  * Short press -> Toggle light
  * Double press -> Turn light on at 100%
* IKEA Tradfri On/Off Switch -> Class: IKEATradfriE1743
  * Short release Turn On -> Turn light on
  * Long press Turn On -> Smoothly increase brightness until released
  * Long release Turn On -> Stop light dimming
  * Short release Turn Off -> Turn light off
  * Long press Turn Off -> Smoothly decrease brightness until released
  * Long release Turn Off -> Stop light dimming
* IKEA Symfonisk Sound Controller -> Class: IKEASymfonisk
  * Short press -> Toggle light
  * Double press -> Turn light on at 100%

The configuration parameters are as follows:

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | switches | The module name of the app.
`class` | False | string | | The name of the Class for the type of controller used.
`switch_id` | False | str | | The idenfitifier of the switch/remote. Can be found in the field "id" in the event message.
`lights` | True | string, list | | List of light entity_ids. If set, the default light behaviour will be applied to the switch/remote.
`custom_button_config` | True | dict | | Configuration for unused button presses or to override button presses of the default light behaviour if enabled.

Custom button configuration:
key | optional | type | default | description
-- | -- | -- | -- | --
`service` | False | string | | The service to be executed, e.g. light.turn_on.
`service` | True | string, list | | List of entity_ids to be used with the service call.
`data` | True | dict | | Dict of additonal service data, e.g. brightness_pct to 100%.


Example to configure turn on the lights in the office and living room at 100% brightness, on a long press of the Turn On button:

```yaml
custom_button_config:
  long_press_turn_on:
    service: light.turn_on
    entity_id: 
      - light.office
      - light.livingroom
    data:
      brightness_pct: 100

```

Full example:

```yaml
office_light_switch:
  module: switches
  class: HueDimmerSwitch
  switch_id: hue_dimmer_office
  lights: light.office
  custom_button_config:
    long_press_turn_off:
      service: homeassistant.turn_off
      entity_id: 
        - media_player.office
        - light.office
```
When I need more complex actions on a button press, like calling multiple services with delays in between etc., I create a script in Home Assistant and call this script from the button press.

</p>
</details>

## System Monitoring <a name="system-monitoring" href="https://github.com/Burningstone91/smart-home-setup#system-monitoring"></a>
### Basic Explanation of Setup
I use various integrations, custom components and scripts to montior most of the devices in my home. All this configuration is in one package called system_monitoring.yaml.

This is still a work in progress, but here are some screenshots.

The Server View:

![Alt text](/git-pictures/lovelace_views/server.png?raw=true "Server View")

The Network View:

![Alt text](/git-pictures/lovelace_views/network.png?raw=true "Network View")

The Backup View:

![Alt text](/git-pictures/lovelace_views/backup_view.png?raw=true "Backup View")

The Unifi Device Tracker View:

![Alt text](/git-pictures/lovelace_views/unifi_devices.png?raw=true "Device Tracker")

The System Monitoring View:

![Alt text](/git-pictures/lovelace_views/system_monitoring.png?raw=true "System Monitoring")

Create a file called system_monitoring.yaml inside the packages directory of Home Assistant.

<details><summary>Step-by-step Guide</summary>
<p>

### Create and distribute SSH keys
In order to execute shell commands on remote machines throught SSH, we create SSH keys on the host running Home Assistant and copy the public key to the remote machines. 

SSH into the host running Home Assistant

Create new keys
```bash
ssh-keygen
```
Enter a name for the keys or press Enter to use the default.

Copy the keys to the remote machine
```bash
ssh-copy-id username@ip-of-remote-machine
```
Enter the SSH password to login to the remote machine.

e.g.
```bash
ssh-copy-id pi@10.10.70.7
```

If everything was sucessful, you will be able to SSH into the host without entering a password. 

Now we need to mount the SSH keys from the host to the Home Assistant docker container. In order to do this, add the following line to the `volumes:` section of the Home Assistant container in the `docker-compose.yml` file.

```yaml
- /home/pi/.ssh:/root/.ssh
```
Replace `pi` with your username on the host machine running Home Assistant.

Start the docker stack:
```bash
docker-compose up -d
```

### Proxmox
#### Virtual Machines status
To get the status of the virtual machines running inside Proxmox we can use the [Proxmox VE integration](https://www.home-assistant.io/integrations/proxmoxve/). First follow the directions from the docs [here](https://www.home-assistant.io/integrations/proxmoxve/#proxmox-permissions) to create a user in Proxmox with sufficient permissions to read the status of the virtuals machines. Next, add the following to the system_monitoring.yaml file:

```yaml
proxmoxve:
  host: 10.10.40.6
  username: secretuser
  password: supersecretpassword
  realm: pve
  verify_ssl: false
  nodes:
    - node: pve
      vms:
        - 101
        - 102
        - 103
        - 105
```

The numbers in the section vms are the ids of the VMs running in Proxmox. 

#### Proxmox version
To get the currently installed version we can use the [command line sensor integration](https://www.home-assistant.io/integrations/sensor.command_line/). Before creating the sensor, make sure that you copied the SSH keys (as describted [here](#create-and-distribute-ssh-keys)) from the host machine to the machine running Proxmox.

Add the following to the system_monitoring.yaml file:

```yaml
sensor:
  - platform: command_line
    name: Version Proxmox VE 
    command: 'ssh -i /root/.ssh/id_rsa -o StrictHostKeyChecking=no -q root@10.10.40.6 pveversion | cut -f2 -d/'
    scan_interval: 3600
```

In the `command` field in the part `root@10.10.40.6`, replace root with the username used to SSH into the Proxmox host and 10.10.40.6 with the IP of the Proxmox host.

Restart Home Assistant. You should now have a sensor called `sensor.version_proxmox_ve`, which shows the current running Proxmox VE version and which will be updated every hour (scan_interval: 3600).

### Host Monitoring
#### System statistics
To get statistics like cpu load, memory usage, etc. we use the [System Monitor integration](https://www.home-assistant.io/integrations/systemmonitor/). Add the following in the `sensor:` section of the system_monitoring.yaml file:


```yaml
  - platform: systemmonitor
    resources:
    - type: disk_use_percent
      arg: /home
    - type: disk_use
      arg: /home
    - type: disk_free
      arg: /home
    - type: memory_free
    - type: memory_use
    - type: memory_use_percent
    - type: swap_use_percent
    - type: swap_use
    - type: swap_free
    - type: load_1m
    - type: load_5m
    - type: load_15m
    - type: network_in
      arg: ens18
    - type: network_out
      arg: ens18
    - type: throughput_network_in
      arg: ens18
    - type: throughput_network_out
      arg: ens18
    - type: packets_in
      arg: ens18
    - type: packets_out
      arg: ens18
    - type: processor_use
    - type: last_boot   
    - type: ipv4_address
      arg: ens18
```
Restart Home Assistant. 

#### CPU Temperature
As I run Home Assistant inside a Virtual machine, I don't have direct access to the CPU temperature of the machine running Home Assistant. As a workaround we can use a [command line sensor integration](https://www.home-assistant.io/integrations/sensor.command_line/). Before creating the sensor, make sure that you copied the SSH keys (as describted [here](#create-and-distribute-ssh-keys)) from the virtual machine to the host running the virtual machines.

Add the following in the `sensor:` section of the system_monitoring.yaml file:

```yaml
  - platform: command_line
    name: temperature_cpu_nuc
    command: 'ssh -i /root/.ssh/id_rsa -o StrictHostKeyChecking=no -q root@10.10.40.6 cat /sys/class/thermal/thermal_zone3/temp'
    value_template: "{{ value | int / 1000 }}"
    unit_of_measurement: "°C"
```

In the `command` field in the part `root@10.10.40.6`, replace root with the username used to SSH into the Proxmox host and 10.10.40.6 with the IP of the Proxmox host.

To get the correct thermal zone issue the following command on the host machine running Home Assistant:
```
cat /sys/class/thermal/thermal_zone*/type
```
Example output:

```bash
root@pve:~# cat /sys/class/thermal/thermal_zone*/type
acpitz ## <-thermal zone 0
pch_skylake ## <-thermal zone 1
iwlwifi_1 ## <-thermal zone 2
x86_pkg_temp ## <-thermal zone 3
```
For the Intel NUC the type to look for is `x86_pkg_temp`.

### Docker Monitoring
To monitor docker containers we can use a nice little custom component called [Monitor Docker](https://github.com/ualex73/monitor_docker). Install as per instructions on the Github Repository. This requires to have MQTT setup in Home Assistant and it doesn't work for Home Assistant Supervised (there's a workaround shown [here](https://github.com/ualex73/monitor_docker/issues/31)) or Home Assistant OS (no workaround that would be persistent). This gives you a bunch of sensors such as processor use, ram use, image for each docker container and some statistics about docker such as total number of running containers and version.

Here's my example config from system_monitoring.yaml:

```yaml
monitor_docker:
  - name: Docker
    containers:
      - appdaemon
      - esphome-dashboard
      - hass
      - hass-db
      - mqtt
      - influxdb
      - grafana
      - portainer
      - unifi-poller
    rename:
      appdaemon: AppDaemon
      esphome-dashboard: "ESPHome-Dashboard"
      hass: Home Assistant
      hass-db: Postgres
      mqtt: Mosquitto
      influxdb: InfluxDB
      grafana: Grafana
      portainer: Portainer
      unifi-poller: "Unifi-Poller"
    monitored_conditions:
      - version
      - status
      - image
      - cpu_percentage
      - memory_percentage
```

### Software versions
#### Home Assistant
To get the installed and latest available version of Home Assistant we can use the [version integration](https://www.home-assistant.io/integrations/version/).

Add the following in the `sensor:` section of the system_monitoring.yaml file:\
Installed:
```yaml
  - platform: version
    name: current_version_homeassistant
```
Latest(example for docker install, showing beta versions):
```yaml
  - platform: version
    name: latest_version_homeassistant
    source: docker
    beta: true
```
Restart Home Assistant.

#### AppDaemon
To get the latest available version of AppDaemon we can use the [command line sensor integration](https://www.home-assistant.io/integrations/sensor.command_line/) to curl the PyPi address of AppDaemon.

Add the following in the `sensor:` section of the system_monitoring.yaml file:

```yaml
  - platform: command_line
    name: latest_version_appdaemon
    command: >-
      curl -L
      -H "User-Agent: Home Assistant"
      -H "Content-Type: application/json"
      https://pypi.python.org/pypi/appdaemon/json
    value_template: '{{ value_json.info.version }}'
    scan_interval: 3600
```
To get the installed version:
TODO

Restart Home Assistant.

#### DeCONZ
To get the installed and latest available version of DeCONZ we can use the [rest sensor integration](https://www.home-assistant.io/integrations/rest/). To get the current version of deCONZ you need to generate an API key. Detailed instructions on how to get an API key can be found in the [deCONZ REST API docs](https://dresden-elektronik.github.io/deconz-rest-doc/getting_started/).

Add the following in the `sensor:` section of the system_monitoring.yaml file:\
Installed:
```yaml  
  - platform: rest
    resource: http://ip-of-phoscon:8080/api/YOURAPIKEY/config
    name: current_version_deconz
    value_template: "{{ value_json.swversion }}"
    scan_interval: 3600
```
Latest:
```yaml  
  - platform: rest
    resource: https://api.github.com/repos/dresden-elektronik/deconz-rest-plugin/releases/latest
    name: latest_version_deconz
    value_template: >
      {{ value_json.tag_name.strip('_stable').lstrip('V').replace('_','.').replace('0','') }}
    scan_interval: 3600
```

#### ConBee II Firmware
To get the current firmware of the ConBee II we can use the [rest sensor integration](https://www.home-assistant.io/integrations/rest/). This also needs an API key as described in the previous section.

Add the following in the `sensor:` section of the system_monitoring.yaml file:\
Installed:
```yaml  
  - platform: rest
    resource: http://ip-of-phoscon:8080/api/YOURAPIKEY/config
    name: current_firmware_conbee
    value_template: "{{ value_json.fwversion }}"
    scan_interval: 3600
```

To get the latest version of the ConBee II firmware I use a small AppDaemon app.

TODO (add instructions for AppDaemon app)

#### PiHole
To get the installed and latest available version of Pi Hole we can use the [rest sensor integration](https://www.home-assistant.io/integrations/rest/).

Add the following in the `sensor:` section of the system_monitoring.yaml file:\
Core Installed:
```yaml  
  - platform: rest
    resource: http://10.10.0.8/admin/api.php?versions
    name: current_version_pihole_core
    value_template: "{{ value_json.core_current[1:] }}"
```
Core Latest:
```yaml  
  - platform: rest
    resource: http://10.10.0.8/admin/api.php?versions
    name: latest_version_pihole_core
    value_template: "{{ value_json.core_latest[1:] }}"
```
Web Installed:
```yaml  
  - platform: rest
    resource: http://10.10.0.8/admin/api.php?versions
    name: current_version_pihole_core
    value_template: "{{ value_json.core_current[1:] }}"
```
Web Latest:
```yaml  
  - platform: rest
    resource: http://10.10.0.8/admin/api.php?versions
    name: current_version_pihole_web
    value_template: "{{ value_json.web_current[1:] }}"
```
FTL Installed:
```yaml  
  - platform: rest
    resource: http://10.10.0.8/admin/api.php?versions
    name: current_version_pihole_ftl
    value_template: "{{ value_json.FTL_current[1:] }}"
```
FTL Latest:
```yaml  
  - platform: rest
    resource: http://10.10.0.8/admin/api.php?versions
    name: latest_version_pihole_ftl
    value_template: "{{ value_json.FTL_latest[1:] }}"
```

Restart Home Assistant.

#### Docker Containers
To monitor the whether the docker containers use the latest available image, I use a docker container called [What's Up Docker](https://fmartinou.github.io/whats-up-docker/#/) or short WUD. It sends the data through MQTT and the binary sensors will be added automatically to Home Assistant, without any further configuration.

Create a new directory called "wud" on the level where the home-assistant and appdaemon directories are located to store the data.
Add the following to docker-compose.yml to configure the WUD docker container:

```yaml
  wud:
    container_name: wud
    environment:
      - WUD_TRIGGER_MQTT_MOSQUITTO_URL=mqtt://mqtt-server-ip:1883
      - WUD_TRIGGER_MQTT_MOSQUITTO_USER=yourmqttusername
      - WUD_TRIGGER_MQTT_MOSQUITTO_PASSWORD=yoursupersecretmqttpassword
      - WUD_TRIGGER_MQTT_MOSQUITTO_HASS_ENABLED=true
      - WUD_WATCHER_LOCAL_SOCKET=/var/run/docker.sock
      - WUD_WATCHER_LOCAL_WATCHBYDEFAULT=false
    image: fmartinou/whats-up-docker:5.2.0
    restart: unless-stopped
    ports:
      - "3005:3000"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - ./wud:/store
```

I stopped using the latest tag, and started using version tags instead for my docker containers. This makes me more conscious about updating my containers and avoids running into updates with breaking changes, when running `docker-compose pull`. This led to some headaches in the past with e.g. InfluxDB and Mosquitto. 

I don't watch all containers by default, as I have some self-built ones and some containers on a registery that is not supported by What's Up Docker. Instead I add labels to the containers I want to watch and also to only watch for dot versions such as 2.2.5. I add the following lines:

```yaml
labels: 
      - wud.tag.include=^\d+\.\d+\.\d+$$
      - wud.watch=true
```
Here's an example for Grafana:

```yaml
  grafana:
    container_name: grafana
    depends_on:
      - influxdb
    environment:
      - GF_SECURITY_ADMIN_USER=secretusername
      - GF_SECURITY_ADMIN_PASSWORD=supersecretpassword
    image: grafana/grafana:8.1.1
    labels: 
      - wud.tag.include=^\d+\.\d+\.\d+$$
      - wud.watch=true
    restart: unless-stopped
    user: "1000"
    ports:
      - "3000:3000"
    volumes:
      - ./grafana:/var/lib/grafana
      - /etc/localtime:/etc/localtime:ro
```

I also have some containers running on other machines than Home Assistant. These can also be watched with wud. First you need to enable the docker remote API:

1. SSH into the remote machine running the docker stack you want to watch.
2. Edit the docker service file:
`nano /lib/systemd/system/docker.service`
3. Find the line which starts with `ExecStart` and change it to:
`ExecStart=/usr/bin/dockerd -H=fd:// -H=tcp://0.0.0.0:2375`
4. Save the modified file.
5. Reload the docker daemon with `sudo systemctl daemon-reload`
6. Restart docker with `sudo service docker restart`
7. Test with sending the below command from another machine:
`curl http://ip-of-docker-machine:2375/images/json`
8. In case of success a JSON formatted string should be returned, containing various information about the containers on this machine.

Now add the following to the wud docker configuration to include the remote host:

```yaml
environment:
    - WUD_WATCHER_CLOUD_HOST=ip-of-remote-docker-host
    - WUD_WATCHER_CLOUD_PORT=2375
    - WUD_WATCHER_CLOUD_WATCHBYDEFAULT=false
```
Again add the labels to the containers you want to watch on the remote host.

In case of success, you should now have one binary sensor per container you are watching. The binary sensor is `on` when a new version is available. The attribute `image_tag_value` shows the current version and the attribute `result_tag` shows the latest version available. We'll use these sensors later in the automation, which notifies about updates available.

### Synology NAS
#### Statistics
To monitor the Synology NAS we can use the [Synology DSM integration](https://www.home-assistant.io/integrations/synology_dsm/). In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "Synology DSM" and click on it. In the host field enter the IP of your NAS, fill in the username and password to log into the NAS and press Submit. You should now have sensors for the disk temperature, disk size, cpu load etc.

#### Model and Firmware
To get the model and current firmware we can use the [SNMP integration](https://www.home-assistant.io/integrations/snmp/). First you need to enable SNMP on the NAS. Login to the Web Interface of the NAS, go to "Control Panel" and then choose "Terminal & SNMP". Go to the tab "SNMP" and enable the SNMP Service.
Add the following in the `sensor:` section of the system_monitoring.yaml file:
Model:
```yaml
  - platform: snmp
    name: Model NAS
    host: 10.10.40.15
    community: 'public'
    baseoid: 1.3.6.1.4.1.6574.1.5.1.0
```
Firmware:
```yaml
  - platform: snmp
    name: Firmware NAS
    host: 10.10.40.15
    community: 'public'
    baseoid: 1.3.6.1.4.1.6574.1.5.3.0
```
The Synology DSM integration provides a binary_sensor that shows whether an update is available or not.

### Unifi Devices
#### Unifi Controller
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "Unifi" and click on it.
Enter the IP of your Unifi Controller in the field "host".
Enter your username and password and press "SUBMIT"

This will give you a device_tracker for each network device and some additional data, such as IP address as attributes of the device trackers.

#### Unifi Device statistics
To get the model, current firmware and other measures we can use the [SNMP integration](https://www.home-assistant.io/integrations/snmp/). First you need to enable SNMP in Unifi. Login to the Web Interface of the Unifi Controller. Go to "Settings", then "Services". In the tab "SNMP" enable "SNMPV1, SNMPV2C". Availability of updates is an attribute of the device trackers created by the Unifi integration. The device trackers for the unifi devices have an attribute 'upgradeable', which is 'true' when an upgrade for the device is availble and it disappears when the device is up-to-date. 

Add the following in the `sensor:` section of the system_monitoring.yaml file:\

[AP-AC Pro](https://github.com/Burningstone91/smart-home-setup/blob/5c6b161a2bccc7ad7227cdc8e7b9d0411bcfc469/home-assistant/packages/system_monitoring.yaml#L248)

[Switch US8-150w](https://github.com/Burningstone91/smart-home-setup/blob/5c6b161a2bccc7ad7227cdc8e7b9d0411bcfc469/home-assistant/packages/system_monitoring.yaml#L283)

[Switch US8-60w](https://github.com/Burningstone91/smart-home-setup/blob/5c6b161a2bccc7ad7227cdc8e7b9d0411bcfc469/home-assistant/packages/system_monitoring.yaml#L325)

[Unifi Security Gateway 3](https://github.com/Burningstone91/smart-home-setup/blob/5c6b161a2bccc7ad7227cdc8e7b9d0411bcfc469/home-assistant/packages/system_monitoring.yaml#L360)

### PiHole
To monitor a PiHole instance we can use the [Pi-Hole integration](https://www.home-assistant.io/integrations/pi_hole/). In order to enable/disable PiHole, we need to get the API key first. Log into the Web interface of Pi-Hole go to "Settings". In the tab "API/Web Interface" click on the button "Show API token". Copy the token.
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "Pi-Hole" and click on it.
Enter the IP of your Pi-Hole instance in the field "Host".
Paste the token from the previous step in the field "API key" and press "SUBMIT".

### Speedtest
To get Speedtest data we can use the [Speedtest.net integration](https://www.home-assistant.io/integrations/speedtestdotnet/).
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "speedtest" and click on it. Press "SUBMIT".


### Remote Raspberry Pis
To monitor remote Raspberry Pis such as my Room Assistant instances, I use this nice little shell script called [System Sensors](https://github.com/Sennevds/system_sensors) that publishes statistics about the Pi such as updates available, last boot, cpu load, etc. to MQTT. It uses Audo-Discovery, therefore we don't need to do anything on Home Assistant's side.

Instructions how to set it up on a Pi:
Install dependencies and download script.
```bash
sudo apt-get install git
sudo apt-get install git python3-pip python3-apt
git clone https://github.com/Sennevds/system_sensors.git
cd system_sensors
pip3 install -r requirements.txt
```

Edit config:
```bash
nano settings_example.yaml
```

```yaml
mqtt:
  hostname: 10.10.40.6
  port: 1883
  user: secretuser
  password: supersecretpassword
deviceName: pi_dressroom
client_id: pi_dressroom_system_monitor
timezone: Europe/Zurich
update_interval: 60
check_wifi_strength: true
check_available_updates: true
```

Rename settings file:
```bash
mv settings_example.yaml setting.yaml
```

Create a systemd service:
```bash
sudo nano /etc/systemd/system/system_sensors.service
```
```bash
[Unit]
Description=System Sensor service
After=multi-user.target

[Service]
User=pi
Type=idle
ExecStart=/usr/bin/python3 /home/pi/system_sensors/src/system_sensors.py /home/pi/system_sensors/src/settings.yaml

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable system_sensors.service
sudo systemctl start system_sensors.service
```

### Portainer
To manage docker containers through a GUI, we can use [Portainer](https://www.portainer.io/).
Add the following to docker-compose.yml to configure the portainer docker container:
```yaml
  portainer:
    container_name: portainer
    image: "portainer/portainer:1.24.1-alpine"
    ports:
      - "9000:9000"
      - "8000:8000"
    restart: always
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - ./portainer:/data
```

Start docker stack:
```bash
docker-compose up -d
```

Now you can manage your docker containers through the GUI at http://ip-of-home-assistant-server:9000.

### Notify on Update available
I use an automation that notifies me when an update is available. When my Desktop is running it will send a notification to my phone, otherwise it will send an E-Mail to Evernote./
Sidenote: Evernote is an app to manage your notes and I use it heavily to organize all my projects in my personal life and in my work life as well. The E-Mail that is sent to Evernote contains instructions on where the note should be placed, this way it will show up when I do a daily review of my notes and I can plan the tasks that were sent by Home Assistant accordingly. I use this for non-critical notifications, like "the oven hasn't been cleaned for a long time" or "an update for Grafana is available". These are things that I want to have a note in my organization system and can plan to do when time allows it, instead of having a Home Assistant notification hanging around on my phone constantly reminding me about the task. This will trick your mind and make the task more important than it actually is, it occupies your mind until you finished the task and takes away space for other thoughts and ideas.

I have a package for the configuration of the different notifiers and notifier groups called [notifiers.yaml](/home-assistant/packages/notifiers.yaml).

Here's an example configuration for the mail notifier (which I use to send an Mail to Evernote) using the [SNMP integration](https://www.home-assistant.io/integrations/smtp/).

```yaml
notify:
  - platform: smtp
    name: evernote
    server: smtp.gmail.com
    port: 587
    encryption: starttls
    timeout: 15
    username: !secret mail_address
    password: !secret mail_password
    sender: !secret mail_address
    sender_name: Home Assistant
    recipient: !secret evernote_mail
```
The notifier for the phone will automatically be created once you connected the Home Assistant Companion App on your phone with your Home Assistant instance. 

The linked automation triggers on all the different sensors that show that an update is available in different ways. The docker sensors show "Update Available", the Pi sensors have a number of updates available and the version sensors each have a latest and a current version sensor. If my Desktop is running, then the notification will be sent to my phone because then I may have time to do the update right now as I'm already using my computer. Otherwise it will be sent to my organization tool via Mail that I can plan it for later.

[Notify on update available](https://github.com/Burningstone91/smart-home-setup/blob/309ba38ed9797f3849d91597a8be7b4bf9643d8a/home-assistant/packages/system_monitoring.yaml#L805)


### Home Assistant Heartbeat and Backup Sensors (Healthchecks.io)
I use [Healtchecks.io](https://healthchecks.io/) to create a heartbeat monitor for Home Assistant. This works by sending a ping to a specific URL from healthchecks.io through the [rest sensor integration](https://www.home-assistant.io/integrations/rest/) every x minutes. Healthchecks.io checks at the given interval whether the ping is received or not, and if not it will send a notification through one of the various integrations they have such as WhatsApp, E-Mail, Slack, etc. 

Create a free account at [Healtchecks.io](https://healthchecks.io/). Add a new check, give it a meaninful name such as "Home Assistant Heartbeat" and note down the ping URL, they look like this: https://hc-ping.com/abcdef-gh2345-hgi234234 . Change the schedule to your needs, I use a period of 5 minutes and a grace period of 5 minutes, this means it checks every 5 minutes (period) and if a ping is not received 5 minutes (grace period) after it should it will send an alert.

Now in Home Assistant add a Rest sensor like this:

```yaml
sensor:
  - platform: rest
    resource: healtchecks_ping_url
    name: Home Assistant Heartbeat
    scan_interval: 300
```
The scan interval must match with the period you set in the healtchecks.io check. Now the sensor will send a GET request to the healtchecks.io ping URL every 5 minutes.

I also use healthchecks.io to monitor my most important backups, such as the Home Assistant VM, the Network Pi, etc..

To monitor the automatic VM backup through Proxmox, I configured Proxmox to send the mail on sucess to the healthchecks.io mail address for this check. I then configured the check in healthchecks.io to look for the word "success" in the mail, set up a schedule to check daily at the time I do the backup. 

To monitor the backups of my Main NAS to the Backup NAS, I use the same methodology as for the VM backups, but the mail comes from Synology instead of Proxmox.

To monitor the backup of the network Pi and the ZigBee/Z-Wave Pi, I simply added a curl command to the healtchecks.io URL to my the cron jobs.

To see the status of your healthchecks.io checks and the last ping, you can use a REST sensor. First you need to log in to your healtchecks.io account and go to the settings of your project. There you'll find a button to "Show API Keys". Each check has an individual URL to get the status and the last ping. They look like this: https://healthchecks.io/api/v1/checks/UNIQUEIDOFYOURCHECK

Status of check:
```yaml
sensor:
  - platform: rest
    resource: https://healthchecks.io/api/v1/checks/UNIQUEIDOFYOURCHECK
    name: Daily Backup Home Assistant VM
    headers:
      X-Api-Key: YOURAPIKEY
    scan_interval: 1800
    value_template: "{{ value_json.status }}"
```
Last Ping:
```yaml
sensor:
  - platform: rest
    resource: https://healthchecks.io/api/v1/checks/UNIQUEIDOFYOURCHECK
    name: Last Backup Home Assistant VM
    headers:
      X-Api-Key: YOURAPIKEY
    scan_interval: 1800
    value_template: >
      {%- set last_boot = value_json.last_ping %}
      {%- set uptime = now().timestamp() - as_timestamp(last_boot) %}
      {%- set time = uptime | int %}
      {%- set minutes = ((time % 3600) // 60) %}
      {%- set minutes = '{}min'.format(minutes) if minutes > 0 else '' %}
      {%- set hours = ((time % 86400) // 3600) %}
      {%- set hours = '{}hr '.format(hours) if hours > 0 else '' %}
      {%- set days = (time // 86400) %}
      {%- set days = '{}d '.format(days) if days > 0 else '' %}
      {{ 'Less than 1 min' if time < 60 else days + hours + minutes }}
```

#### Notification on Failed Backup
I use an automation to notify me when one of the above backup healthchecks goes "down" (no ping happened -> issue).
[Notify on failed backup](https://github.com/Burningstone91/smart-home-setup/blob/daff0ff26c3ec0610c9fba7b204b1c2bc01a89b4/home-assistant/packages/system_monitoring.yaml#L1061)

### System Monitoring Notifications
#### Notification on Low Battery
I use a simple automation to notify me when the battery level for any of the ZigBee or Z-Wave devices is below 20%.

[Notify on low battery level](https://github.com/Burningstone91/smart-home-setup/blob/309ba38ed9797f3849d91597a8be7b4bf9643d8a/home-assistant/packages/system_monitoring.yaml#L859)

#### Notification on Bad Login Attempt
I use an automation to notify me when there was a bad login attempt. I use the emergency channel (only works for Android phones) for this notification. I configured my phone to allow messages from the emergency channel when in Do not Disturb Mode. 

[Notify on bad login attempt](https://github.com/Burningstone91/smart-home-setup/blob/309ba38ed9797f3849d91597a8be7b4bf9643d8a/home-assistant/packages/system_monitoring.yaml#L1000)

#### Notification on Device Offline
I use an automation to notify me when a device went offline. For network clients I check the device tracker generated by the Unifi integration going to 'not_home' for 5 minutes and for the ZigBee/Z-Wave devices I check when the respective sensor goes 'unavailable' for 5 minutes.

[Notify on device offline](https://github.com/Burningstone91/smart-home-setup/blob/309ba38ed9797f3849d91597a8be7b4bf9643d8a/home-assistant/packages/system_monitoring.yaml#L1017)

#### Notification on High Usage/Temperature of Devices
I use automations to notify me about high CPU load, high CPU/Disk temperature, high disk usage and under Voltage detected for the Pis.

[High CPU Load](https://github.com/Burningstone91/smart-home-setup/blob/309ba38ed9797f3849d91597a8be7b4bf9643d8a/home-assistant/packages/system_monitoring.yaml#L903)

[High CPU Temperature](https://github.com/Burningstone91/smart-home-setup/blob/309ba38ed9797f3849d91597a8be7b4bf9643d8a/home-assistant/packages/system_monitoring.yaml#L949)

[High Disk Temperature](https://github.com/Burningstone91/smart-home-setup/blob/eacd482ef61c7074f3bb49123ecbeefc1c74c96b/home-assistant/packages/system_monitoring.yaml#L1023)

[High Disk Usage](https://github.com/Burningstone91/smart-home-setup/blob/309ba38ed9797f3849d91597a8be7b4bf9643d8a/home-assistant/packages/system_monitoring.yaml#L930)

[Undervoltage](https://github.com/Burningstone91/smart-home-setup/blob/309ba38ed9797f3849d91597a8be7b4bf9643d8a/home-assistant/packages/system_monitoring.yaml#L977)

#### Notification on Insecure NAS
I use automations to notify me about one of the NAS being insecure, the sensor for this comes from the Synology DSM integration. Synology has a so called "Security Advisor" that you can configure, which performs certain security checks such as strong passwords, non-default port for SSH etc. If the Security Advisor is unsafe, the sensor in Home Assistant changes to `on`.

[Insecure NAS](https://github.com/Burningstone91/smart-home-setup/blob/eacd482ef61c7074f3bb49123ecbeefc1c74c96b/home-assistant/packages/system_monitoring.yaml#L1001)

</p>
</details>



## History & Databases <a name="history-databases" href="https://github.com/Burningstone91/smart-home-setup#history-databases"></a>
### Basic Explanation of Setup
For storing historical data, I use two databases. One database for short-term data, to show some history graphs in the frontend, debugging etc. and one database for long-term data such as temperature levels, power consumption etc. For the short-term data I use [PostgreSQL](https://www.postgresql.org/) and for long-term data [InfluxDB](https://www.influxdata.com/) and to make graphs for long-term data I use [Grafana](https://grafana.com/)

(ToDo) Add some Grafana Chart screenshots

<details><summary>Step-by-step Guide</summary>
<p>

### PostgreSQL
Create a new directory called "home-assistant-db" on the level where the home-assistant and appdaemon directories are located to store the data.
Add the following to docker-compose.yml to configure the PostgreSQL docker container:

```yaml
  hass-db:
    container_name: hass-db
    environment:
      POSTGRES_DB: "smart_home"
      POSTGRES_PASSWORD: "supersecretpassword"
      POSTGRES_USER: "secretusername"
    image: "postgres:9.6.19-alpine"
    ports:
      - "5432:5432"
    restart: always
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./home-assistant-db:/var/lib/postgresql/data
```

Start docker stack:
```bash
docker-compose up -d
```

Now you have a database called "smart_home", which we can use in the next step as the Home Assistant DB.

### Recorder
To use the PostgreSQL database created in the previous step, we need to configure and setup the [recorder integration](https://www.home-assistant.io/integrations/recorder/). I set the purge_keep_days to 7, which means that the Database will be purged every 7 days. I explicitly choose, which entities to include (whitelist) to not spam my DB with unnecessary data such as what time it was 5 days ago when the sun was at -6 elevation. The db url is as follows: 
`postgresql://username:password@127.0.0.1/smart_home `

Add a new file called history.yaml in the directory `packages`. 
Here's an example from my config:

```yaml
recorder:
  db_url: !secret db_url
  purge_keep_days: 7
  include:
    domains:
      - person
    entity_globs:
      - sensor.temperature*
      - sensor.humidity*
      - sensor.lux*
      - sensor.speedtest*
      - sensor.ram_use_pct*
      - sensor.cpu_load*
      - binary_sensor.door*
      - binary_sensor.window*
      - binary_sensor.motion*
      - binary_sensor.tamper*
    entities:
      - binary_sensor.bed_dimitri
      - sensor.location_phone_dimitri
      - sensor.network_throughput_in_ha
      - sensor.network_throughput_out_ha
      - sensor.wan_in_usg_mbps
      - sensor.wan_out_usg_mbps
      - sensor.network_in_ha
      - sensor.network_out_ha
      - sensor.network_down_nas
      - sensor.network_up_nas
      - light.balcony_ceiling
      - light.bedroom
      - light.bedroom_bed
      - light.bedroom_ceiling
      - light.livingroom
      - light.dressroom
      - light.office
      - media_player.buero_musik_main
      - media_player.receiver_livingroom
```

There's an excellent guide on the forums [here](https://community.home-assistant.io/t/how-to-reduce-your-database-size-and-extend-the-life-of-your-sd-card/205299) that explains how you can reduce the size of your DB, if this should be an issue for you.

### History
To enable the [history integration](https://www.home-assistant.io/integrations/history/) in Home Assistant add the following to history.yaml
```
history:
```

### InfluxDB
#### Setup Database
Create a new directory called "influxdb" on the level where the home-assistant and appdaemon directories are located to store the data.
Add the following to docker-compose.yml to configure the influxdb docker container:

```yaml
  influxdb:
    container_name: influxdb 
    environment:
      - INFLUXDB_DB=smart_home
      - INFLUXDB_ADMIN_USER=username
      - INFLUXDB_ADMIN_PASSWORD=yoursupersecretpassword
    image: influxdb:latest
    ports:
      - '8086:8086'
    restart: unless-stopped
    volumes:
      - ./influxdb:/var/lib/influxdb
      - /etc/localtime:/etc/localtime:ro
```

Start docker stack:
```bash
docker-compose up -d
```

#### Configure InfluxDB in Home Assistant
To push data from Home Assistant to InfluxDB we can use the [InfluxDB integration](https://www.home-assistant.io/integrations/influxdb/). 
Add the following to the history.yaml file, here's an example from my config:

```yaml
influxdb:
  username: !secret username
  password: !secret yoursupersecretpassword
  database: smart_home
  include:
    domains:
      - person
    entity_globs:
      - sensor.temperature*
      - sensor.humidity*
      - sensor.lux*
      - sensor.speedtest*
      - sensor.ram_use_pct*
      - sensor.cpu_load*
    entities:
      - binary_sensor.bed_dimitri
      - sensor.network_throughput_in_ha
      - sensor.network_throughput_out_ha
      - sensor.wan_in_usg_mbps
      - sensor.wan_out_usg_mbps
      - sensor.network_in_ha
      - sensor.network_out_ha
      - sensor.network_down_nas
      - sensor.network_up_nas
      - light.balcony_ceiling
      - light.bedroom
      - light.bedroom_bed
      - light.bedroom_ceiling
      - light.livingroom
      - light.dressroom
      - light.office
      - media_player.buero_musik_main
      - media_player.receiver_livingroom
```

### Grafana
To create nice graphs and statistics out of the InfluxDB, we use Grafana.

Get the user id:
```bash
id -u 
```
Enter the number below in the field `user:`
Add the following to docker-compose.yml to configure the grafana docker container:

```yaml


  grafana:
    container_name: grafana
    depends_on:
      - influxdb
    environment:
      - GF_SECURITY_ADMIN_USER=username
      - GF_SECURITY_ADMIN_PASSWORD=yoursupersecretpassword
    image: grafana/grafana:latest
    restart: unless-stopped
    user: "1000"
    ports:
      - '3000:3000'
    volumes:
      - ./grafana:/var/lib/grafana
      - /etc/localtime:/etc/localtime:ro
```

Start docker stack:
```bash
docker-compose up -d
```

Go to the Web Interface of Grafana under http://ip-of-home-assistant-server:3000.
Go to "Configuration", then "Data Sources", choose "Add Data Source" then choose "Influx DB".
Enter the username and password of the InfluxDB. The URL for the InfluxDB database is http://ip-of-home-assistant-server:8086 and the database name is `smart_home`.


</p>
</details>


## Climate <a name="climate" href="https://github.com/Burningstone91/smart-home-setup#climate"></a>
### Basic Explanation of Setup
At our home we have floor heating, which is controlled by an outside temperature sensor from the landlord. So there's no automations for setting a thermostat or turning off heating when we leave (it's anyway not efficient to turn off floor heating for only a few hours). I do however have some automations to notify me about mold conditions, good opportunity to open the windows and ventilate the house, a window left open for too long and an automation to turn on/off the dehumidifier when someone opens/closes a window in the same room. And also some automations related to weather conditons, like close windows when rain is coming.

### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:33%;">
3x Xiaomi Temp/Humidity Sensor
</td>
<td align="center" style="width:34%;">
1x IKEA Tradfri Plug (Dehumidifier)
</td>
<td align="center" style="width:33%;">
15x Xiaomi Door/Window Sensor
</td>
</tr>

<tr>
<td align="center" style="width:33%;">
<img src="git-pictures/device_pictures/xiaomi_temp.png" raw=true height="150" alt="Philips Hue" />
</td>
<td align="center" style="width:34%;">
<img src="git-pictures/device_pictures/ikea_plug.jpg" raw=true height="150" alt="IKEA Plug" />
</td>
<td align="center" style="width:33%;">
<img src="git-pictures/device_pictures/xiaomi_door.png" raw=true height="150" alt="Hue Motion" />
</td>
</tr>

<tr><td colspan="3">
There's a Xiaomi Door/Window sensor on each door and window in the house. Temperature and Humidity are measured by the Aeotec Multisensor, which are used for motion detection as well. In addition there are 3x Xiaomi Temp/Humidity sensors placed in rooms without one of the Aeotec Multisensors. The dehumidifier is "smart" by itself, I can set a target humidity and it will automatically start/stop to dehumidify accordingly. The only thing I added is an IKEA smart plug in order to turn it on/off when someone opens/closes the window in the room. 
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

### Adding Temperature/Humidity sensors to the ZigBee network (Xiaomi)
Head over to the Phoscon Web UI under http://ip-of-your-pi:8080/pwa. And execute the following steps to integrate a Xiaomi Temperature/Humidity sensor:

* In Phoscon go to Devices -> Sensors and press "Add new sensor" at the bottom of the page.
* Choose "Other".
* Press and hold the button at the top of the sensor until the blue LED starts to blink.
* The sensor should now show up in Phoscon.

There will be one sensor for temperature, one for humdity and one for the battery level in Home Assistant.

### Adding Door/Window sensors to the ZigBee network (Xiaomi)
Head over to the Phoscon Web UI under http://ip-of-your-pi:8080/pwa. And execute the following steps to integrate a Xiaomi Door/Window sensor:

* In Phoscon go to Devices -> Sensors and press "Add new sensor" at the bottom of the page.
* Choose "Other".
* Reset the device by pressing and holding the setup button (small holle at one side of the larger part of the sensor) until the LED starts to blink.
* The sensor should now show up in Phoscon.

The Xiaomi Door/Window sensors are a bit tricky to pair. What helped me was to continuously trigger the sensor after holding the setup button by rapidly opening/closing the door/window.

There will be a binary sensor for the status of the sensor and one for the battery level in Home Assistant.

### Adding IKEA Tradfri smart plug to the ZigBee network (Xiaomi)
Head over to the Phoscon Web UI under http://ip-of-your-pi:8080/pwa. And execute the following steps to integrate a IKEA Tradfri smart plug:

* In Phoscon go to Devices -> Lights and press "Add new lights" at the bottom of the page.
* Reset the device by pressing and holding the setup button (small holle at one side of plug) until the LED starts to blink.
* The plug should now show up in Phoscon.

There will be a switch in Home Assistant.

### Configure Weather in Home Assistant (Meteo Swiss)
I use the the [Meteo Swiss custom component](https://github.com/websylv/homeassistant-meteoswiss). This is a weather integration for Switzerland and it delivers pretty good results. It can be installed through the [Home Assistant Community Store (HACS)](https://github.com/hacs/integration). The configuration is explained in the github repo of the component and it's pretty straightforward anyway.

### Notification on Window left open
I use the following automation, which sends me a notification when a window is left open longer than a specified time. The time is determined by the month. In January, February and December it's 5 minutes, in March and November 10 minutes, in April, May, September and October 15 minutes, and in June, July and August 25 minutes. 

[Notify on Window Left Open](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/climate.yaml#L41)

### Notification on Window left open
I use the following automation, which sends me a notification when a window is left open when it starts to rain. The notification contains the friendly names of the windows that are open.

First create a group containing all windows/doors leading to the outside:

```yaml
group:
  windows_doors_outside:
    name: Fenster
    entities:
      - binary_sensor.window_bathroomlarge
      - binary_sensor.window_bedroom
      - binary_sensor.window_dressroom
      - binary_sensor.window_kitchen
      - binary_sensor.window_livingroom
      - binary_sensor.window_office
      - binary_sensor.door_livingroom
      - binary_sensor.door_kitchen
      - binary_sensor.door_main
```

Then the automation [Notify on Window Left Open When Rain](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/climate.yaml#L112)

This triggers when the weather entity changes to any of the rainy states.

### Turn off dehumidifier when window in same room is opened
I use the following automation to turn of the dehumidifier when the window in the same room is opened and turn it back on when the window is closed. There is a condition to only execute it when the dehumidifier is on when the window is opened.

[Turn on/off Dehumidifier on Window Open/Close](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/climate.yaml#L136)


</p>
</details>



## Household Tasks <a name="household-tasks" href="https://github.com/Burningstone91/smart-home-setup#household-tasks"></a>
To keep track of the various tasks to be done around the house, I setup some sensors and automations to notify me and my wife about tasks that haven't been done for the predefined period. When one of us completes the task, he can push the "done" button in the automation. This will send a little "thank you" message to the person that did the task, clears the notification for the other person and sends a notification to the other person that the task has already been done. The sensor has an attribute that that tracks the user that marked the task as solved. 

<details><summary>Step-by-step Guide</summary>
<p>
First create a lovelace template for the tasks. This template creates a button that when pressed creates an MQTT sensor with the name of the task. After the sensor has been created, another click will mark the task as solved. The button shows the number of days per cycle of the task and how many days before the task is due the users should be notified. I got this idea from this post on the Home Assistant forum [Chores - Keep track using HA](https://community.home-assistant.io/t/chores-keep-track-using-ha/153796/15).

The template requires [lovelace gen](https://github.com/thomasloven/hass-lovelace_gen). 

```yaml
# lovelace_gen

{% set entity = 'sensor.'+sensor_name %}

type: 'custom:button-card'
entity: {{entity}}
name: {{name}}
icon: {{icon}}
label: >
  [[[ return variables.var.label ]]]
show_label: true
custom_fields:
  status: >
    [[[ return '<span style="display: inline-block; color: white; background: '+variables.var.color+'; padding: 0 5px; border-radius: 5px;">'+variables.var.days_left+'</span>' ]]]
styles:
  grid:
    - grid-template-areas: '"i n status" "i l status"'
    - grid-template-columns: 15% 1fr 1fr
    - grid-template-rows: 1fr 1fr
  icon:
    - color: >
        [[[ return variables.var.color ]]]
  label:
    - color: var(--disabled-text-color)
    - justify-self: start
  name: 
    - justify-self: start
variables:
  var: >
    [[[
      let colors = {};
      colors["success"] = "#8BC24A";
      colors["warning"] = "#FFC107";
      colors["error"] = "#FF5252";
      colors["disabled"] = "var(--disabled-text-color)";
      
      let result = {};
      result.label = "Aufgabe erstellen";
      result.color = colors["disabled"];
      result.days_left = "";
      let date;
      let seconds;
      let timestamp;
      let time;
      let minutes;
      let hours;
      let days;
      
      if (states['{{entity}}']) {
        if (entity.state != 'unknown') {
          date = entity.state;
          seconds = new Date(date);
          timestamp = (seconds.getTime()) / 1000;
          time = (Date.now() / 1000) - timestamp;
          minutes = Math.floor(((time % 3600) / 60));
          hours = Math.floor(((time % 86400) / 3600));
          days = Math.floor((time / 86400));
          
          result.color = colors["success"];

          // LAST TRIGGER
          if (time < 60)
            result.label = 'weniger als 1 Minute';
          else if (days == 1)
            result.label = '1 Tag her';
          else if (days > 1)
            result.label = days+' Tage her';
          else if (hours >= 1)
            result.label = hours+' Stunden her';
          else if (hours < 1)
            result.label = minutes+(minutes > 1 ? ' Minuten' : ' Minute');
          
          // DAYS LEFT
          result.days_left = Math.round(((timestamp + ({{cycle_days|int}}*86400)) - (Date.now()/1000)) / 86400);
          if (result.days_left <= {{warning_before|int}}) {
            result.color = colors["warning"];
          }
          if (result.days_left <= 0) {
            result.color = colors["error"];
          }
          result.days_left = result.days_left + (result.days_left == 1 ? " Tag übrig" : " Tage übrig");

        } else {
          result.label = "Klicken zum Erledigen";
        }
      }
      return result;
      
    ]]]
tap_action:
  confirmation:
    text: >
      [[[
        if (!states['{{entity}}'])
          return 'Entität {{entity}} wird erstellt.'
        else
          return '{{name}} wirklich als erledigt markieren?'
      ]]]
  action: call-service
  service: mqtt.publish
  service_data:
    topic: >
      [[[
        if (!states['{{entity}}'])
          return 'homeassistant/sensor/{{sensor_name}}/config'
        else
          return 'homeassistant/sensor/{{sensor_name}}/state'
      ]]]
    payload: >
      [[[
        var timestamp = Date.now();
        var time = new Date(timestamp).toISOString();

        if (!states['{{entity}}'])
          return '{ "name": "{{sensor_name}}", "state_topic": "homeassistant/sensor/{{sensor_name}}/state", "value_template": "\{\{ value_json.state \}\}", "device_class": "timestamp", "json_attributes_topic": "homeassistant/sensor/{{sensor_name}}/state", "json_attributes_template": "\{\{ value_json.attributes | tojson \}\}" }'
        else
          return '{ "state":"' + time + '", "attributes": { "cycle_days": {{cycle_days}}, "warning_before": {{warning_before}} } }'
      ]]]
    retain: true

```

And here a sample button for a task to change the bed sheets every 14 days and notify 1 day before the task is due. Using this button will create a sensor called `sensor.chore_change_bed_sheets`.

```yaml
cards:
  - !include
    - ../../templates/household_task.yaml
    - name: Change Bed Sheets
      sensor_name: chore_change_bed_sheets
      icon: mdi:bed
      warning_before: 1
      cycle_days: 14
```

Afterwards create a group containing all the household tasks. E.g.

```yaml
group:
  household_tasks:
    name: Haushaltsaufgaben
    entities:
      - sensor.chore_clean_dust
      - sensor.chore_vacuum_clean
      - sensor.chore_clean_floor_wet
      - sensor.chore_oil_floor
      - sensor.chore_dechalk
      - sensor.chore_clean_covers
      - sensor.chore_clean_curtains
      - sensor.chore_clean_window_frames
      - sensor.chore_clean_windows
      - etc.
```

Then the automation to notify the everyone that the task is due. Please note, this example is for the Android companion app, the iOS app handles actionable notifications differently. 

[Notify on Household Task Due](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/household.yaml#L41)

Then the automation that waits for someone to mark the task as solved by pressing the done button in the notification. This then updates the sensor with the name, current time and the name of the executor of the task.

[Mark Task Solved When Confirmed](https://github.com/Burningstone91/smart-home-setup/blob/7b0a9e6e8d19e47a13d662d29533813273a2e130/home-assistant/packages/household.yaml#L75)

And finally some name customization to show nice names in the frontend and the messages. E.g.

```yaml
# Entity Customization
homeassistant:
  customize:
    sensor.chore_vacuum_clean:
      friendly_name: Vacuum the House
```

</p>
</details>


## Security <a name="security" href="https://github.com/Burningstone91/smart-home-setup#security"></a>
### Basic Explanation of Setup

For Security I use the [manual alarm control panel integration](https://www.home-assistant.io/integrations/manual/). To detect activity and trigger the alarm I use the Xiaomi Door Sensor on every door and window, and the motion sensors in the rooms. In addition I use Xiaomi Water Leak Sensors in every bathroom, the storageroom and below the kitchen sink to warn me about water leaks.

### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:50%;">
???? Cameras ????
</td>
<td align="center" style="width:50%;">
4x Xiaomi Water Leak Sensor
</td>
</tr>

<tr>
<td align="center" style="width:50%;">
<img src="git-pictures/device_pictures/.jpg" raw=true height="100" alt="Camera" />
</td>
<td align="center" style="width:50%;">
<img src="git-pictures/device_pictures/xiaomi_water_leak.png" raw=true height="200" alt="Xiaomi Water Leak Sensor" />
</td>
</tr>

<tr><td colspan="2">
The water leak sensors are placed in every place a water leak could occur :).
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

### Setup Manual Alarm Control Panel
Configure the the [manual alarm control panel integration](https://www.home-assistant.io/integrations/manual/) according to the docs. Here's an example from my system:

```yaml
alarm_control_panel:
  - platform: manual
    name: Home Alarm
    code: !secret alarm_code
    arming_time: 30
    trigger_time: 120
    delay_time: 20
    disarmed:
      trigger_time: 0
    armed_home:
      delay_time: 0
      arming_time: 0
```
### Adding water leak sensors to the ZigBee network (Xiaomi)
Head over to the Phoscon Web UI under http://ip-of-your-pi:8080/pwa. And execute the following steps to integrate a Xiaomi Water Leak Sensor:

* In Phoscon go to Devices -> Sensors and press "Add new sensor" at the bottom of the page.
* Choose "Other".
* Enable Pairing Mode on the device by pressing on the button on top of the sensor for at least 5 seconds.

### Arm When Everyone Gone
This automation sets the alarm control panel to `armed_away` when everyone left the house. First create a group containing all household members.

```yaml
group:
  family:
    name: Familie
    entities:
      - person.him
      - person.her
```
Then use the automation
[Arm Away When Everyone Gone](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L36).

### Arm When Sleep Mode is activated
This automation sets the alarm control panel to `armed_home` when the the sleep mode is activated.
[Arm Home When Sleep Mode Activated](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L65)

### Disarm When Someone Arrives or Sleep Mode Is Deactivated
This automation disarms the alarm when someone arrives at home.
[Disarm When Someone Arrives](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L50)

### Notify On Alarm Status Change
This automation notifies us when the alarm panel is armed/disarmed.
[Notify on Alarm Status Change](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L130)

### Trigger Alarm
These two automations (one for armed home, one for armed away) trigger the alarm when one of the configured sensors detects activity (motion, door opened).
[Trigger Alarm Armed Home](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L154)
[Trigger Alarm Armed Away](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L178)

### Alert When House is Insecure
For important repeating notifications we use the [alert integration](https://www.home-assistant.io/integrations/alert/), this way we get notified until the issue has been resolved (e.g. a notification is sent every 5 minutes until the configured binary_sensor is off). This alert sends a repeating, actionable notification when nobody is home and the alarm panel is not armed. The alarm can be activated by pressing the button in the actionable notifation.
The binary_sensor that indicates when nobody is home and the alarm is disarmed for more than 1 minute:
[Binary Sensor Nobody Home Alarm Disarmed](https://github.com/Burningstone91/smart-home-setup/blob/9d3b0c314f7d686e709fd94936dca02677282eef/home-assistant/packages/security.yaml#L17)

[Nobody Home And Alarm Disarmed](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L214)

The corresponding automation for the actionable notification action:
[Arm Alarm When Confirmed By Mobile](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L95)

### Alert When Alarm Has Been Triggered
This alert sends a repeating, actionable notification when the alarm has been triggered. The alert can be ignored by pressing the button in the actionable notification. The alarm panel will then be set to the correct state based on home presence and sleep mode.
[Alarm Triggered](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L233)
The corresponding automation for the actionable notification action:
[Disable Alarm When Confirmed By Mobile](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L109)

### Alert When Water Lead Detected
This alert sends a repeating notification when a water leak has been detected. 
[Waterleak Detected](https://github.com/Burningstone91/smart-home-setup/blob/a3ca6a1a2546a5bb87ec3fb4c8807926559d3e0f/home-assistant/packages/security.yaml#L250)

</p>
</details>

## Home Cinema <a name="home-cinema" href="https://github.com/Burningstone91/smart-home-setup#home-cinema"></a>
### Basic Explanation of Setup
We have a small "Home Cinema" in the living room with an Epson projector, a 107" fixed screen, a Denon AVR and a pair of Dynaudio stand speakers. To play media there's a Raspberry Pi 4 running Libreelec, a Nintendo Switch and a Box from our cable provider for TV.  Home Assistant is used to set the lights based on the current activity of the Logitech Harmony Remote, brighten/dim the lights on pause/play and pause/play on a phone call.

### Hardware Used
<table align="center" border="0">
<tr>
<td align="center" style="width:50%;">
Logitech Harmony Hub
</td>
<td align="center" style="width:50%;">
Denon AVR-X2200W
</td>
</tr>

<tr>
<td align="center" style="width:50%;">
<img src="git-pictures/device_pictures/harmony.png" raw=true height="120" alt="Camera" />
</td>
<td align="center" style="width:50%;">
<img src="git-pictures/device_pictures/denon_avr.png" raw=true height="150" alt="Xiaomi Water Leak Sensor" />
</td>
</tr>
<tr><td colspan="2">
Everything is controlled by a Logitech Harmony Remote (which I plan to replace with the YIO remote once I get the time). I integrated the Denon AVR into Home Assistant to easily be able to control the volume from Home Assistant.
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

### Configure Logitech Harmony Remote in Home Assistant
To use the Logitech Harmony Hub with Home Assistant, we can use the [Logitech Harmony Hub integration](https://www.home-assistant.io/integrations/harmony/)
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "Logitech Harmony Hub" and click on it.
Enter the IP of your Harmony Hub in the field "Host".
Enter the name of your Hub set in the Logitech app in the field "Hub name" and press "SUBMIT".

You should now have an entity `remote.name_of_your_hub` and a file `harmony_XXXX.conf` should be created in the same directory as configuration.yaml. It contains the configuration of the Logitech Harmony Remote such as the commands for the different devices.

### Setup Emulated Roku
Because Home Assistant can not detect when a button has been pressed on the Harmony Remote, we can use the [Emulated Roku integration ](https://www.home-assistant.io/integrations/emulated_roku/) as a workaround. The emulated Roku can be added to the Logitech Harmony Remote and then you add the Roku to the activity you want to know button presses for. Now you assign an action on the Roku to any of the buttons for this activity. Home Assistant will see an event when this button has been pressed, as you can see in the below automations. 

#### Configure via UI
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "Emulated Roku" and click on it.
Enter a name and "8060" in the field "Port". Then hit Submit

#### Configure via Configuration Files
Add the following to your configuration:

```yaml
emulated_roku:
  servers:
    - name: Roku
      listen_port: 8060
      host_ip: ip-of-ha
```

Go to http://ip-of-ha:8060. If it was sucessful you should see a page with some details about the emulated Roku device.

#### Harmony Hub can't see emulated Roku
In some cases the Harmony Hub can't see the emulated Roku device due to different VLANs, multicast issues or similar. In my case the Harmony Hub and Home Assistant are in a separate VLAN. To overcome this issue you can use a Linux Laptop or Desktop, put it on the same VLAN as the Harmony Hub and advertise the emulated Roku from there, then the Harmony Hub is able to see the emulated Roku device.

1. Install aiohttp.
```bash
pip3 install aiohttp
```
2. Copy the advertise script from [here](https://github.com/Burningstone91/smart-home-setup/emulated-roku-script).
3. Navigate to the folder holding the advertise.py file.
4. Execute the following command.
```bash
python3 advertise.py --api_ip=ip-of-home_assistant --api_port=8060 --name=name-defined-for-emulated-roku-device
```
5. Search for the Roku device on the Harmony Remote.
6. You can delete the emulated roku script as it is no longer needed after sucessful pairing.


### Set Home Cinema Light based on Harmony Activity
We set the light color and brightness based on the currently active scene, e.g. for "Music" we play a colorloop, for "Movies" the light is dim and orange etc. For this we have a script, which is called by multiple automations.

Script:
[Set lights based on Harmony activity](https://github.com/Burningstone91/smart-home-setup/blob/5f97f97020edd0402e7d48e4b8aee1ebffc81c81/home-assistant/packages/home_cinema.yaml#L89)

And the automation that calls the script whenever the Harmony Activity changes.
[Change lights when Harmony activity changes](https://github.com/Burningstone91/smart-home-setup/blob/5f97f97020edd0402e7d48e4b8aee1ebffc81c81/home-assistant/packages/home_cinema.yaml#L3)

### Brighten/Dim Light on Pause/Play
When the Pause button on the Harmony Remote has been pressed (detected through the emulated Roku), the lights brighten up to 100%, when the Play button is pressed the lights change back according to the currently running activity.

[Brighten/Dim Light on Pause/Play](https://github.com/Burningstone91/smart-home-setup/blob/5f97f97020edd0402e7d48e4b8aee1ebffc81c81/home-assistant/packages/home_cinema.yaml#L17)

### Pause/Play on Phone Call
When my wife or I receive a phone call (detected through Home Assistant Companion App) while we are home and the Home Cinema is running, the currently playing media is paused and then resumed once the phone call ends.

[Pause/Play on Phone Call](https://github.com/Burningstone91/smart-home-setup/blob/5f97f97020edd0402e7d48e4b8aee1ebffc81c81/home-assistant/packages/home_cinema.yaml#L42)

### Configure Denon AVR in Home Assistant
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "Denon AVR" and click on it.
Enter the IP of your Denon AVR in the field "IP address".
Enter your username and password and press "SUBMIT"

</p>
</details>



## Multiroom Media <a name="multiroom-audio" href="https://github.com/Burningstone91/smart-home-setup#multiroom-audio"></a>
### Basic Explanation of Setup

![Alt text](/git-pictures/multiroom_audio_overview.png?raw=true "Multiroom Audio Overview")

### Mopidy/Snapcast

<details><summary>Step-by-step Guide</summary>
<p>

#### Snapserver
Create a folder called `snapserver` in the same directory as home-assistant, appdaemon etc. and put the files from [here](https://github.com/Burningstone91/smart-home-setup/tree/master/snapserver) into this directory. Create a subfolder called "snapfifo". Add a file called `snapserver.conf`, this holds the configuration for the different streams that will be available to stream to the snapclients. Below is an example with two Spotify Accounts and four pipes from mopidy (livingroom, bedroom, office and TTS).

```conf
[server]

[http]

doc_root = /usr/share/snapserver/snapweb

[tcp]

[stream]

source = librespot:///librespot?name=House&devicename=House&username=some-username&password=some-password&killall=false&bitrate=320&volume=100&params=--zeroconf-port%205353
source = librespot:///librespot?name=Multiroom&devicename=Multiroom&username=some-username&password=some-password&killall=false&bitrate=320&volume=100&params=--zeroconf-port%205353
source = pipe:///run/snapserver/tts_fifo?name=TTS
source = pipe:///run/snapserver/office_fifo?name=Office
source = pipe:///run/snapserver/livingroom_fifo?name=Livingroom
source = pipe:///run/snapserver/bedroom_fifo?name=Bedroom

[logging]
```

Add the following to `docker-compose.yml`:

```yaml
  snapserver:
    build: 
      context: ./snapserver
    container_name: snapserver
    environment:
      - DEVICE_NAME=MultiRoom
    image: burningstone/snapserver
    ports:
      - "1704:1704"
      - "1705:1705"
      - "1780:1780"
      - "5353:5353"
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./snapserver/snapserver.conf:/etc/snapserver.conf
      - ./snapserver/snapfifo:/run/snapserver/
```

Build the docker container with `docker-compose build snapserver` and start it with `docker-compose up -d`. Install Snapcast on your Android phone. Point it to the instance running snapserver, you should now see 6 differnt Streams available, two for Spotify and four for Mopidy. In Spotify Connect you should now see a new device available with the respective accounts configured in `snapserver.conf`. This will be used to play Spotify Connect in multiple rooms.

#### Mopidy
Create a folder called `mopidy` in the same directory as home-assistant, appdaemon etc. and put the files from [here](https://github.com/Burningstone91/smart-home-setup/tree/master/mopidy/docker) into this directory. Create a subfolder for each room and one for TTS, in my case `livingroom`, `bedroom`, `office` and `tts`. Add a file called `mopidy.conf` in each of these subfolder with the following content:

```conf
[core]
data_dir = /var/lib/mopidy

[mpd]
hostname = 0.0.0.0

[http]
hostname = 0.0.0.0

[iris]
country = CH
locale = de_CH

[local]
media_dir = /var/lib/mopidy/media

[audio]
output = audioresample ! audioconvert ! audio/x-raw,rate=48000,channels=2,format=S16LE ! wavenc ! filesink location=/run/snapserver/livingroom_fifo

[spotify]
enabled = false

[spotify-web]
enabled = false

[soundcloud]
enabled = false

[file]
enabled = false

[gmusic]
enabled = false

[moped]
enabled = false

[pandora]
enabled = false

[youtube]
enabled = false
```

Where you adjust `livingroom_fifo` for each room accordingly. Make sure that the fifo has the same name as you configured in `snapserver.conf` above. 

To add spotify go to https://mopidy.com/ext/spotify/ to authenticate your Spotify account with their API.
Press green button and copy the client_id and the client_secret in the box below the button.

Add the following to the above configured mopidy.conf files:

```conf
[spotify]
enabled = true
client_id = client_id_generated_in_previous_step
client_secret = client_secret_generated_in_previous_step
username = spotify_username_used_to_authenticate
password = password_of_spotify_user
```

Now add a section to the `docker-compose.yml` file for each Mopidy instance, like this:

```yaml
  mopidy_bedroom:
    build:
      context: ./mopidy/docker
    container_name: mopidy_bedroom
    image: burningstone/mopidy
    ports:
      - "6681:6680"
      - "6601:6600"
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./snapserver/snapfifo:/run/snapserver/
      - ./mopidy/bedroom/mopidy.conf:/config/mopidy.conf
      - ./music:/var/lib/mopidy/media:ro
      - ./mopidy/local:/var/lib/mopidy/local

  mopidy_livingroom:
    build:
      context: ./mopidy/docker
    container_name: mopidy_livingroom
    image: burningstone/mopidy
    ports:
      - "6682:6680"
      - "6602:6600"
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./snapserver/snapfifo:/run/snapserver/
      - ./mopidy/livingroom/mopidy.conf:/config/mopidy.conf
      - ./music:/var/lib/mopidy/media:ro
      - ./mopidy/local:/var/lib/mopidy/local

  mopidy_office:
    build:
      context: ./mopidy/docker
    container_name: mopidy_office
    image: burningstone/mopidy
    ports:
      - "6683:6680"
      - "6603:6600"
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./snapserver/snapfifo:/run/snapserver/
      - ./mopidy/office/mopidy.conf:/config/mopidy.conf
      - ./music:/var/lib/mopidy/media:ro
      - ./mopidy/local:/var/lib/mopidy/local

  mopidy_tts:
    build:
      context: ./mopidy/docker
    container_name: mopidy_tts
    image: burningstone/mopidy
    ports:
      - "6680:6680"
      - "6600:6600"
    restart: unless-stopped
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./snapserver/snapfifo:/run/snapserver/
      - ./mopidy/tts/mopidy.conf:/config/mopidy.conf
```
Make sure that you configure different ports for each mopidy instance, otherwise you'll get port conflicts. Also make sure that the line `./mopidy/livingroom/mopidy.conf:/config/mopidy.conf` matches the respective directory where you put the mopidy.conf file from above. For the rooms you can see two additional volumes being mapped, `./music:/var/lib/mopidy/media:ro` which is an NFS mount of a remote NAS on the host system and `./mopidy/local:/var/lib/mopidy/local` which is used by Mopidy to save metadata about local media. This way you can play local media files on each room instance from the same soruce. 

Build each container with `docker-compose build mopidy_tts` and then run `docker-compose up -d`. You should now be able to reach the Mopidy web interface through http://ip-of-mopidy-server:6680 (mopidy tts instance) where you change the port according to which mopidy instance you wanna access. 

Now with Snapserver and Mopidy setup and configured, you should be able to play music on any of the Mopidy instances, change the source from one of the snapclients to this Mopidy instance and you should hear the music from the snapclient.

</p>
</details>

### Music Only Client (Volumio)
#### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:33%;">
3x Pi Zero W
</td>
<td align="center" style="width:34%;">
2x HifiBerry DAC
</td>
<td align="center" style="width:33%;">
1x HifiBerry Mini Amp
</td>
</tr>

<tr>
<td align="center" style="width:33%;">
<img src="git-pictures/device_pictures/pi_zero_w.jpg" raw=true height="250" alt="Pi Zero W"/>
</td>
<td align="center" style="width:34%;">
<img src="git-pictures/device_pictures/hifiberry_dac_zero.jpg" raw=true height="250" alt="HifiBerry DAC Zero" />
</td>
<td align="center" style="width:33%;">
<img src="git-pictures/device_pictures/hifiberry_amp_mini.jpg" raw=true height="250" alt="HifiBerry Mini Amp" />
</td>
</tr>

<tr><td colspan="3">
In rooms without a display (bathroom, balcony, etc.) we use a Pi Zero W with [Volumio](https://volumio.org/) as a media player for music. The Pi Zeros are either coupled with a HifiBerry DAC and an existing amplifier + speakers or with a HifiBerry Amp and passive speakers. In Volumio we use the Spotify Connect Plugin and the Snapcast Plugin. This way one can either connect through Spotify Connect directly to play music in this specific room or through Snapcast to play in multiple rooms.
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

#### Volumio
Follow the instructions from HifiBerry to mount the HifiBerry DAC/Amp onto the Pi.
1. Download Volumio version 2.729 (Somehow newer versions don't work with the Pi directly, but you can install the old version and update, this works well) from here -> http://updates.volumio.org/pi/volumio/2.729/volumio-2.729-2020-03-18-pi.img.zip
2. Flash the image to an SD card and insert it into the Pi. Then plug the power cable into the Pi.
3. Wait a few minutes until you see a WiFi hotspot created by Volumio. To access the hotspot use username: volumio and password: volumio2
4. Go to http://volumio.local
5. Follow the instructions to configure the initial settings. DON'T enable I2S DAC yet when using a HifiBerry DAC.
6. Restart Volumio
7. Go to Settings -> Playback -> Enable I2S DAC -> Choose Adafruit UDA1334A (HifiBerry DAC+ Zero) and press Save.
8. Update Volumio through Settings -> System -> Search for Updates

#### Spotify Connect Plugin
In Volumio go to Plugins and install the plugin "Volumio Spotify Connect2".

#### Snapcast Plugin
I had some issues with the official plugin available in Volumio, maybe because it is a few versions behind. That's why I install the newer version of the plugin manually.
1. Go to http://ip-of-volumio-pi/dev/ to enable SSH. 
2. SSH into Volumio `ssh volumio@ip-of-volumio-pi`, password is `volumio`.
3. Clone repo `git clone https://github.com/Saiyato/volumio-snapcast-plugin.git`
4. `cd volumio-snapcast-plugin`
5. `rm volumio-snapcast-plugin.zip`
6. `volumio plugin install`, wait for successful install message and restart Volumio.
7. In Volumio go to Settings -> Plugins -> Installed Plugins -> Activate the SnapCast plugin and go to its settings.
8. Disable SnapServer, for SnapClient enable custom host and put the IP of the machine running Snapserver.
9. Choose HifiBerry DAC+ for "Soundcard To Use For Playback" 

#### Configure Volumio integration in Home Assistant
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "volumio" and click on it.
Enter the IP of the Pi in the field "Host" and hit "SUBMIT".

</p>
</details>


### Audio/Video Client (Libreelec)
#### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:33%;">
Raspberry Pi 4
</td>
</tr>

<tr>
<td align="center" style="width:33%;">
<img src="git-pictures/device_pictures/pi4.jpg" raw=true height="250" alt="Pi Zero W"/>
</td>
</tr>

<tr><td colspan="3">
In rooms with a display (livingroom, bedroom, etc.) we use a Pi 4 with [Libreelec](https://libreelec.tv/) as a media player for music and video. In Kodi we use the Spotify Connect Plugin and the Snapclient Plugin. This way one can either connect through Spotify Connect directly to play music in this specific room or through Snapcast to play in multiple rooms.
</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

#### Libreelec
1. Download latest Libreelec image from https://libreelec.tv/downloads_new/
2. Flash the image to an SD card and insert it into the Pi. Then plug the HDMI and power cable into the Pi.
3. Once Libreelec booted up go to Settings -> Libreelec -> Audio -> Audio Output and choose ALSA

#### Spotify Connect Add-On
In Libreelec go to Add-Ons -> Services -> Install Librespot Add-On

#### Snapclient Add-on
1. In Libreelec go to Add-Ons -> Services -> Install Snapclient Add-On.
2. SSH into Libreelec `ssh root@ip-of-libreelec-pi`, password is `libreelec`.
3. Change password with `passwd`.
4. Adjust the snapclient start file, otherwise the snapserver can't be found if it is not on the same network.
5. `nano /storage/.kodi/addons/service.snapclient/bin/snapclient.start`
6. Remove `ID` from `hostID` in the line and save.
```
[ -n "$sc_h" ] && sc_H="--hostID $sc_h"
```
7. Reboot the Pi.
8. Configure the Snapclient Add-On through the UI, in the field "HostID", enter the IP of the machine running snapserver.

#### Configure Kodi integration in Home Assistant
In Libreelec go to Settings -> Services -> Control -> Enable "Allow remote control via HTTP"
In Home Assistant on the sidebar click on "Configuration" then on "Integrations". Click on "+ ADD INTEGRATION" in the bottom right corner, search for "kodi" and click on it.
Enter the IP of the Pi in the field "Host" and hit "SUBMIT".

#### Add Kodi to Logitech Harmony Remote
Open the Logitech Harmony app on the phone and add a new entertainment device. Choose manufacturer "Microsoft" and Model "Kodi".
In Libreelec go to Settings -> Libreelec -> Bluetooth, a new device should appear called "Harmony Keyboard", clickt it and choose "pair".

#### Setup a Centralized DB for Kodi with a Synology NAS
To keep watched state etc. of my movies and tv-shows synced across my Kodi devices, I setup a centralized DB on the Synology NAS.
1. Login to the web interface of the Synology NAS.
2. Install MariaDB 10 and set a strong password. Open the settings and check the box "Enable TCP/IP connection"
3. Install phpMyAdmin.
4. Login to phpMyAdmin with username `root` and the password used for MariaDB configured in step 2.
5. Go to the tab "User accounts" and press "Add user account".
6. Configure a username and password for the Kodi clients.
7. Check the box "Grant all privileges on wildcard name (username\_%).
8. Check the box "Check all" next to "Global privileges".
9. Press "Go" in the bottom right corner.

Now on the first Kodi instance add file called advancedsettings.xml to configure the connection to the DB.
1. SSH into Libreelec `ssh root@ip-of-libreelec-pi`.
2. `nano ~/.kodi/userdata/advancedsettings.xml`
3. Add the following content, replace the capital strings with your respective info and save.

```xml
<advancedsettings>
  <videodatabase>
    <type>mysql</type>
    <host>IP_OF_SYNOLOGY_NAS</host>
    <port>3307</port>
    <name>kodi_video</name>
    <user>USERNAME_KODI_CLIENT</user>
    <pass>PASSWORD_KODI_CLIENT</pass>
  </videodatabase>
  <musicdatabase>
     <type>mysql</type>
     <host>IP_OF_SYNOLOGY_NAS</host>
     <port>3307</port>
     <name>kodi_music</name>
     <user>USERNAME_KODI_CLIENT</user>
    <pass>PASSWORD_KODI_CLIENT</pass>
  </musicdatabase>
  <videolibrary>
    <importwatchedstate>true</importwatchedstate>
    <importresumepoint>true</importresumepoint>
  </videolibrary>
</advancedsettings>
```
4. Reboot the Pi.
5. Add all the media and scrape the information.
For all the other Kodi clients, copy the files "sources.xml", "mediasources.xml" and "advancedsettings.xml" from the userdata folder of the first Pi.
After all these steps you should now be able to pause a video in one room and then resume at the same point in another room. Also the watched status of your episodes will be synced across all instances and movie information etc. is shared across all instances.


</p>
</details>

### Multiroom Audio in Home Assistant

<details><summary>Step-by-step Guide</summary>
<p>

#### Configure Spotify integration in Home Assistant
#### Configure Snapcast integration in Home Assistant
#### Configure MPD (Mopidy) integration in Home Assistant

</p>
</details>


## Appliances <a name="appliances" href="https://github.com/Burningstone91/smart-home-setup#appliances"></a>
### Basic Explanation of Setup

### Hardware used
<table align="center" border="0">
<tr>
<td align="center" style="width:100%;">
1x myStrom Plug
</td>
</tr>

<tr>
<td align="center" style="width:100%;">
<img src="git-pictures/device_pictures/mystrom_plug.png" raw=true height="100" alt="Plug" />
</td>
</tr>

<tr><td colspan="2">
We use the myStrom plug to measure the energy consumption of our dishwasher in order to determine the state of the dishwasher.

</td></tr>
</table>

<details><summary>Step-by-step Guide</summary>
<p>

### Integrate myStrom plug to Home Assistant
We use the [myStrom integration](https://www.home-assistant.io/integrations/mystrom/) to add the plug to Home Assistant.
Place the following in your configuration, where host is the IP of the myStrom plug:

```yaml
switch:
  # Power Metering Plug Dishwaser
  - platform: mystrom
    host: 10.10.70.13
    name: Plug Dishwasher
```

And restart Home Assistant. This will give you a switch called `switch.plug_dishwasher`.

### Measuring and Monitoring Power and Energy consumption
The switch has an attribute that shows the current power consumption, we can use a template sensor to extract the attribute into a separate sensor, which can then be used to calculate energy consumption over time etc.

```yaml
sensor:
  # Extract power attribute from dishwasher plug
  - platform: template
    sensors:
      power_dishwasher:
        friendly_name: Strom Geschirrspüler
        unit_of_measurement: "W"
        device_class: power
        value_template: "{{ state_attr('switch.plug_dishwasher', 'current_power_w') }}"
```

To show the power consumption over time, we can use the [integration integration](https://www.home-assistant.io/integrations/integration/)(no, it's not a typo :D).


```yaml
sensor:
  # Convert power (W) to energy (kWh)
  - platform: integration
    source: sensor.power_dishwasher
    name: energy_dishwasher
    unit_prefix: k
    round: 2
```

### Determine state of Dishwasher
To determine the state of the dishwasher (cleaning, drying etc.) we create an input_select that holds the possible states:

```yaml
input_select:
  status_dishwasher:
  name: Status Geschirrspüler
  options:
    - Sauber #Clean
    - Dreckig #Dirty
    - Läuft #Running
```

Then the automation that changes the input_select.

The logic is as follows:
* Power > 30 W (I monitoried a few cycles to get the values) for 2 minutes AND dishwasher state NOT Running-> Running
* Power < 5 W for 20 minutes AND dishwasher state is Running -> Clean
* Clean for 4 hours -> Dirty

[Determine Dishwasher State](https://github.com/Burningstone91/smart-home-setup/blob/master/home-assistant/packages/kitchen.yaml#L43)

I don't have an automation (yet) to detected the dishwasher has been emptied, as there is no place to put a door sensor that is not disturbing to look at.
</p>
</details>
