"""Emulated Roku library."""
from asyncio import (
    AbstractEventLoop, DatagramProtocol, DatagramTransport, Task, sleep)
from base64 import b64decode
from ipaddress import ip_address
from logging import getLogger
from os import name as osname
from random import randrange
import socket
from uuid import NAMESPACE_OID, uuid5

from aiohttp import web

_LOGGER = getLogger(__name__)

APP_PLACEHOLDER_ICON = b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAoMBgDTD2"
    "qgAAAAASUVORK5CYII=")

INFO_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" ?>
<root xmlns="urn:schemas-upnp-org:device-1-0">
    <specVersion>
        <major>1</major>
        <minor>0</minor>
    </specVersion>
    <device>
    <deviceType>urn:roku-com:device:player:1-0</deviceType>
    <friendlyName>{usn}</friendlyName>
    <manufacturer>Roku</manufacturer>
    <manufacturerURL>http://www.roku.com/</manufacturerURL>
    <modelDescription>Emulated Roku</modelDescription>
    <modelName>Roku 4</modelName>
    <modelNumber>4400x</modelNumber>
    <modelURL>http://www.roku.com/</modelURL>
    <serialNumber>{usn}</serialNumber>
    <UDN>uuid:{uuid}</UDN>
    </device>
</root>
"""

DEVICE_INFO_TEMPLATE = """<device-info>
    <udn>{uuid}</udn>
    <serial-number>{usn}</serial-number>
    <device-id>{usn}</device-id>
    <vendor-name>Roku</vendor-name>
    <model-number>4400X</model-number>
    <model-name>Roku 4</model-name>
    <model-region>US</model-region>
    <supports-ethernet>true</supports-ethernet>
    <wifi-mac>00:00:00:00:00:00</wifi-mac>
    <ethernet-mac>00:00:00:00:00:00</ethernet-mac>
    <network-type>ethernet</network-type>
    <user-device-name>{usn}</user-device-name>
    <software-version>7.5.0</software-version>
    <software-build>09021</software-build>
    <secure-device>true</secure-device>
    <language>en</language>
    <country>US</country>
    <locale>en_US</locale>
    <time-zone>US/Pacific</time-zone>
    <time-zone-offset>-480</time-zone-offset>
    <power-mode>PowerOn</power-mode>
    <supports-suspend>false</supports-suspend>
    <supports-find-remote>false</supports-find-remote>
    <supports-audio-guide>false</supports-audio-guide>
    <developer-enabled>false</developer-enabled>
    <keyed-developer-id>0000000000000000000000000000000000000000</keyed-developer-id>
    <search-enabled>false</search-enabled>
    <voice-search-enabled>false</voice-search-enabled>
    <notifications-enabled>false</notifications-enabled>
    <notifications-first-use>false</notifications-first-use>
    <supports-private-listening>false</supports-private-listening>
    <headphones-connected>false</headphones-connected>
</device-info>
"""

APPS_TEMPLATE = """<apps>
    <app id="1" version="1.0.0">Emulated App 1</app>
    <app id="2" version="1.0.0">Emulated App 2</app>
    <app id="3" version="1.0.0">Emulated App 3</app>
    <app id="4" version="1.0.0">Emulated App 4</app>
    <app id="5" version="1.0.0">Emulated App 5</app>
    <app id="6" version="1.0.0">Emulated App 6</app>
    <app id="7" version="1.0.0">Emulated App 7</app>
    <app id="8" version="1.0.0">Emulated App 8</app>
    <app id="9" version="1.0.0">Emulated App 9</app>
    <app id="10" version="1.0.0">Emulated App 10</app>
</apps>
"""

ACTIVE_APP_TEMPLATE = """<active-app>
    <app>Roku</app>
