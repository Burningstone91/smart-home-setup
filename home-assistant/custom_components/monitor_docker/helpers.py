"""Monitor Docker API helper."""

import aiodocker
import asyncio
import concurrent
import logging
import os

from datetime import datetime, timezone
from dateutil import parser, relativedelta

from homeassistant.helpers.discovery import load_platform

import homeassistant.util.dt as dt_util

from homeassistant.const import (
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_URL,
    EVENT_HOMEASSISTANT_STOP,
)

from .const import (
    ATTR_MEMORY_LIMIT,
    ATTR_ONLINE_CPUS,
    ATTR_VERSION_ARCH,
    ATTR_VERSION_KERNEL,
    ATTR_VERSION_OS,
    ATTR_VERSION_OS_TYPE,
    COMPONENTS,
    CONF_CERTPATH,
    CONTAINER,
    CONTAINER_STATS_CPU_PERCENTAGE,
    CONTAINER_STATS_1CPU_PERCENTAGE,
    CONTAINER_INFO_IMAGE,
    CONTAINER_INFO_NETWORK_AVAILABLE,
    CONTAINER_STATS_MEMORY,
    CONTAINER_STATS_MEMORY_PERCENTAGE,
    CONTAINER_STATS_NETWORK_SPEED_UP,
    CONTAINER_STATS_NETWORK_SPEED_DOWN,
    CONTAINER_STATS_NETWORK_TOTAL_UP,
    CONTAINER_STATS_NETWORK_TOTAL_DOWN,
    DOCKER_INFO_IMAGES,
    CONTAINER_INFO_STATE,
    CONTAINER_INFO_STATUS,
    CONTAINER_INFO_UPTIME,
    DOCKER_INFO_CONTAINER_RUNNING,
    DOCKER_INFO_CONTAINER_PAUSED,
    DOCKER_INFO_CONTAINER_STOPPED,
    DOCKER_INFO_CONTAINER_TOTAL,
    DOCKER_INFO_VERSION,
    DOCKER_STATS_CPU_PERCENTAGE,
    DOCKER_STATS_1CPU_PERCENTAGE,
    DOCKER_STATS_MEMORY,
    DOCKER_STATS_MEMORY_PERCENTAGE,
    DOMAIN,
    PRECISION,
)

VERSION = "1.4"

_LOGGER = logging.getLogger(__name__)


def toKB(value):
    """Converts bytes to kBytes."""
    return round(value / (1024 ** 1), PRECISION)


def toMB(value):
    """Converts bytes to MBytes."""
    return round(value / (1024 ** 2), PRECISION)


