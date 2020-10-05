"""Define constants for the Monitor Docker component."""

DOMAIN = "monitor_docker"
API = "api"
CONFIG = "config"
CONTAINER = "container"

CONF_CERTPATH = "certpath"
CONF_CONTAINERS = "containers"
CONF_RENAME = "rename"
CONF_SENSORNAME = "sensorname"
CONF_SWITCHENABLED = "switchenabled"
CONF_SWITCHNAME = "switchname"

DEFAULT_NAME = "Docker"
DEFAULT_SENSORNAME = "{name} {sensor}"
DEFAULT_SWITCHNAME = "{name}"

COMPONENTS = ["sensor", "switch"]

PRECISION = 2

DOCKER_INFO_VERSION = "version"
DOCKER_INFO_CONTAINER_RUNNING = "containers_running"
DOCKER_INFO_CONTAINER_PAUSED = "containers_paused"
DOCKER_INFO_CONTAINER_STOPPED = "containers_stopped"
DOCKER_INFO_CONTAINER_TOTAL = "containers_total"
DOCKER_INFO_IMAGES = "images"
DOCKER_STATS_CPU_PERCENTAGE = "containers_cpu_percentage"
DOCKER_STATS_1CPU_PERCENTAGE = "containers_1cpu_percentage"
DOCKER_STATS_MEMORY = "containers_memory"
DOCKER_STATS_MEMORY_PERCENTAGE = "containers_memory_percentage"

CONTAINER_INFO_ALLINONE = "allinone"
CONTAINER_INFO_STATE = "state"
CONTAINER_INFO_STATUS = "status"
CONTAINER_INFO_NETWORK_AVAILABLE = "network_available"
CONTAINER_INFO_UPTIME = "uptime"
CONTAINER_INFO_IMAGE = "image"
CONTAINER_STATS_CPU_PERCENTAGE = "cpu_percentage"
CONTAINER_STATS_1CPU_PERCENTAGE = "1cpu_percentage"
CONTAINER_STATS_MEMORY = "memory"
CONTAINER_STATS_MEMORY_PERCENTAGE = "memory_percentage"
CONTAINER_STATS_NETWORK_SPEED_UP = "network_speed_up"
CONTAINER_STATS_NETWORK_SPEED_DOWN = "network_speed_down"
CONTAINER_STATS_NETWORK_TOTAL_UP = "network_total_up"
CONTAINER_STATS_NETWORK_TOTAL_DOWN = "network_total_down"

DOCKER_MONITOR_LIST = {
    DOCKER_INFO_VERSION: ["Version", None, "mdi:information-outline", None],
    DOCKER_INFO_CONTAINER_RUNNING: ["Containers Running", None, "mdi:docker", None],
    DOCKER_INFO_CONTAINER_PAUSED: ["Containers Paused", None, "mdi:docker", None],
    DOCKER_INFO_CONTAINER_STOPPED: ["Containers Stopped", None, "mdi:docker", None],
    DOCKER_INFO_CONTAINER_TOTAL: ["Containers Total", None, "mdi:docker", None],
    DOCKER_STATS_CPU_PERCENTAGE: ["CPU", "%", "mdi:chip", None],
    DOCKER_STATS_1CPU_PERCENTAGE: ["1CPU", "%", "mdi:chip", None],
    DOCKER_STATS_MEMORY: ["Memory", "MB", "mdi:memory", None],
    DOCKER_STATS_MEMORY_PERCENTAGE: ["Memory (percent)", "%", "mdi:memory", None],
    DOCKER_INFO_IMAGES: ["Images", None, "mdi:docker", None],
}

CONTAINER_MONITOR_LIST = {
    CONTAINER_INFO_STATE: ["State", None, "mdi:checkbox-marked-circle-outline", None],
    CONTAINER_INFO_STATUS: ["Status", None, "mdi:checkbox-marked-circle-outline", None],
    CONTAINER_INFO_UPTIME: ["Up Time", "", "mdi:clock", "timestamp"],
    CONTAINER_INFO_IMAGE: ["Image", None, "mdi:information-outline", None],
    CONTAINER_STATS_CPU_PERCENTAGE: ["CPU", "%", "mdi:chip", None],
    CONTAINER_STATS_1CPU_PERCENTAGE: ["1CPU", "%", "mdi:chip", None],
    CONTAINER_STATS_MEMORY: ["Memory", "MB", "mdi:memory", None],
    CONTAINER_STATS_MEMORY_PERCENTAGE: ["Memory (percent)", "%", "mdi:memory", None],
    CONTAINER_STATS_NETWORK_SPEED_UP: ["Network speed Up", "kB/s", "mdi:upload", None],
    CONTAINER_STATS_NETWORK_SPEED_DOWN: [
        "Network speed Down",
        "kB/s",
        "mdi:download",
        None,
    ],
    CONTAINER_STATS_NETWORK_TOTAL_UP: ["Network total Up", "MB", "mdi:upload", None],
    CONTAINER_STATS_NETWORK_TOTAL_DOWN: [
        "Network total Down",
        "MB",
        "mdi:download",
        None,
    ],
}

CONTAINER_MONITOR_NETWORK_LIST = [
    CONTAINER_STATS_NETWORK_SPEED_UP,
    CONTAINER_STATS_NETWORK_SPEED_DOWN,
    CONTAINER_STATS_NETWORK_TOTAL_UP,
    CONTAINER_STATS_NETWORK_TOTAL_DOWN,
]

MONITORED_CONDITIONS_LIST = list(DOCKER_MONITOR_LIST.keys()) + list(
    CONTAINER_MONITOR_LIST.keys()
)


ATTR_MEMORY_LIMIT = "Memory_limit"
ATTR_ONLINE_CPUS = "Online_CPUs"
ATTR_VERSION_ARCH = "Architecture"
ATTR_VERSION_KERNEL = "Kernel"
ATTR_VERSION_OS = "OS"
ATTR_VERSION_OS_TYPE = "OS_Type"
