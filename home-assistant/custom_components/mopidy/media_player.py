"""Support to interact with a MopidyMusic Server."""
import re
import logging
from mopidyapi import MopidyAPI
from requests.exceptions import ConnectionError as reConnectionError
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.media_player import (
    BrowseMedia,
    MediaPlayerEntity,
    PLATFORM_SCHEMA,
)
from homeassistant.components.media_player.errors import BrowseError
import homeassistant.util.dt as dt_util
import homeassistant.helpers.config_validation as cv
from homeassistant.components.media_player.const import (
    MEDIA_CLASS_ALBUM,
    MEDIA_CLASS_ARTIST,
    MEDIA_CLASS_COMPOSER,
    MEDIA_CLASS_DIRECTORY,
    MEDIA_CLASS_GENRE,
    MEDIA_CLASS_MUSIC,
    MEDIA_CLASS_PLAYLIST,
    MEDIA_CLASS_PODCAST,
    MEDIA_CLASS_TRACK,
    MEDIA_CLASS_URL,
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
    MEDIA_TYPE_EPISODE,
    MEDIA_TYPE_MUSIC,
    MEDIA_TYPE_PLAYLIST,
    MEDIA_TYPE_TRACK,
    REPEAT_MODE_ALL,
    REPEAT_MODE_OFF,
    REPEAT_MODE_ONE,
    SUPPORT_BROWSE_MEDIA,
    SUPPORT_CLEAR_PLAYLIST,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PAUSE,
    SUPPORT_PLAY,
    SUPPORT_PLAY_MEDIA,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_REPEAT_SET,
    SUPPORT_SEEK,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_SHUFFLE_SET,
    SUPPORT_STOP,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_STEP,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_PORT,
    CONF_NAME,
    STATE_IDLE,
    STATE_UNAVAILABLE,
    STATE_PLAYING,
    STATE_PAUSED,
    STATE_OFF,
    STATE_UNKNOWN,
)

from .const import DOMAIN, ICON, DEFAULT_NAME, DEFAULT_PORT

SUPPORT_MOPIDY = (
    SUPPORT_BROWSE_MEDIA
    | SUPPORT_CLEAR_PLAYLIST
    | SUPPORT_NEXT_TRACK
    | SUPPORT_PAUSE
    | SUPPORT_PLAY
    | SUPPORT_PLAY_MEDIA
    | SUPPORT_PREVIOUS_TRACK
    | SUPPORT_REPEAT_SET
    | SUPPORT_SHUFFLE_SET
    | SUPPORT_SEEK
    | SUPPORT_STOP
    | SUPPORT_TURN_OFF
    | SUPPORT_TURN_ON
    | SUPPORT_SELECT_SOURCE
)

MEDIA_TYPE_SHOW = "show"

PLAYABLE_MEDIA_TYPES = [
    MEDIA_TYPE_PLAYLIST,
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
    MEDIA_TYPE_EPISODE,
    MEDIA_TYPE_SHOW,
    MEDIA_TYPE_TRACK,
]

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)

CACHE_ROSETTA = {}