#################################################################
class DockerAPI:
    """Docker API abstraction allowing multiple Docker instances beeing monitored."""

    def __init__(self, hass, config):
        """Initialize the Docker API."""

        self._hass = hass
        self._config = config
        self._containers = {}
        self._tasks = {}
        self._info = {}
        self._event_create = {}
        self._event_destroy = {}

        _LOGGER.debug("Helper version: %s", VERSION)

        self._interval = config[CONF_SCAN_INTERVAL].seconds

        self._loop = asyncio.get_event_loop()

        try:
            # Try to fix unix:// to unix:/// (3 are required by aiodocker)
            url = self._config[CONF_URL]
            if (
                url is not None
                and url.find("unix://") == 0
                and url.find("unix:///") == -1
            ):
                url = url.replace("unix://", "unix:///")

            # Do some debugging logging for TCP/TLS
            if url is not None:
                _LOGGER.debug("Docker URL is '%s'", url)

                # Check for TLS if it is not unix
                if url.find("tcp:") == 0 or url.find("http:") == 0:
                    tlsverify = os.environ.get("DOCKER_TLS_VERIFY", None)
                    certpath = os.environ.get("DOCKER_CERT_PATH", None)
                    if tlsverify is None:
                        _LOGGER.debug(
                            "Docker environment 'DOCKER_TLS_VERIFY' is NOT set"
                        )
                    else:
                        _LOGGER.debug(
                            "Docker environment set 'DOCKER_TLS_VERIFY=%s'", tlsverify
                        )

                    if certpath is None:
                        _LOGGER.debug(
                            "Docker environment 'DOCKER_CERT_PATH' is NOT set"
                        )
                    else:
                        _LOGGER.debug(
                            "Docker environment set 'DOCKER_CERT_PATH=%s'", certpath
                        )

                    if self._config[CONF_CERTPATH]:
                        _LOGGER.debug(
                            "Docker CertPath set '%s', setting environment variables DOCKER_TLS_VERIFY/DOCKER_CERT_PATH",
                            self._config[CONF_CERTPATH],
                        )
                        os.environ["DOCKER_TLS_VERIFY"] = "1"
                        os.environ["DOCKER_CERT_PATH"] = self._config[CONF_CERTPATH]

            self._api = aiodocker.Docker(url=url)
        except Exception as err:
            _LOGGER.error("Can not connect to Docker API (%s)", str(err), exc_info=True)
            return

        version = self._loop.run_until_complete(self._api.version())
        _LOGGER.debug("Docker version: %s", version.get("Version", None))

        # Start task to monitor events of create/delete/start/stop
        self._tasks["events"] = self._loop.create_task(self._run_docker_events())

        # Start task to monitor total/running containers
        self._tasks["info"] = self._loop.create_task(self._run_docker_info())

        # Get the list of containers to monitor
        containers = self._loop.run_until_complete(self._api.containers.list(all=True))

        for container in containers or []:
            # Determine name from Docker API, it contains an array with a slash
            cname = container._container["Names"][0][1:]

            # We will monitor all containers, including excluded ones.
            # This is needed to get total CPU/Memory usage.
            _LOGGER.debug("%s: Container Monitored", cname)

            # Create our Docker Container API
            self._containers[cname] = DockerContainerAPI(
                self._api, cname, self._interval
            )

        hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, self._monitor_stop)

        for component in COMPONENTS:
            load_platform(
                self._hass,
                component,
                DOMAIN,
                {CONF_NAME: self._config[CONF_NAME]},
                self._config,
            )

    #############################################################
    def _monitor_stop(self, _service_or_event):
        """Stop the monitor thread."""
        _LOGGER.info("Stopping Monitor Docker thread (%s)", self._config[CONF_NAME])

        self._loop.stop()

    #############################################################
    async def _run_docker_events(self):
        """Function to retrieve docker events. We can add or remove monitored containers."""

        try:
            subscriber = self._api.events.subscribe()

            while True:
                event = await subscriber.get()
                if event is None:
                    _LOGGER.error("run_docker_events loop ended")
                    break

                # Only monitor container events
                if event["Type"] == CONTAINER:
                    if event["Action"] == "create":
                        # Check if another task is running, ifso, we don't create a new one
                        taskcreated = (
                            True if self._event_create or self._event_destroy else False
                        )

                        cname = event["Actor"]["Attributes"]["name"]

                        # Add container name to containers to be monitored this has to
                        # be a new task, otherwise it will block our event monitoring
                        if cname not in self._event_create:
                            _LOGGER.debug("%s: Event create container", cname)
                            self._event_create[cname] = 0
                        else:
                            _LOGGER.error(
                                "%s: Event create container, but already in working table?"
                            )

                        if self._event_create and not taskcreated:
                            self._loop.create_task(self._container_create_destroy())

                    elif event["Action"] == "destroy":
                        # Check if another task is running, ifso, we don't create a new one
                        taskcreated = (
                            True if self._event_create or self._event_destroy else False
                        )

                        cname = event["Actor"]["Attributes"]["name"]

                        # Remove container name to containers to be monitored this has to
                        # be a new task, otherwise it will block our event monitoring
                        if cname in self._event_create:
                            _LOGGER.warning(
                                "%s: Event destroy received, but create wasn't executed yet",
                                cname,
                            )
                            del self._event_create[cname]
                        elif cname not in self._event_destroy:
                            _LOGGER.debug("%s: Event destroy container", cname)
                            self._event_destroy[cname] = 0
                        else:
                            _LOGGER.error(
                                "%s: Event destroy container, but already in working table?",
                                cname,
                            )

                        if self._event_destroy and not taskcreated:
                            self._loop.create_task(self._container_create_destroy())
                    elif event["Action"] == "rename":
                        # during a docker-compose up -d <container> the old container can be renamed
                        # sensors/switch should be removed before the new container is monitored

                        # New name
                        cname = event["Actor"]["Attributes"]["name"]

                        # Old name, and remove leading slash
                        oname = event["Actor"]["Attributes"]["oldName"]
                        oname = oname[1:]

                        if oname in self._containers:
                            _LOGGER.debug(
                                "%s: Event rename container to '%s'", oname, cname
                            )
                            self._containers[cname] = self._containers[oname]
                            del self._containers[oname]

                            # We also need to rename the internal name
                            self._containers[cname].set_name(cname)
                        else:
                            _LOGGER.error(
                                "%s: Event rename container doesn't exist in list?",
                                oname,
                            )

        except Exception as err:
            _LOGGER.error("run_docker_events (%s)", str(err), exc_info=True)

    #############################################################
    async def _container_create_destroy(self):
        """Handles create or destroy of container events."""

        try:
            while self._event_create or self._event_destroy:

                # Go through create loop first
                for cname in self._event_create:
                    if self._event_create[cname] > 2:
                        del self._event_create[cname]
                        await self._container_add(cname)
                        break
                    else:
                        self._event_create[cname] += 1
                else:
                    # If all create, we can handle the destroy loop
                    for cname in self._event_destroy:
                        await self._container_remove(cname)

                    self._event_destroy = {}

                # Sleep for 1 second, don't try to create it too fast
                await asyncio.sleep(1)

        except Exception as err:
            _LOGGER.error("container_create_destroy (%s)", str(err), exc_info=True)

    #############################################################
    async def _container_add(self, cname):

        if cname in self._containers:
            _LOGGER.error("%s: Container already monitored", cname)
            return

        _LOGGER.debug("%s: Starting Container Monitor", cname)

        # Create our Docker Container API
        self._containers[cname] = DockerContainerAPI(
            self._api, cname, self._interval, False
        )

        # We should wait until container is attached
        result = await self._containers[cname]._initGetContainer()

        if result:
            # Lets wait 1 second before we try to create sensors/switches
            await asyncio.sleep(1)

            for component in COMPONENTS:
                load_platform(
                    self._hass,
                    component,
                    DOMAIN,
                    {CONF_NAME: self._config[CONF_NAME], CONTAINER: cname},
                    self._config,
                )
        else:
            _LOGGER.error("%s: Problem during start of monitoring", cname)

    #############################################################
    async def _container_remove(self, cname):

        if cname in self._containers:
            _LOGGER.debug("%s: Stopping Container Monitor", cname)
            self._containers[cname].cancel_task()
            self._containers[cname].remove_entities()
            await asyncio.sleep(0.1)
            del self._containers[cname]
        else:
            _LOGGER.error("%s: Container is NOT monitored", cname)

    #############################################################
    async def _run_docker_info(self):
        """Function to retrieve information like docker info."""

        try:
            while True:
                info = await self._api.system.info()
                self._info[DOCKER_INFO_VERSION] = info.get("ServerVersion")
                self._info[DOCKER_INFO_CONTAINER_RUNNING] = info.get(
                    "ContainersRunning"
                )
                self._info[DOCKER_INFO_CONTAINER_PAUSED] = info.get("ContainersPaused")
                self._info[DOCKER_INFO_CONTAINER_STOPPED] = info.get(
                    "ContainersStopped"
                )
                self._info[DOCKER_INFO_CONTAINER_TOTAL] = info.get("Containers")
                self._info[DOCKER_INFO_IMAGES] = info.get("Images")

                self._info[ATTR_MEMORY_LIMIT] = info.get("MemTotal")
                self._info[ATTR_ONLINE_CPUS] = info.get("NCPU")
                self._info[ATTR_VERSION_OS] = info.get("OperationSystem")
                self._info[ATTR_VERSION_OS_TYPE] = info.get("OStype")
                self._info[ATTR_VERSION_ARCH] = info.get("Architecture")
                self._info[ATTR_VERSION_KERNEL] = info.get("KernelVersion")

                self._info[DOCKER_STATS_CPU_PERCENTAGE] = 0.0
                self._info[DOCKER_STATS_1CPU_PERCENTAGE] = 0.0
                self._info[DOCKER_STATS_MEMORY] = 0
                self._info[DOCKER_STATS_MEMORY_PERCENTAGE] = 0.0

                # Now go through all containers and get the cpu/memory stats
                for container in self._containers.values():
                    try:
                        info = container.get_info()
                        if info.get(CONTAINER_INFO_STATE) == "running":
                            stats = container.get_stats()
                            if stats.get(CONTAINER_STATS_CPU_PERCENTAGE) is not None:
                                self._info[DOCKER_STATS_CPU_PERCENTAGE] += stats.get(
                                    CONTAINER_STATS_CPU_PERCENTAGE
                                )
                            if stats.get(CONTAINER_STATS_MEMORY) is not None:
                                self._info[DOCKER_STATS_MEMORY] += stats.get(
                                    CONTAINER_STATS_MEMORY
                                )
                    except Exception as err:
                        _LOGGER.error(
                            "%s: run_docker_info memory/cpu of X (%s)",
                            self._config[CONF_NAME],
                            str(err),
                            exc_info=True,
                        )

                # Calculate memory percentage
                if (
                    self._info[ATTR_MEMORY_LIMIT] is not None
                    and self._info[ATTR_MEMORY_LIMIT] is not 0
                ):
                    self._info[DOCKER_STATS_MEMORY_PERCENTAGE] = round(
                        self._info[DOCKER_STATS_MEMORY]
                        / toMB(self._info[ATTR_MEMORY_LIMIT])
                        * 100,
                        PRECISION,
                    )

                # Try to fix possible 0 values in history at start-up
                self._info[DOCKER_STATS_CPU_PERCENTAGE] = (
                    None
                    if self._info[DOCKER_STATS_CPU_PERCENTAGE] == 0.0
                    else round(self._info[DOCKER_STATS_CPU_PERCENTAGE], PRECISION)
                )

                # Calculate for 0-100%
                if self._info[DOCKER_STATS_CPU_PERCENTAGE] == 0.0:
                    self._info[DOCKER_STATS_1CPU_PERCENTAGE] = None
                elif self._info[DOCKER_STATS_CPU_PERCENTAGE] is None:
                    self._info[DOCKER_STATS_1CPU_PERCENTAGE] = None
                else:
                    self._info[DOCKER_STATS_1CPU_PERCENTAGE] = round(
                        (
                            self._info[DOCKER_STATS_CPU_PERCENTAGE]
                            / self._info[ATTR_ONLINE_CPUS]
                        ),
                        PRECISION,
                    )

                self._info[DOCKER_STATS_MEMORY] = (
                    None
                    if self._info[DOCKER_STATS_MEMORY] == 0.0
                    else round(self._info[DOCKER_STATS_MEMORY], PRECISION)
                )

                self._info[DOCKER_STATS_MEMORY_PERCENTAGE] = (
                    None
                    if self._info[DOCKER_STATS_MEMORY_PERCENTAGE] == 0.0
                    else round(self._info[DOCKER_STATS_MEMORY_PERCENTAGE], PRECISION)
                )

                _LOGGER.debug(
                    "Version: %s, Containers: %s, Running: %s, CPU: %s%%, 1CPU: %s%%, Memory: %sMB, %s%%",
                    self._info[DOCKER_INFO_VERSION],
                    self._info[DOCKER_INFO_CONTAINER_TOTAL],
                    self._info[DOCKER_INFO_CONTAINER_RUNNING],
                    self._info[DOCKER_STATS_CPU_PERCENTAGE],
                    self._info[DOCKER_STATS_1CPU_PERCENTAGE],
                    self._info[DOCKER_STATS_MEMORY],
                    self._info[DOCKER_STATS_MEMORY_PERCENTAGE],
                )

                await asyncio.sleep(self._interval)
        except Exception as err:
            _LOGGER.error(
                "%s: run_docker_info (%s)",
                self._config[CONF_NAME],
                str(err),
                exc_info=True,
            )

    #############################################################
    def list_containers(self):
        return self._containers.keys()

    #############################################################
    def get_container(self, cname):
        if cname in self._containers:
            return self._containers[cname]
        else:
            _LOGGER.error("Trying to get a not existing container %s", cname)
            return None

    #############################################################
    def get_info(self):
        return self._info


