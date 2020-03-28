# Burningstone's Smart Home Journey
Installation and Configuration of my Smart Home Setup

## Introduction
I discovered Home Assistant around 2 years ago, installed it, played a bit with it, but didn't really have a need for it at that time. Some Philips Hue bulbs and Dimmers later, I gave Home Assistant another try. This time it got me hooked. I became addicted immediately. This was a bit more than 1 year ago. In this time I started to learn Python, YAML, wrote my own code for automations, etc. and setup a system that works pretty stable and covers my current needs. You can find my current setup [here](https://github.com/Burningstone91/smart-home).

Now I will build my whole setup from scratch, add some new features and hardware and you can follow me on this journey. I will keep adding my new configuration and the corresponding documentation continuously to this repo. You may ask, why I do this when I have a stable, running system? First, this will be a documentation that I can use to give me an overview of my system and in worst case (house burnt down + wife lost USB stick attached to key + I lost USB stick attached to key + I lost external drive that I always carry in my backpack, yes I know I'm paranoid :P) help me to setup everything again. Second, I hope that other people can profit from this, learn from my journey, use parts of my config in their own system or at least it helps them to solve one of their issues. And third, my current setup grew quite a lot in complexity. Due to my skills evolving and learning new tricks or methods to do certain things, it became inconsistent in regards to naming and in how and where things are configured and the documentation is lacking heavily. 

!!!WARNING!!! I'm by no means a programmer and I don't work as a professional in IT or something IT related. I'm just passionate about home automation, programming, IoT and technology in general.

My "Server" is an Intel NUC with an i3-7100U CPU, 8 GB of RAM and a 1 TB SSD (I use it for other virtual machines as well). The Smart Home runs inside an Ubuntu virtual machine in Proxmox.

If you find any information here useful feel free to buy me a coffee :)

<a href="https://www.buymeacoff.ee/u89Ao5n" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee" style="height: 19px !important;width: 68px !important;" ></a>

## Overview
I will explain here the different parts of my home automation system and how I set them up. For each part, I will talk about the hardware involved and how I integrated it into the system and I will also give an explanation on the automations and the corresponding code related to this part. 

* <a href="https://github.com/Burningstone91/smart-home-setup#start">
      Start of my Journey and Basic Setup
  </a>

## Start of my Jouney and Basic Setup<a name="start" href="https://github.com/Burningstone91/smart-home-setup#start">
First some preparations and the install of [Home Assistant](https://www.home-assistant.io/), which will be the core of the home automation system.

### Preparations
First install Docker and Docker-Compose on the host machine following the official instructions online.

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
    image: homeassistant/home-assistant:0.105.2
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

## Setup MQTT Broker
The MQTT broker is the server that hosts the MQTT network. It provides the infrastructure for devices to publish/subscribe to topics. In this setup [Mosquitto](https://mosquitto.org/) is the broker of choice.

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
Create a file called "core.yaml" inside the directory config/packages. Add the following to the file:

```yaml
mqtt:
  broker: 127.0.0.1
  username: [username]
  password: [password]
  discovery: true
```

## Setup AppDaemon - Automation Engine
[AppDaemon](https://appdaemon.readthedocs.io/en/latest/) can be used to write Home Automation apps for Home Assistant in Python. It's an alternative to Home Assistant's inbuilt automations. You can create more complicated automations and reuse the same code for multiple apps. The official AppDaemon documentation provides a [detailed explanation](https://appdaemon.readthedocs.io/en/latest/APPGUIDE.html) on how to create your first app.

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

Stop the docker stack:

```
docker-compose down
```

Add the following to the docker-compose.yml to configure the AppDaemon docker container:

```yaml
  appdaemon:
    container_name: appdaemon
    image: acockburn/appdaemon:4.0.1
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


## Presence Detection
### Basic Explanation of Setup
I use the [person integration](https://www.home-assistant.io/integrations/person/) from Home Assistant to combine a bluetooth device tracker (device attached to my keys) and a gps device tracker (my phone). The docs give a detailed explanation on how the location is determined when multiple device trackers are used. Long story short, when I'm at home, my position is determined first by keys and then by phone. When I'm not home, my position is determined first by phone then by keys.
I also use the [zone integration](https://www.home-assistant.io/integrations/zone/) from Home Assistant to show in which place (work, grocery store, etc.) we are, when we are not home. And I use [Room Assistant](https://www.room-assistant.io/) and the [MQTT Room Presence integration](https://www.home-assistant.io/integrations/mqtt_room/) from Home Assistant to show in which room we are, when we are home.
I'm using the bluetooth device trackers now for around 2 years and I did not have a single false trigger in 2 years. Home Assistant marks us as home before we open the front door and marks us as left 3 min after we left the house.
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

The Nut Mini's are attatched to our keys and I'm soon going to buy some Fitness Bands to replace them. They send a Bluetooth Low Energy (BLE) signal every 3 seconds. There's one Raspberry Pi's as central as possible in every room that I want to automate. The Pi's run [Room Assistant](https://www.room-assistant.io/), which catches these signals and determines the location of the Nut Mini based on the strength of the signal. It talks to Home Assistant through MQTT and if discovery is enabled it will be detected automatically.

<tr><td colspan="2">