class MissingMediaInformation(BrowseError):
    """Missing media required information."""


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up the Mopidy platform."""
    uid = config_entry.data[CONF_ID]
    name = config_entry.data[CONF_NAME]
    host = config_entry.data[CONF_HOST]
    port = config_entry.data[CONF_PORT]

    entity = MopidyMediaPlayerEntity(host, port, name, uid)
    async_add_entities([entity])


async def async_setup_platform(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities, discover_info=None
):
    """Set up the Mopidy platform."""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    name = config.get(CONF_NAME)

    entity = MopidyMediaPlayerEntity(host, port, name)
    async_add_entities([entity], True)


class MopidyMediaPlayerEntity(MediaPlayerEntity):
    """Representation of the Mopidy server."""

    def __init__(self, hostname, port, name, uuid=None):
        """Initialize the Mopidy device."""
        self.hostname = hostname
        self.port = port
        self.device_name = name
        if uuid is None:
            self.uuid = re.sub("[._-]+", "_", hostname)
        else:
            self.uuid = uuid

        self.server_version = None
        self.player_currenttrack = None
        self.player_streamttile = None
        self.player_currenttrach_source = None

        self._media_position = None
        self._media_position_updated_at = None
        self._state = STATE_UNKNOWN
        self._volume = None
        self._muted = None
        self._media_image_url = None
        self._shuffled = None
        self._repeat_mode = None
        self._playlists = []
        self._currentplaylist = None

        self.client = None
        self._available = None

        self._has_support_volume = None

    def _fetch_status(self):
        """Fetch status from Mopidy."""
        _LOGGER.debug("Fetching Mopidy Server status for %s", self.device_name)
        self.player_currenttrack = self.client.playback.get_current_track()
        self.player_streamttile = self.client.playback.get_stream_title()

        if hasattr(self.player_currenttrack, "uri"):
            self.player_currenttrach_source = self.player_currenttrack.uri.partition(
                ":"
            )[0]
        else:
            self.player_currenttrach_source = None

        media_position = int(self.client.playback.get_time_position() / 1000)
        if media_position != self._media_position:
            self._media_position = media_position
            self._media_position_updated_at = dt_util.utcnow()

        state = self.client.playback.get_state()
        if state is None:
            self._state = STATE_UNAVAILABLE
        elif state == "playing":
            self._state = STATE_PLAYING
        elif state == "paused":
            self._state = STATE_PAUSED
        elif state == "stopped":
            self._state = STATE_OFF
        else:
            self._state = STATE_UNKNOWN

        v = self.client.mixer.get_volume()
        self._volume = None
        self._has_support_volume = False
        if v is not None:
            self._volume = float(v / 100)
            self._has_support_volume = True

        self._muted = self.client.mixer.get_mute()

        if hasattr(self.player_currenttrack, "uri"):
            res = self.client.library.get_images([self.player_currenttrack.uri])
            if (
                self.player_currenttrack.uri in res
                and len(res[self.player_currenttrack.uri]) > 0
                and hasattr(res[self.player_currenttrack.uri][0], "uri")
            ):
                self._media_image_url = res[self.player_currenttrack.uri][0].uri
                if self.player_currenttrach_source == "local":
                    self._media_image_url = (
                        f"http://{self.hostname}:{self.port}{self._media_image_url}"
                    )
        else:
            self._media_image_url = None

        self._shuffled = self.client.tracklist.get_random()
        self._playlists = self.client.playlists.as_list()

        repeat = self.client.tracklist.get_repeat()
        single = self.client.tracklist.get_single()
        if repeat and single:
            self._repeat_mode = REPEAT_MODE_ONE
        elif repeat:
            self._repeat_mode = REPEAT_MODE_ALL
        else:
            self._repeat_mode = REPEAT_MODE_OFF

    @property
    def unique_id(self):
        """Return the unique id for the entity."""
        return self.uuid

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self.device_name

    @property
    def icon(self) -> str:
        """Return the icon."""
        return ICON

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self):
        """Return the media state."""
        return self._state

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def media_content_id(self):
        """Return the content ID of current playing media."""
        if hasattr(self.player_currenttrack, "uri"):
            return self.player_currenttrack.uri
        return None

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MEDIA_TYPE_MUSIC

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        if hasattr(self.player_currenttrack, "length"):
            return int(self.player_currenttrack.length / 1000)
        return None

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        return self._media_position

    @property
    def media_position_updated_at(self):
        """Last valid time of media position."""
        return self._media_position_updated_at

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        return self._media_image_url

    @property
    def media_image_remotely_accessible(self):
        """If the image url is remotely accessible."""
        return False

    @property
    def media_title(self):
        """Return the title of current playing media."""
        if self.player_streamttile is not None:
            return self.player_streamttile

        if hasattr(self.player_currenttrack, "name"):
            return self.player_currenttrack.name
        return None

    @property
    def media_artist(self):
        """Artist of current playing media, music track only."""
        if self.player_streamttile is not None:
            if hasattr(self.player_currenttrack, "name"):
                return self.player_currenttrack.name

        if hasattr(self.player_currenttrack, "artists"):
            return ", ".join([a.name for a in self.player_currenttrack.artists])
        return None

    @property
    def media_album_name(self):
        """Album name of current playing media, music track only."""
        if hasattr(self.player_currenttrack, "album") and hasattr(
            self.player_currenttrack.album, "name"
        ):
            return self.player_currenttrack.album.name
        return None

    @property
    def media_album_artist(self):
        """Album artist of current playing media, music track only."""
        if hasattr(self.player_currenttrack, "artists"):
            return ", ".join([a.name for a in self.player_currenttrack.artists])
        return None

    @property
    def media_track(self):
        """Track number of current playing media, music track only."""
        if hasattr(self.player_currenttrack, "track_no"):
            return self.player_currenttrack.track_no
        return None

    @property
    def media_playlist(self):
        """Title of Playlist currently playing."""
        if self._currentplaylist is not None:
            return self._currentplaylist

        if hasattr(self.player_currenttrack, "album") and hasattr(
            self.player_currenttrack.album, "name"
        ):
            return self.player_currenttrack.album.name

        return None

    @property
    def shuffle(self):
        """Boolean if shuffle is enabled."""
        return self._shuffled

    @property
    def repeat(self):
        """Return current repeat mode."""
        return self._repeat_mode

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        support = SUPPORT_MOPIDY
        if self._has_support_volume:
            support = (
                support | SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET | SUPPORT_VOLUME_STEP
            )
        return support

    @property
    def source(self):
        """Name of the current input source."""
        return None

    @property
    def source_list(self):
        """Return the list of available input sources."""
        return [el.name for el in self._playlists]

    def mute_volume(self, mute):
        """Mute the volume."""
        self.client.mixer.set_mute(mute)

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        self.client.mixer.set_volume(int(volume * 100))

    def turn_off(self):
        """Turn the media player off."""
        self.client.playback.stop()

    def turn_on(self):
        """Turn the media player on."""
        self.client.playback.play()

    def media_play(self):
        """Send play command."""
        self.client.playback.play()

    def media_pause(self):
        """Send pause command."""
        self.client.playback.pause()

    def media_stop(self):
        """Send stop command."""
        self.client.playback.stop()

    def media_previous_track(self):
        """Send previous track command."""
        self.client.playback.previous()

    def media_next_track(self):
        """Send next track command."""
        self.client.playback.next()

    def media_seek(self, position):
        """Send seek command."""
        self.client.playback.seek(int(position * 1000))

    def play_media(self, media_type, media_id, **kwargs):
        """Play a piece of media."""
        self._currentplaylist = None

        if media_type == MEDIA_TYPE_PLAYLIST:
            p = self.client.playlists.lookup(media_id)
            self._currentplaylist = p.name
            if media_id.partition(":")[0] == "m3u":
                media_uris = [t.uri for t in p.tracks]
            else:
                media_uris = [media_id]
        else:
            media_uris = [media_id]

        t_uris = []
        schemes = self.client.rpc_call("core.get_uri_schemes")
        for uri in media_uris:
            if "yt" in schemes and (
                uri.startswith("https://www.youtube.com/")
                or uri.startswith("https://youtube.com/")
                or uri.startswith("https://youtu.be/")
            ):
                t_uris.append(f"yt:{uri}")
            else:
                t_uris.append(uri)

        media_uris = t_uris

        if len(media_uris) > 0:
            self.client.tracklist.clear()
            self.client.tracklist.add(uris=media_uris)
            self.client.playback.play()

        else:
            _LOGGER.error("No media for %s (%s) could be found.", media_id, media_type)
            raise MissingMediaInformation

    def select_source(self, source):
        """Select input source."""
        for el in self._playlists:
            if el.name == source:
                self.play_media(MEDIA_TYPE_PLAYLIST, el.uri)
                return el.uri
        raise ValueError(f"Could not find {source}")

    def clear_playlist(self):
        """Clear players playlist."""
        self.client.tracklist.clear()

    def set_shuffle(self, shuffle):
        """Enable/disable shuffle mode."""
        self.client.tracklist.set_random(shuffle)

    def set_repeat(self, repeat):
        """Set repeat mode."""
        if repeat == REPEAT_MODE_ALL:
            self.client.tracklist.set_repeat(True)
            self.client.tracklist.set_single(False)
        elif repeat == REPEAT_MODE_ONE:
            self.client.tracklist.set_repeat(True)
            self.client.tracklist.set_single(True)
        else:
            self.client.tracklist.set_repeat(False)
            self.client.tracklist.set_single(False)

    def volume_up(self):
        """Turn volume up for media player."""
        new_volume = self.client.mixer.get_volume() + 5
        if new_volume > 100:
            new_volume = 100

        self.client.mixer.set_volume(new_volume)

    def volume_down(self):
        """Turn volume down for media player."""
        new_volume = self.client.mixer.get_volume() - 5
        if new_volume < 0:
            new_volume = 0

        self.client.mixer.set_volume(new_volume)

    @property
    def device_class(self):
        """Return the device class"""
        return "speaker"

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "indentifiers": {(DOMAIN, self.device_name)},
            "manufacturer": "Mopidy",
            "model": f"Mopidy server {self.server_version}",
            "name": self.device_name,
            "sw_version": self.server_version,
        }

    def _connect(self):
        try:
            self.client = MopidyAPI(
                host=self.hostname, port=self.port, use_websocket=False
            )
            self.server_version = self.client.rpc_call("core.get_version")
            _LOGGER.debug(
                "Connection to Mopidy server %s (%s:%s) established",
                self.device_name,
                self.hostname,
                self.port,
            )
        except reConnectionError as error:
            _LOGGER.error(
                "Cannot connect to %s @ %s:%s",
                self.device_name,
                self.hostname,
                self.port,
            )
            _LOGGER.error(error)
            self._available = False
            return
        self._available = True

    def update(self):
        """Get the latest data and update the state."""
        if self._available is None:
            self._connect()

        if self._available:
            self._fetch_status()

    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        """Implement the websocket media browsing helper."""

        return await self.hass.async_add_executor_job(
            self._media_library_payload,
            dict(
                media_content_type=(
                    "library" if media_content_type is None else media_content_type
                ),
                media_content_id=(
                    "library" if media_content_id is None else media_content_id
                ),
            ),
        )

    def _media_item_image_url(self, source, url):
        """Return the correct url to the item's thumbnail."""

        if source == "local":
            url = f"http://{self.hostname}:{self.port}{url}"

        url = f"{url}?t=x"
        return url

    def _media_library_payload(self, payload):
        """Create response payload to describe contents of a specific library."""
        source = None

        try:
            payload["media_content_type"]
            payload["media_content_id"]
        except KeyError as err:
            _LOGGER.error("Missing type or uri for media item payload: %s", payload)
            raise MissingMediaInformation from err

        library_info = dict(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id="library",
            media_content_type="library",
            title="Media Library",
            can_play=False,
            can_expand=True,
            children=[],
        )
        library_info.update(payload)

        if payload["media_content_id"] == "library":
            library_items = self.client.library.browse(None)
            library_info["title"] = "Media Library"
        else:
            source = payload["media_content_id"].partition(":")[0]
            library_items = self.client.library.browse(payload["media_content_id"])
            extra_info = fetch_media_info(
                payload["media_content_type"], payload["media_content_id"]
            )
            library_info.update(extra_info)
            image = self.client.library.get_images([payload["media_content_id"]])
            if (
                payload["media_content_id"] in image
                and len(image[payload["media_content_id"]]) > 0
            ):
                library_info["thumbnail"] = self._media_item_image_url(
                    source, image[payload["media_content_id"]][0].uri
                )

        children_uri = []
        for item in library_items:
            library_info["children"].append(
                self._media_item_payload(
                    {"name": item.name, "type": item.type, "uri": item.uri}
                )
            )
            children_uri.append(item.uri)

        if source == "spotify":
            # Spotify thumbnail lookup is throttled
            s = 10
        else:
            s = 1000
        uri_set = [
            children_uri[r * s : (r + 1) * s]
            for r in range((len(children_uri) + s - 1) // s)
        ]

        images = dict()
        for s in uri_set:
            images.update(self.client.library.get_images(s))

        if len(images.keys()) > 0:
            for item in library_info["children"]:
                if (
                    item.media_content_id in images
                    and len(images[item.media_content_id]) > 0
                ):
                    item.thumbnail = self._media_item_image_url(
                        source, images[item.media_content_id][0].uri
                    )

        library_info["can_play"] = (
            library_info["media_content_type"] in PLAYABLE_MEDIA_TYPES
        )

        if payload["media_content_id"] in CACHE_ROSETTA:
            library_info["title"] = CACHE_ROSETTA[payload["media_content_id"]]

        r = BrowseMedia(**library_info)
        try:
            r.children_media_class = extra_info["children_media_class"]
        except:
            r.children_media_class = MEDIA_CLASS_DIRECTORY
        return r

    def _media_item_payload(self, item):
        try:
            media_type = item["type"]
            media_id = item["uri"]
        except KeyError as err:
            _LOGGER.error("Missing type or uri for media item: %s", item)
            raise MissingMediaInformation from err

        media_class = MEDIA_CLASS_DIRECTORY
        can_expand = media_type not in [MEDIA_TYPE_TRACK]
        can_play = media_type in PLAYABLE_MEDIA_TYPES

        payload = dict(
            media_class=media_class,
            media_content_id=media_id,
            media_content_type=media_type,
            can_play=can_play,
            can_expand=can_expand,
            title=item.get("name"),
        )
        CACHE_ROSETTA[media_id] = payload["title"]
        extra_info = fetch_media_info(media_type, media_id)
        payload.update(extra_info)
        return BrowseMedia(**payload)


def fetch_media_info(
    media_type=None,
    media_uri=None,
    defaults={},
):
    """Fetch addional media information which is not available through the mopidy API"""

    res = dict()
    res["media_class"] = defaults.get("media_class")
    res["children_media_class"] = defaults.get("children_media_class")

    if media_type is None or media_uri is None:
        return res

    source = media_uri.partition(":")[0]
    uri = media_uri.partition(":")[2]

    if False:
        _LOGGER.debug(f"media_type: {media_type}")
        _LOGGER.debug(f"media_uri: {media_uri}")
        _LOGGER.debug(f"source: {source}")
        _LOGGER.debug(f"uri: {uri}")

    if media_type == "directory":
        res["media_class"] = MEDIA_CLASS_DIRECTORY
        res["children_media_class"] = MEDIA_CLASS_DIRECTORY

    elif media_type == "album":
        res["media_class"] = MEDIA_CLASS_ALBUM
        res["children_media_class"] = MEDIA_CLASS_TRACK

    elif media_type == "artist":
        res["media_class"] = MEDIA_CLASS_ARTIST
        res["children_media_class"] = MEDIA_CLASS_TRACK

    elif media_type == "track":
        res["media_class"] = MEDIA_CLASS_TRACK
        res["children_media_class"] = MEDIA_CLASS_TRACK

    elif media_type == "playlist":
        res["media_class"] = MEDIA_CLASS_PLAYLIST
        res["children_media_class"] = MEDIA_CLASS_TRACK

    if source == "local":
        media_info = {}
        for el in uri.partition("?")[2].split("&"):
            if el != "":
                media_info[el.partition("=")[0]] = el.partition("=")[2]

        if media_type == "directory" and media_info.get("type") == "album":
            res["title"] = "Albums"
            res["media_class"] = MEDIA_CLASS_ALBUM
            res["children_media_class"] = MEDIA_CLASS_ALBUM

        elif media_type == "directory" and media_info.get("type") == "artist":
            res["media_class"] = MEDIA_CLASS_ARTIST
            res["children_media_class"] = MEDIA_CLASS_ARTIST
            if media_info.get("role") == "composer":
                res["title"] = "Composer"
                res["media_class"] = MEDIA_CLASS_COMPOSER
                res["children_media_class"] = MEDIA_CLASS_COMPOSER
            elif media_info.get("role") == "performer":
                res["title"] = "Performer"
            else:
                res["title"] = "Artists"

        elif (
            media_type == "directory"
            and media_info.get("composer") is not None
            and media_info.get("album") is not None
        ):
            res["media_class"] = MEDIA_CLASS_ALBUM
            res["children_media_class"] = MEDIA_CLASS_TRACK

        elif media_type == "directory" and media_info.get("composer") is not None:
            res["media_class"] = MEDIA_CLASS_COMPOSER
            res["children_media_class"] = MEDIA_CLASS_ALBUM

        elif (
            media_type == "directory"
            and media_info.get("genre") is not None
            and media_info.get("album") is not None
        ):
            res["media_class"] = MEDIA_CLASS_ALBUM
            res["children_media_class"] = MEDIA_CLASS_TRACK

        elif media_type == "directory" and media_info.get("genre") is not None:
            res["media_class"] = MEDIA_CLASS_GENRE
            res["children_media_class"] = MEDIA_CLASS_ALBUM

        elif media_type == "directory" and media_info.get("type") == "genre":
            res["title"] = "Genres"
            res["media_class"] = MEDIA_CLASS_GENRE
            res["children_media_class"] = MEDIA_CLASS_GENRE

        elif (
            media_type == "directory"
            and media_info.get("type") == "track"
            and media_info.get("album") is not None
        ):
            res["media_class"] = MEDIA_CLASS_ALBUM
            res["children_media_class"] = MEDIA_CLASS_TRACK

        elif media_type == "directory" and media_info.get("type") == "track":
            res["media_class"] = MEDIA_CLASS_TRACK
            res["children_media_class"] = MEDIA_CLASS_TRACK

        elif media_type == "artist":
            res["media_class"] = MEDIA_CLASS_ARTIST
            res["children_media_class"] = MEDIA_CLASS_ALBUM

    elif source == "spotify":
        if media_type == "directory" and uri == "top:tracks:countries":
            res["media_class"] = MEDIA_CLASS_DIRECTORY
            res["children_media_class"] = MEDIA_CLASS_DIRECTORY

        elif media_type == "directory" and "top:tracks:" in uri:
            res["media_class"] = MEDIA_CLASS_DIRECTORY
            res["children_media_class"] = MEDIA_CLASS_TRACK

        elif media_type == "directory" and uri in [
            "top:albums",
            "top:albums:countries",
        ]:
            res["media_class"] = MEDIA_CLASS_DIRECTORY
            res["children_media_class"] = MEDIA_CLASS_ALBUM

        elif media_type == "directory" and "top:albums:" in uri:
            res["media_class"] = MEDIA_CLASS_DIRECTORY
            res["children_media_class"] = MEDIA_CLASS_ALBUM

        elif media_type == "directory" and uri in [
            "top:artists",
            "top:artists:countries",
        ]:
            res["media_class"] = MEDIA_CLASS_ARTIST
            res["children_media_class"] = MEDIA_CLASS_ARTIST

        elif media_type == "directory" and "top:artists:" in uri:
            res["media_class"] = MEDIA_CLASS_ARTIST
            res["children_media_class"] = MEDIA_CLASS_ARTIST

        elif media_type == "directory" and uri == "your:tracks":
            res["media_class"] = MEDIA_CLASS_DIRECTORY
            res["children_media_class"] = MEDIA_CLASS_TRACK

        elif media_type == "directory" and uri == "your:albums":
            res["media_class"] = MEDIA_CLASS_DIRECTORY
            res["children_media_class"] = MEDIA_CLASS_ALBUM

        elif media_type == "directory" and uri == "top":
            res["title"] = "Top Lists"

        elif media_type == "directory" and uri == "directory":
            res["title"] = "Spotify"

    elif source[:7] == "podcast":
        if media_type == "album":
            res["media_class"] = MEDIA_CLASS_DIRECTORY
            res["children_media_class"] = MEDIA_CLASS_PODCAST

        elif media_type == "track":
            res["media_class"] = MEDIA_CLASS_PODCAST
            res["children_media_class"] = MEDIA_CLASS_PODCAST

    return res