#################################################################
class DockerContainerAPI:
    """Docker Container API abstraction."""

    def __init__(self, api, name, interval, atInit=True):
        self._api = api
        self._name = name
        self._interval = interval
        self._busy = False
        self._atInit = atInit
        self._task = None
        self._subscribers = []
        self._cpu_old = {}
        self._network_old = {}
        self._network_error = 0
        self._memory_error = 0
        self._cpu_error = 0

        self._info = {}
        self._stats = {}

        self._loop = asyncio.get_event_loop()

        # During start-up we will wait on container attachment,
        # preventing concurrency issues the main HA loop (we are
        # othside that one with our threads)
        if self._atInit:
            try:
                self._container = self._loop.run_until_complete(
                    self._api.containers.get(self._name)
                )
            except Exception as err:
                _LOGGER.error(
                    "%s: Container not available anymore (1) (%s)",
                    self._name,
                    str(err),
                    exc_info=True,
                )
                return

            self._task = self._loop.create_task(self._run())

    #############################################################
    async def _initGetContainer(self):

        # If we noticed a event=create, we need to attach here.
        # The run_until_complete doesn't work, because we are already
        # in a running loop.

        try:
            self._container = await self._api.containers.get(self._name)
        except Exception as err:
            _LOGGER.error(
                "%s: Container not available anymore (2) (%s)",
                self._name,
                str(err),
                exc_info=True,
            )
            return False

        self._task = self._loop.create_task(self._run())

        return True

    #############################################################
    async def _run(self):
        """Loop to gather container info/stats."""

        try:
            while True:

                # Don't check container if we are doing a start/stop
                if not self._busy:
                    await self._run_container_info()

                    # Only run stats if container is running
                    if self._info[CONTAINER_INFO_STATE] in ("running", "paused"):
                        await self._run_container_stats()

                    self._notify()
                else:
                    _LOGGER.debug("%s: Waiting on stop/start of container", self._name)

                await asyncio.sleep(self._interval)
        except concurrent.futures._base.CancelledError:
            pass
        except Exception as err:
            _LOGGER.error(
                "%s: Container not available anymore (3) (%s)",
                self._name,
                str(err),
                exc_info=True,
            )

    #############################################################
    async def _run_container_info(self):
        """Get container information, but we can not get
           the uptime of this container, that is only available
           while listing all containers :-(.
        """

        self._info = {}

        raw = await self._container.show()

        self._info[CONTAINER_INFO_STATE] = raw["State"]["Status"]
        self._info[CONTAINER_INFO_IMAGE] = raw["Config"]["Image"]
        self._info[CONTAINER_INFO_NETWORK_AVAILABLE] = (
            False if raw["HostConfig"]["NetworkMode"] in ["host", "none"] else True
        )

        # We only do a calculation of startedAt, because we use it twice
        startedAt = parser.parse(raw["State"]["StartedAt"])

        # Determine the container status in the format:
        # Up 6 days
        # Up 6 days (Paused)
        # Exited (0) 2 months ago
        # Restarting (99) 5 seconds ago

        if self._info[CONTAINER_INFO_STATE] == "running":
            self._info[CONTAINER_INFO_STATUS] = "Up {}".format(
                self._calcdockerformat(startedAt)
            )
        elif self._info[CONTAINER_INFO_STATE] == "exited":
            self._info[CONTAINER_INFO_STATUS] = "Exited ({}) {} ago".format(
                raw["State"]["ExitCode"],
                self._calcdockerformat(parser.parse(raw["State"]["FinishedAt"])),
            )
        elif self._info[CONTAINER_INFO_STATE] == "created":
            self._info[CONTAINER_INFO_STATUS] = "Created {} ago".format(
                self._calcdockerformat(parser.parse(raw["Created"]))
            )
        elif self._info[CONTAINER_INFO_STATE] == "restarting":
            self._info[CONTAINER_INFO_STATUS] = "Restarting"
        elif self._info[CONTAINER_INFO_STATE] == "paused":
            self._info[CONTAINER_INFO_STATUS] = "Up {} (Paused)".format(
                self._calcdockerformat(startedAt)
            )
        else:
            self._info[CONTAINER_INFO_STATUS] = "None ({})".format(
                raw["State"]["Status"]
            )

        if self._info[CONTAINER_INFO_STATE] in ("running", "paused"):
            self._info[CONTAINER_INFO_UPTIME] = dt_util.as_local(startedAt).isoformat()
        else:
            self._info[CONTAINER_INFO_UPTIME] = None
            _LOGGER.debug("%s: %s", self._name, self._info[CONTAINER_INFO_STATUS])

    #############################################################
    async def _run_container_stats(self):

        # Initialize stats information
        stats = {}
        stats["cpu"] = {}
        stats["memory"] = {}
        stats["network"] = {}
        stats["read"] = {}

        # Get container stats, only interested in [0]
        raw = await self._container.stats(stream=False)
        raw = raw[0]

        stats["read"] = parser.parse(raw["read"])

        # Gather CPU information
        cpu_stats = {}
        try:
            cpu_new = {}
            cpu_new["total"] = raw["cpu_stats"]["cpu_usage"]["total_usage"]
            cpu_new["system"] = raw["cpu_stats"]["system_cpu_usage"]

            # Compatibility wih older Docker API
            if "online_cpus" in raw["cpu_stats"]:
                cpu_stats["online_cpus"] = raw["cpu_stats"]["online_cpus"]
            else:
                cpu_stats["online_cpus"] = len(
                    raw["cpu_stats"]["cpu_usage"]["percpu_usage"] or []
                )

            # Calculate cpu usage, but first iteration we don't know it
            if self._cpu_old:
                cpu_delta = float(cpu_new["total"] - self._cpu_old["total"])
                system_delta = float(cpu_new["system"] - self._cpu_old["system"])

                cpu_stats["total"] = round(0.0, PRECISION)
                if cpu_delta > 0.0 and system_delta > 0.0:
                    cpu_stats["total"] = round(
                        (cpu_delta / system_delta)
                        * float(cpu_stats["online_cpus"])
                        * 100.0,
                        PRECISION,
                    )

            self._cpu_old = cpu_new

            if self._cpu_error > 0:
                _LOGGER.debug(
                    "%s: CPU error count %s reset to 0", self._name, self._cpu_error
                )

            self._cpu_error = 0

        except KeyError as err:

            # Something wrong with the raw data
            if self._cpu_error == 0:
                _LOGGER.error(
                    "%s: Cannot determine CPU usage for container (%s)",
                    self._name,
                    str(err),
                )
                if "cpu_stats" in raw:
                    _LOGGER.error("Raw 'cpu_stats' %s", raw["cpu_stats"])
                else:
                    _LOGGER.error("No 'cpu_stats' found in raw packet")

            self._cpu_error += 1

        # Gather memory information
        memory_stats = {}
        try:
            # Memory is in Bytes, convert to MBytes
            memory_stats["usage"] = toMB(
                raw["memory_stats"]["usage"] - raw["memory_stats"]["stats"]["cache"]
            )
            memory_stats["limit"] = toMB(raw["memory_stats"]["limit"])
            memory_stats["max_usage"] = toMB(raw["memory_stats"]["max_usage"])
            memory_stats["usage_percent"] = round(
                float(memory_stats["usage"]) / float(memory_stats["limit"]) * 100.0,
                PRECISION,
            )

            if self._memory_error > 0:
                _LOGGER.debug(
                    "%s: Memory error count %s reset to 0",
                    self._name,
                    self._memory_error,
                )

            self._memory_error = 0

        except (KeyError, TypeError) as err:

            if self._memory_error == 0:
                _LOGGER.error(
                    "%s: Cannot determine memory usage for container (%s)",
                    self._name,
                    str(err),
                )
                if "memory_stats" in raw:
                    _LOGGER.error(
                        "%s: Raw 'memory_stats' %s", raw["memory_stats"], self._name
                    )
                else:
                    _LOGGER.error(
                        "%s: No 'memory_stats' found in raw packet", self._name
                    )

            self._memory_error += 1

        _LOGGER.debug(
            "%s: CPU: %s%%, Memory: %sMB, %s%%",
            self._name,
            cpu_stats.get("total", None),
            memory_stats.get("usage", None),
            memory_stats.get("usage_percent", None),
        )

        # Gather network information, doesn't work in network=host mode
        network_stats = {}
        if self._info[CONTAINER_INFO_NETWORK_AVAILABLE]:
            try:
                network_new = {}
                network_stats["total_tx"] = 0
                network_stats["total_rx"] = 0
                for if_name, data in raw["networks"].items():
                    network_stats["total_tx"] += data["tx_bytes"]
                    network_stats["total_rx"] += data["rx_bytes"]

                network_new = {
                    "read": stats["read"],
                    "total_tx": network_stats["total_tx"],
                    "total_rx": network_stats["total_rx"],
                }

                if self._network_old:
                    tx = network_new["total_tx"] - self._network_old["total_tx"]
                    rx = network_new["total_rx"] - self._network_old["total_rx"]
                    tim = (
                        network_new["read"] - self._network_old["read"]
                    ).total_seconds()

                    # Calculate speed, also convert to kByte/sec
                    network_stats["speed_tx"] = toKB(round(float(tx) / tim, PRECISION))
                    network_stats["speed_rx"] = toKB(round(float(rx) / tim, PRECISION))

                self._network_old = network_new

                # Convert total to MB
                network_stats["total_tx"] = toMB(network_stats["total_tx"])
                network_stats["total_rx"] = toMB(network_stats["total_rx"])

            except KeyError as err:
                _LOGGER.error(
                    "%s: Can not determine network usage for container (%s)",
                    self._name,
                    str(err),
                )
                if "networks" in raw:
                    _LOGGER.error("%s: Raw 'networks' %s", raw["networks"], self._name)
                else:
                    _LOGGER.error("%s: No 'networks' found in raw packet", self._name)

                # Check how many times we got a network error, after 5 times it won't happen
                # anymore, thus we disable error reporting
                self._network_error += 1
                if self._network_error > 5:
                    _LOGGER.error(
                        "%s: Too many errors on 'networks' stats, disabling monitoring"
                    )
                    self._info[CONTAINER_INFO_NETWORK_AVAILABLE] = False

        # All information collected
        stats["cpu"] = cpu_stats
        stats["memory"] = memory_stats
        stats["network"] = network_stats

        stats[CONTAINER_STATS_CPU_PERCENTAGE] = cpu_stats.get("total")
        if "online_cpus" in cpu_stats and cpu_stats.get("total") is not None:
            stats[CONTAINER_STATS_1CPU_PERCENTAGE] = round(
                cpu_stats.get("total") / cpu_stats["online_cpus"], PRECISION
            )
        stats[CONTAINER_STATS_MEMORY] = memory_stats.get("usage")
        stats[CONTAINER_STATS_MEMORY_PERCENTAGE] = memory_stats.get("usage_percent")
        stats[CONTAINER_STATS_NETWORK_SPEED_UP] = network_stats.get("speed_tx")
        stats[CONTAINER_STATS_NETWORK_SPEED_DOWN] = network_stats.get("speed_rx")
        stats[CONTAINER_STATS_NETWORK_TOTAL_UP] = network_stats.get("total_tx")
        stats[CONTAINER_STATS_NETWORK_TOTAL_DOWN] = network_stats.get("total_rx")

        self._stats = stats

    #############################################################
    def cancel_task(self):
        if self._task is not None:
            _LOGGER.info("%s: Cancelling task for container info/stats", self._name)
            self._task.cancel()
        else:
            _LOGGER.info(
                "%s: Task (not running) can not be cancelled for container info/stats",
                self._name,
            )

    #############################################################
    def remove_entities(self):
        if len(self._subscribers) > 0:
            _LOGGER.debug("%s: Removing entities from container", self._name)

        for callback in self._subscribers:
            callback(remove=True)

        self._subscriber = []

    #############################################################
    async def _start(self):
        """Separate loop to start container, because HA loop can't be used."""

        try:
            await self._container.start()
        except Exception as err:
            _LOGGER.error("%s: Can not start containner (%s)", self._name, str(err))
        finally:
            self._busy = False

    #############################################################
    async def start(self):
        """Called from HA switch."""
        _LOGGER.info("%s: Start container", self._name)

        self._busy = True
        self._loop.create_task(self._start())

    #############################################################
    async def _stop(self):
        """Separate loop to stop container, because HA loop can't be used."""
        try:
            await self._container.stop(t=10)
        except Exception as err:
            _LOGGER.error("%s: Can not stop containner (%s)", self._name, str(err))
        finally:
            self._busy = False

    #############################################################
    async def stop(self):
        """Called from HA switch."""
        _LOGGER.info("%s: Stop container", self._name)

        self._busy = True
        self._loop.create_task(self._stop())

    #############################################################
    def get_name(self):
        """Return the container name."""
        return self._name

    #############################################################
    def set_name(self, name):
        """Set the container name."""
        self._name = name

    #############################################################
    def get_info(self):
        """Return the container info."""
        return self._info

    #############################################################
    def get_stats(self):
        """Return the container stats."""
        return self._stats

    #############################################################
    def register_callback(self, callback, variable):
        """Register callback from sensor/switch."""
        if callback not in self._subscribers:
            _LOGGER.debug(
                "%s: Added callback to container, entity: %s", self._name, variable
            )
            self._subscribers.append(callback)

    #############################################################
    def _notify(self):
        if len(self._subscribers) > 0:
            _LOGGER.debug(
                "%s: Send notify (%d) to container", self._name, len(self._subscribers)
            )

        for callback in self._subscribers:
            callback()

    #############################################################
    @staticmethod
    def _calcdockerformat(dt):
        """Calculate datetime to Docker format, because it isn't available in stats."""
        if dt is None:
            return "None"

        delta = relativedelta.relativedelta(datetime.now(timezone.utc), dt)

        if delta.years != 0:
            return "{} {}".format(delta.years, "year" if delta.years == 1 else "years")
        elif delta.months != 0:
            return "{} {}".format(
                delta.months, "month" if delta.months == 1 else "months"
            )
        elif delta.days != 0:
            return "{} {}".format(delta.days, "day" if delta.days == 1 else "days")
        elif delta.hours != 0:
            return "{} {}".format(delta.hours, "hour" if delta.hours == 1 else "hours")
        elif delta.minutes != 0:
            return "{} {}".format(
                delta.minutes, "minute" if delta.minutes == 1 else "minutes"
            )

        return "{} {}".format(
            delta.seconds, "second" if delta.seconds == 1 else "seconds"
        )