</active-app>
"""

MUTLICAST_TTL = 300
MULTICAST_MAX_DELAY = 5
MULTICAST_GROUP = "239.255.255.250"
MULTICAST_PORT = 1900

MULTICAST_RESPONSE = "HTTP/1.1 200 OK\r\n" \
                     "Cache-Control: max-age = {ttl}\r\n" \
                     "ST: roku:ecp\r\n" \
                     "Location: http://{advertise_ip}:{advertise_port}/\r\n" \
                     "USN: uuid:roku:ecp:{usn}\r\n" \
                     "\r\n"

MULTICAST_NOTIFY = "NOTIFY * HTTP/1.1\r\n" \
                   "HOST: {multicast_ip}:{multicast_port}\r\n" \
                   "Cache-Control: max-age = {ttl}\r\n" \
                   "NT: upnp:rootdevice\r\n" \
                   "NTS: ssdp:alive\r\n" \
                   "Location: http://{advertise_ip}:{advertise_port}/\r\n" \
                   "USN: uuid:roku:ecp:{usn}\r\n" \
                   "\r\n"


class EmulatedRokuDiscoveryProtocol(DatagramProtocol):
    """Roku SSDP Discovery protocol."""

    def __init__(self, loop: AbstractEventLoop,
                 host_ip: str, roku_usn: str,
                 advertise_ip: str, advertise_port: int):
        """Initialize the protocol."""
        self.loop = loop
        self.host_ip = host_ip
        self.roku_usn = roku_usn
        self.advertise_ip = advertise_ip
        self.advertise_port = advertise_port
        self.ssdp_response = MULTICAST_RESPONSE.format(
            advertise_ip=advertise_ip, advertise_port=advertise_port,
            usn=roku_usn, ttl=MUTLICAST_TTL)

        self.notify_broadcast = MULTICAST_NOTIFY.format(
            advertise_ip=advertise_ip, advertise_port=advertise_port,
            multicast_ip=MULTICAST_GROUP, multicast_port=MULTICAST_PORT,
            usn=roku_usn, ttl=MUTLICAST_TTL)

        self.notify_task = None  # type: Task
        self.transport = None  # type: DatagramTransport

    def connection_made(self, transport):
        """Set up the multicast socket and schedule the NOTIFY message."""
        self.transport = transport

        sock = self.transport.get_extra_info('socket')  # type: socket
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                        socket.inet_aton(MULTICAST_GROUP) +
                        socket.inet_aton(self.host_ip))

        _LOGGER.debug("multicast:started for %s/%s:%s/usn:%s",
                      MULTICAST_GROUP,
                      self.advertise_ip, self.advertise_port, self.roku_usn)

        self.notify_task = self.loop.create_task(self._multicast_notify())

    def connection_lost(self, exc):
        """Clean up the protocol."""
        _LOGGER.debug("multicast:connection_lost for %s/%s:%s/usn:%s",
                      MULTICAST_GROUP,
                      self.advertise_ip, self.advertise_port, self.roku_usn)

        self.close()

    async def _multicast_notify(self) -> None:
        """Broadcast a NOTIFY multicast message."""
        while self.transport and not self.transport.is_closing():
            _LOGGER.debug("multicast:broadcast\n%s", self.notify_broadcast)

            self.transport.sendto(self.notify_broadcast.encode(),
                                  (MULTICAST_GROUP, MULTICAST_PORT))

            await sleep(MUTLICAST_TTL)

    def _multicast_reply(self, data: str, addr: tuple) -> None:
        """Reply to a discovery message."""
        if self.transport is None or self.transport.is_closing():
            return

        _LOGGER.debug("multicast:reply %s\n%s", addr, self.ssdp_response)
        self.transport.sendto(self.ssdp_response.encode('utf-8'), addr)

    def datagram_received(self, data, addr):
        """Parse the received datagram and send a reply if needed."""
        data = data.decode('utf-8')

        if data.startswith("M-SEARCH * HTTP/1.1") and \
                ("ST: ssdp:all" in data or "ST: roku:ecp" in data):
            _LOGGER.debug("multicast:request %s\n%s", addr, data)

            mx_value = data.find("MX:")

            if mx_value != -1:
                mx_delay = int(data[mx_value + 4]) % (MULTICAST_MAX_DELAY + 1)

                delay = randrange(0, mx_delay + 1, 1)
            else:
                delay = randrange(0, MULTICAST_MAX_DELAY + 1, 1)

            self.loop.call_later(delay, self._multicast_reply, data, addr)

    def close(self) -> None:
        """Close the discovery transport."""
        if self.notify_task:
            self.notify_task.cancel()
            self.notify_task = None

        if self.transport:
            self.transport.close()
            self.transport = None


class EmulatedRokuCommandHandler:
    """Base handler class for Roku commands."""

    KEY_HOME = 'Home'
    KEY_REV = 'Rev'
    KEY_FWD = 'Fwd'
    KEY_PLAY = 'Play'
    KEY_SELECT = 'Select'
    KEY_LEFT = 'Left'
    KEY_RIGHT = 'Right'
    KEY_DOWN = 'Down'
    KEY_UP = 'Up'
    KEY_BACK = 'Back'
    KEY_INSTANTREPLAY = 'InstantReplay'
    KEY_INFO = 'Info'
    KEY_BACKSPACE = 'Backspace'
    KEY_SEARCH = 'Search'
    KEY_ENTER = 'Enter'
    KEY_FINDREMOTE = 'FindRemote'
    KEY_VOLUMEDOWN = 'VolumeDown'
    KEY_VOLUMEMUTE = 'VolumeMute'
    KEY_VOLUMEUP = 'VolumeUp'
    KEY_POWEROFF = 'PowerOff'
    KEY_CHANNELUP = 'ChannelUp'
    KEY_CHANNELDOWN = 'ChannelDown'
    KEY_INPUTTUNER = 'InputTuner'
    KEY_INPUTHDMI1 = 'InputHDMI1'
    KEY_INPUTHDMI2 = 'InputHDMI2'
    KEY_INPUTHDMI3 = 'InputHDMI3'
    KEY_INPUTHDMI4 = 'InputHDMI4'
    KEY_INPUTAV1 = 'InputAV1'

    def on_keydown(self, roku_usn: str, key: str) -> None:
        """Handle key down command."""
        pass

    def on_keyup(self, roku_usn: str, key: str) -> None:
        """Handle key up command."""
        pass

    def on_keypress(self, roku_usn: str, key: str) -> None:
        """Handle key press command."""
        pass

    def launch(self, roku_usn: str, app_id: str) -> None:
        """Handle launch command."""
        pass


class EmulatedRokuServer:
    """Emulated Roku server.

    Handles the API HTTP server and UPNP discovery.
    """

    def __init__(self, loop: AbstractEventLoop,
                 handler: EmulatedRokuCommandHandler,
                 roku_usn: str, host_ip: str, listen_port: int,
                 advertise_ip: str = None, advertise_port: int = None,
                 bind_multicast: bool = None):
        """Initialize the Roku API server."""
        self.loop = loop
        self.handler = handler
        self.roku_usn = roku_usn
        self.host_ip = host_ip
        self.listen_port = listen_port

        self.advertise_ip = advertise_ip or host_ip
        self.advertise_port = advertise_port or listen_port

        self.allowed_hosts = (
            self.host_ip,
            "{}:{}".format(self.host_ip, self.listen_port),
            self.advertise_ip,
            "{}:{}".format(self.advertise_ip, self.advertise_port))

        if bind_multicast is None:
            # do not bind multicast group on windows by default
            self.bind_multicast = osname != "nt"
        else:
            self.bind_multicast = bind_multicast

        self.roku_uuid = str(uuid5(NAMESPACE_OID, roku_usn))

        self.roku_info = INFO_TEMPLATE.format(uuid=self.roku_uuid,
                                              usn=roku_usn)
        self.device_info = DEVICE_INFO_TEMPLATE.format(uuid=self.roku_uuid,
                                                       usn=self.roku_usn)

        self.discovery_proto = None  # type: EmulatedRokuDiscoveryProtocol
        self.api_runner = None  # type: web.AppRunner

    async def _roku_root_handler(self, request):
        return web.Response(body=self.roku_info,
                            headers={'Content-Type': 'text/xml'})

    async def _roku_input_handler(self, request):
        return web.Response()

    async def _roku_keydown_handler(self, request):
        key = request.match_info['key']
        self.handler.on_keydown(self.roku_usn, key)
        return web.Response()

    async def _roku_keyup_handler(self, request):
        key = request.match_info['key']
        self.handler.on_keyup(self.roku_usn, key)
        return web.Response()

    async def _roku_keypress_handler(self, request):
        key = request.match_info['key']
        self.handler.on_keypress(self.roku_usn, key)
        return web.Response()

    async def _roku_launch_handler(self, request):
        app_id = request.match_info['id']
        self.handler.launch(self.roku_usn, app_id)
        return web.Response()

    async def _roku_apps_handler(self, request):
        return web.Response(body=APPS_TEMPLATE,
                            headers={'Content-Type': 'text/xml'})

    async def _roku_active_app_handler(self, request):
        return web.Response(body=ACTIVE_APP_TEMPLATE,
                            headers={'Content-Type': 'text/xml'})

    async def _roku_app_icon_handler(self, request):
        return web.Response(body=APP_PLACEHOLDER_ICON,
                            headers={'Content-Type': 'image/png'})

    async def _roku_search_handler(self, request):
        return web.Response()

    async def _roku_info_handler(self, request):
        return web.Response(body=self.device_info,
                            headers={'Content-Type': 'text/xml'})

    @web.middleware
    async def _check_remote_and_host_ip(self, request, handler):
        # only allow access by advertised address or bound ip:[port]
        # (prevents dns rebinding)
        if request.host not in self.allowed_hosts:
            _LOGGER.warning("Rejected non-advertised access by host %s",
                            request.host)
            raise web.HTTPForbidden

        # only allow local network access
        if not ip_address(request.remote).is_private:
            _LOGGER.warning("Rejected non-local access from remote %s",
                            request.remote)
            raise web.HTTPForbidden

        return await handler(request)

    async def _setup_app(self) -> web.AppRunner:
        app = web.Application(loop=self.loop,
                              middlewares=[self._check_remote_and_host_ip])

        app.router.add_route('GET', "/", self._roku_root_handler)

        app.router.add_route('POST', "/keydown/{key}",
                             self._roku_keydown_handler)
        app.router.add_route('POST', "/keyup/{key}",
                             self._roku_keyup_handler)
        app.router.add_route('POST', "/keypress/{key}",
                             self._roku_keypress_handler)
        app.router.add_route('POST', "/launch/{id}",
                             self._roku_launch_handler)
        app.router.add_route('POST', "/input",
                             self._roku_input_handler)
        app.router.add_route('POST', "/search",
                             self._roku_search_handler)

        app.router.add_route('GET', "/query/apps",
                             self._roku_apps_handler)
        app.router.add_route('GET', "/query/icon/{id}",
                             self._roku_app_icon_handler)
        app.router.add_route('GET', "/query/active-app",
                             self._roku_active_app_handler)
        app.router.add_route('GET', "/query/device-info",
                             self._roku_info_handler)

        api_runner = web.AppRunner(app)

        await api_runner.setup()

        return api_runner

    async def start(self) -> None:
        """Start the Roku API server and discovery endpoint."""
        _LOGGER.debug("roku_api:starting server %s:%s",
                      self.host_ip, self.listen_port)

        # set up the HTTP server
        self.api_runner = await self._setup_app()

        api_endpoint = web.TCPSite(self.api_runner,
                                   self.host_ip, self.listen_port)

        await api_endpoint.start()

        # set up the SSDP discovery server
        _, self.discovery_proto = await self.loop.create_datagram_endpoint(
            lambda: EmulatedRokuDiscoveryProtocol(self.loop,
                                                  self.host_ip, self.roku_usn,
                                                  self.advertise_ip,
                                                  self.advertise_port),
            local_addr=(
                MULTICAST_GROUP if self.bind_multicast else self.host_ip,
                MULTICAST_PORT),
            reuse_address=True)

    async def close(self) -> None:
        """Close the Roku API server and discovery endpoint."""
        _LOGGER.debug("roku_api:closing server %s:%s",
                      self.host_ip, self.listen_port)

        if self.discovery_proto:
            self.discovery_proto.close()
            self.discovery_proto = None

        if self.api_runner:
            await self.api_runner.cleanup()
            self.api_runner = None


# Taken from: http://stackoverflow.com/a/11735897
def get_local_ip() -> str:
    """Try to determine the local IP address of the machine."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Use Google Public DNS server to determine own IP
        sock.connect(('8.8.8.8', 80))

        return sock.getsockname()[0]  # type: ignore
    except socket.error:
        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            return '127.0.0.1'
    finally:
        sock.close()
