"""SoundTouch client for controlling Bose SoundTouch devices."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from bose_soundtouch import xml_parser
from bose_soundtouch.enums import AudioMode, KeyState, KeyValue
from bose_soundtouch.exceptions import (
    ConnectionError,
    SoundTouchError,
    TimeoutError,
)
from bose_soundtouch.models import (
    AudioDspControls,
    Bass,
    BassCapabilities,
    Capabilities,
    ContentItem,
    DeviceInfo,
    LevelControls,
    NowPlaying,
    Presets,
    Sources,
    ToneControls,
    Volume,
    Zone,
    ZoneMember,
)

if TYPE_CHECKING:
    from typing import Self


class SoundTouch:
    """
    Client for interacting with a Bose SoundTouch device.

    This class provides methods to control playback, volume, presets,
    and other features of a SoundTouch speaker.

    Example:
        >>> with SoundTouch(host="192.168.1.100") as speaker:
        ...     speaker.set_volume(level=30)
        ...     speaker.play()
    """

    DEFAULT_PORT: int = 8090
    DEFAULT_TIMEOUT: float = 10.0
    # Note: "Gabbo" is the sender name from Bose's API documentation
    # and appears to be required/whitelisted by the device
    DEFAULT_SENDER: str = "Gabbo"

    def __init__(
        self,
        host: str,
        *,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize SoundTouch client.

        Args:
            host: IP address or hostname of the SoundTouch device.
            port: HTTP port (default 8090).
            timeout: Request timeout in seconds.
        """
        self._host = host
        self._port = port
        self._timeout = timeout
        self._base_url = f"http://{host}:{port}"
        self._client = httpx.Client(timeout=timeout)

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager and close client."""
        self.close()

    def __repr__(self) -> str:
        """Return string representation."""
        return f"SoundTouch(host={self._host!r}, port={self._port})"

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    @property
    def host(self) -> str:
        """Device host address."""
        return self._host

    @property
    def port(self) -> int:
        """Device port."""
        return self._port

    # ============ HTTP Methods ============

    def _get(self, endpoint: str) -> str:
        """
        Make GET request, return response text.

        Args:
            endpoint: API endpoint path.

        Returns:
            Response text.

        Raises:
            ConnectionError: If connection fails.
            TimeoutError: If request times out.
            SoundTouchError: For other HTTP errors.
        """
        try:
            response = self._client.get(f"{self._base_url}{endpoint}")
            response.raise_for_status()
            return response.text
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {self._host}") from e
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request to {self._host} timed out") from e
        except httpx.HTTPStatusError as e:
            raise SoundTouchError(f"HTTP error: {e}") from e

    def _post(self, endpoint: str, body: str) -> str:
        """
        Make POST request with XML body, return response text.

        Args:
            endpoint: API endpoint path.
            body: XML request body.

        Returns:
            Response text.

        Raises:
            ConnectionError: If connection fails.
            TimeoutError: If request times out.
            SoundTouchError: For other HTTP errors.
        """
        try:
            response = self._client.post(
                f"{self._base_url}{endpoint}",
                content=body,
                headers={"Content-Type": "application/xml"},
            )
            response.raise_for_status()
            return response.text
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {self._host}") from e
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request to {self._host} timed out") from e
        except httpx.HTTPStatusError as e:
            raise SoundTouchError(f"HTTP error: {e}") from e

    def _get_and_parse[T](self, endpoint: str, parser: callable) -> T:
        """
        GET endpoint, parse XML, check errors, return parsed model.

        Args:
            endpoint: API endpoint path.
            parser: Function to parse the XML response.

        Returns:
            Parsed model.
        """
        text = self._get(endpoint)
        root = xml_parser.parse_xml(text)
        xml_parser.check_for_errors(root)
        return parser(root)

    def _post_and_check(self, endpoint: str, body: str) -> None:
        """
        POST to endpoint and check for errors.

        Args:
            endpoint: API endpoint path.
            body: XML request body.
        """
        text = self._post(endpoint, body)
        root = xml_parser.parse_xml(text)
        xml_parser.check_for_errors(root)

    # ============ Device Info ============

    def get_info(self) -> DeviceInfo:
        """
        Get device information.

        Returns:
            Device information including name, type, and network info.
        """
        return self._get_and_parse("/info", xml_parser.parse_device_info)

    def get_capabilities(self) -> Capabilities:
        """
        Get device capabilities.

        Returns:
            List of device capabilities and their URLs.
        """
        return self._get_and_parse("/capabilities", xml_parser.parse_capabilities)

    def set_name(self, *, name: str) -> None:
        """
        Set device name.

        Args:
            name: New device name.
        """
        body = xml_parser.build_name_xml(name=name)
        self._post_and_check("/name", body)

    # ============ Now Playing ============

    def get_now_playing(self) -> NowPlaying:
        """
        Get current playback state.

        Returns:
            Current playback information including track, artist, and status.
        """
        return self._get_and_parse("/now_playing", xml_parser.parse_now_playing)

    def get_track_info(self) -> NowPlaying:
        """
        Get detailed track information.

        Returns:
            Track information (same format as now_playing).
        """
        return self._get_and_parse("/trackInfo", xml_parser.parse_now_playing)

    # ============ Sources ============

    def get_sources(self) -> Sources:
        """
        Get available content sources.

        Returns:
            List of available sources and their status.
        """
        return self._get_and_parse("/sources", xml_parser.parse_sources)

    def select_source(
        self,
        *,
        source: str,
        source_account: str | None = None,
        location: str | None = None,
        item_name: str | None = None,
    ) -> None:
        """
        Select a content source.

        Args:
            source: Source identifier (e.g., "AUX", "BLUETOOTH").
            source_account: Source account identifier.
            location: Source-specific location.
            item_name: Item display name.
        """
        content_item = ContentItem(
            source=source,
            source_account=source_account,
            location=location,
            item_name=item_name,
        )
        body = xml_parser.build_select_xml(content_item=content_item)
        self._post_and_check("/select", body)

    def select_content_item(self, *, content_item: ContentItem) -> None:
        """
        Select a ContentItem directly.

        Args:
            content_item: Content item to select.
        """
        body = xml_parser.build_select_xml(content_item=content_item)
        self._post_and_check("/select", body)

    # ============ Volume ============

    def get_volume(self) -> Volume:
        """
        Get current volume state.

        Returns:
            Volume information including level and mute status.
        """
        return self._get_and_parse("/volume", xml_parser.parse_volume)

    def set_volume(self, *, level: int) -> None:
        """
        Set volume level.

        Args:
            level: Volume level (0-100).
        """
        body = xml_parser.build_volume_xml(volume=level, mute=None)
        self._post_and_check("/volume", body)

    def set_mute(self, *, enabled: bool) -> None:
        """
        Set mute state.

        Args:
            enabled: True to mute, False to unmute.
        """
        body = xml_parser.build_volume_xml(volume=None, mute=enabled)
        self._post_and_check("/volume", body)

    def mute(self) -> None:
        """Mute the device."""
        self.set_mute(enabled=True)

    def unmute(self) -> None:
        """Unmute the device."""
        self.set_mute(enabled=False)

    # ============ Bass ============

    def get_bass_capabilities(self) -> BassCapabilities:
        """
        Get bass control capabilities.

        Returns:
            Bass capabilities including min, max, and default values.
        """
        return self._get_and_parse(
            "/bassCapabilities", xml_parser.parse_bass_capabilities
        )

    def get_bass(self) -> Bass:
        """
        Get current bass level.

        Returns:
            Current bass level information.
        """
        return self._get_and_parse("/bass", xml_parser.parse_bass)

    def set_bass(self, *, level: int) -> None:
        """
        Set bass level.

        Args:
            level: Bass level (within device's min/max range).
        """
        body = xml_parser.build_bass_xml(bass=level)
        self._post_and_check("/bass", body)

    # ============ Presets ============

    def get_presets(self) -> Presets:
        """
        Get preset slots.

        Returns:
            List of preset slots (1-6) and their content.
        """
        return self._get_and_parse("/presets", xml_parser.parse_presets)

    # ============ Key Presses ============

    def send_key(
        self,
        *,
        key: KeyValue | str,
        sender: str = DEFAULT_SENDER,
    ) -> None:
        """
        Send a key press (press + release) to the device.

        This method sends both a press and release event for the specified key,
        simulating a button press on a remote control.

        Args:
            key: The key to send (KeyValue enum or string).
            sender: Identifier for the sender (default: library name).
        """
        key_str = key.value if isinstance(key, KeyValue) else key

        # Send press
        body = xml_parser.build_key_xml(
            key=key_str,
            state=KeyState.PRESS,
            sender=sender,
        )
        self._post_and_check("/key", body)

        # Send release
        body = xml_parser.build_key_xml(
            key=key_str,
            state=KeyState.RELEASE,
            sender=sender,
        )
        self._post_and_check("/key", body)

    # Convenience methods for common keys

    def play(self) -> None:
        """Start playback."""
        self.send_key(key=KeyValue.PLAY)

    def pause(self) -> None:
        """Pause playback."""
        self.send_key(key=KeyValue.PAUSE)

    def play_pause(self) -> None:
        """Toggle play/pause."""
        self.send_key(key=KeyValue.PLAY_PAUSE)

    def stop(self) -> None:
        """Stop playback."""
        self.send_key(key=KeyValue.STOP)

    def next_track(self) -> None:
        """Skip to next track."""
        self.send_key(key=KeyValue.NEXT_TRACK)

    def previous_track(self) -> None:
        """Skip to previous track."""
        self.send_key(key=KeyValue.PREV_TRACK)

    def power(self) -> None:
        """Toggle power state."""
        self.send_key(key=KeyValue.POWER)

    def volume_up(self) -> None:
        """Increase volume."""
        self.send_key(key=KeyValue.VOLUME_UP)

    def volume_down(self) -> None:
        """Decrease volume."""
        self.send_key(key=KeyValue.VOLUME_DOWN)

    def select_preset(self, *, preset_id: int) -> None:
        """
        Select a preset (1-6).

        Args:
            preset_id: Preset number (1-6).

        Raises:
            ValueError: If preset_id is not between 1 and 6.
        """
        if preset_id < 1 or preset_id > 6:
            raise ValueError("preset_id must be between 1 and 6")
        key = KeyValue[f"PRESET_{preset_id}"]
        self.send_key(key=key)

    def shuffle_on(self) -> None:
        """Enable shuffle."""
        self.send_key(key=KeyValue.SHUFFLE_ON)

    def shuffle_off(self) -> None:
        """Disable shuffle."""
        self.send_key(key=KeyValue.SHUFFLE_OFF)

    def repeat_off(self) -> None:
        """Disable repeat."""
        self.send_key(key=KeyValue.REPEAT_OFF)

    def repeat_one(self) -> None:
        """Repeat current track."""
        self.send_key(key=KeyValue.REPEAT_ONE)

    def repeat_all(self) -> None:
        """Repeat all tracks."""
        self.send_key(key=KeyValue.REPEAT_ALL)

    def thumbs_up(self) -> None:
        """Rate track thumbs up."""
        self.send_key(key=KeyValue.THUMBS_UP)

    def thumbs_down(self) -> None:
        """Rate track thumbs down."""
        self.send_key(key=KeyValue.THUMBS_DOWN)

    def add_favorite(self) -> None:
        """Add current track to favorites."""
        self.send_key(key=KeyValue.ADD_FAVORITE)

    def remove_favorite(self) -> None:
        """Remove current track from favorites."""
        self.send_key(key=KeyValue.REMOVE_FAVORITE)

    def bookmark(self) -> None:
        """Bookmark current track/station."""
        self.send_key(key=KeyValue.BOOKMARK)

    # ============ Multi-Room Zones ============

    def get_zone(self) -> Zone:
        """
        Get current multi-room zone configuration.

        Returns:
            Zone configuration including master and member devices.
        """
        return self._get_and_parse("/getZone", xml_parser.parse_zone)

    def set_zone(
        self,
        *,
        master_mac: str,
        members: list[ZoneMember],
        sender_ip: str | None = None,
    ) -> None:
        """
        Create a multi-room zone.

        Args:
            master_mac: MAC address of the zone master.
            members: List of zone members.
            sender_ip: IP address of the sender (optional).
        """
        body = xml_parser.build_zone_xml(
            master_mac=master_mac,
            members=members,
            sender_ip=sender_ip,
        )
        self._post_and_check("/setZone", body)

    def add_zone_slave(
        self,
        *,
        master_mac: str,
        members: list[ZoneMember],
    ) -> None:
        """
        Add speakers to a zone.

        Args:
            master_mac: MAC address of the zone master.
            members: List of zone members to add.
        """
        body = xml_parser.build_zone_member_xml(
            master_mac=master_mac,
            members=members,
        )
        self._post_and_check("/addZoneSlave", body)

    def remove_zone_slave(
        self,
        *,
        master_mac: str,
        members: list[ZoneMember],
    ) -> None:
        """
        Remove speakers from a zone.

        Args:
            master_mac: MAC address of the zone master.
            members: List of zone members to remove.
        """
        body = xml_parser.build_zone_member_xml(
            master_mac=master_mac,
            members=members,
        )
        self._post_and_check("/removeZoneSlave", body)

    # ============ Audio DSP (optional capability) ============

    def get_audio_dsp_controls(self) -> AudioDspControls:
        """
        Get audio DSP settings.

        Note: Requires audiodspcontrols capability.

        Returns:
            Audio DSP settings including audio mode.
        """
        return self._get_and_parse(
            "/audiodspcontrols", xml_parser.parse_audio_dsp_controls
        )

    def set_audio_mode(self, *, mode: AudioMode) -> None:
        """
        Set audio mode.

        Note: Requires audiodspcontrols capability.

        Args:
            mode: Audio mode to set.
        """
        body = xml_parser.build_audio_dsp_xml(audio_mode=mode, delay=None)
        self._post_and_check("/audiodspcontrols", body)

    def set_video_sync_delay(self, *, delay: int) -> None:
        """
        Set video sync audio delay.

        Note: Requires audiodspcontrols capability.

        Args:
            delay: Delay in milliseconds.
        """
        body = xml_parser.build_audio_dsp_xml(audio_mode=None, delay=delay)
        self._post_and_check("/audiodspcontrols", body)

    # ============ Tone Controls (optional capability) ============

    def get_tone_controls(self) -> ToneControls:
        """
        Get tone controls.

        Note: Requires audioproducttonecontrols capability.

        Returns:
            Tone control settings for bass and treble.
        """
        return self._get_and_parse(
            "/audioproducttonecontrols", xml_parser.parse_tone_controls
        )

    def set_tone_controls(
        self,
        *,
        bass: int | None = None,
        treble: int | None = None,
    ) -> None:
        """
        Set bass and/or treble levels.

        Note: Requires audioproducttonecontrols capability.

        Args:
            bass: Bass value to set, or None to not change.
            treble: Treble value to set, or None to not change.
        """
        body = xml_parser.build_tone_controls_xml(bass=bass, treble=treble)
        self._post_and_check("/audioproducttonecontrols", body)

    # ============ Level Controls (optional capability) ============

    def get_level_controls(self) -> LevelControls:
        """
        Get speaker level controls.

        Note: Requires audioproductlevelcontrols capability.

        Returns:
            Speaker level settings.
        """
        return self._get_and_parse(
            "/audioproductlevelcontrols", xml_parser.parse_level_controls
        )

    def set_level_controls(
        self,
        *,
        front_center: int | None = None,
        rear_surround: int | None = None,
    ) -> None:
        """
        Set speaker levels.

        Note: Requires audioproductlevelcontrols capability.

        Args:
            front_center: Front center speaker level, or None to not change.
            rear_surround: Rear surround speakers level, or None to not change.
        """
        body = xml_parser.build_level_controls_xml(
            front_center=front_center,
            rear_surround=rear_surround,
        )
        self._post_and_check("/audioproductlevelcontrols", body)
