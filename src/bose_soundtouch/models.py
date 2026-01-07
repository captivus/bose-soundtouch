"""Data models for the bose_soundtouch library."""

from __future__ import annotations

from dataclasses import dataclass, field

from bose_soundtouch.enums import ArtStatus, AudioMode, PlayStatus, SourceStatus


# ============ Device Info Models ============


@dataclass(frozen=True)
class NetworkInfo:
    """Network interface information."""

    type: str
    """Network type (e.g., "WIFI", "ETHERNET")."""

    mac_address: str
    """MAC address of the interface."""

    ip_address: str
    """IP address of the interface."""


@dataclass(frozen=True)
class Component:
    """Device component information (SCM, LPM, etc.)."""

    category: str
    """Component category."""

    software_version: str
    """Software version of the component."""

    serial_number: str | None = None
    """Serial number of the component."""


@dataclass(frozen=True)
class DeviceInfo:
    """Device information from the /info endpoint."""

    device_id: str
    """Device MAC address identifier."""

    name: str
    """Device display name."""

    type: str
    """Device type (e.g., "SoundTouch 10", "SoundTouch 300")."""

    account_uuid: str | None = None
    """Cloud account UUID."""

    marge_url: str | None = None
    """Bose cloud service URL."""

    components: list[Component] = field(default_factory=list)
    """List of device components."""

    network_info: list[NetworkInfo] = field(default_factory=list)
    """List of network interfaces."""


# ============ Content Models ============


@dataclass(frozen=True)
class ContentItem:
    """A content item (track, station, source)."""

    source: str
    """Content source (e.g., "SPOTIFY", "TUNEIN", "AUX")."""

    location: str | None = None
    """Source-specific location identifier."""

    source_account: str | None = None
    """Source account identifier."""

    is_presetable: bool = False
    """Whether this content can be saved to a preset."""

    item_name: str | None = None
    """Display name of the content item."""


@dataclass(frozen=True)
class Art:
    """Album art information."""

    url: str | None = None
    """URL of the album art image."""

    status: ArtStatus = ArtStatus.INVALID
    """Status of the album art."""


@dataclass(frozen=True)
class NowPlaying:
    """Current playback state from the /now_playing endpoint."""

    device_id: str
    """Device MAC address identifier."""

    source: str
    """Current content source."""

    content_item: ContentItem | None = None
    """Current content item being played."""

    track: str | None = None
    """Track name."""

    artist: str | None = None
    """Artist name."""

    album: str | None = None
    """Album name."""

    station_name: str | None = None
    """Station name (for radio sources)."""

    art: Art | None = None
    """Album art information."""

    play_status: PlayStatus = PlayStatus.INVALID_PLAY_STATUS
    """Current playback status."""

    description: str | None = None
    """Content description."""

    station_location: str | None = None
    """Station location (for radio sources)."""


# ============ Source Models ============


@dataclass(frozen=True)
class SourceItem:
    """An available content source."""

    source: str
    """Source identifier."""

    source_account: str | None
    """Source account identifier."""

    status: SourceStatus
    """Availability status."""

    display_name: str | None = None
    """Human-readable display name."""


@dataclass(frozen=True)
class Sources:
    """List of available sources from the /sources endpoint."""

    device_id: str
    """Device MAC address identifier."""

    items: list[SourceItem] = field(default_factory=list)
    """List of available source items."""


# ============ Volume Models ============


@dataclass(frozen=True)
class Volume:
    """Volume state from the /volume endpoint."""

    device_id: str
    """Device MAC address identifier."""

    target_volume: int
    """Target volume level (0-100)."""

    actual_volume: int
    """Actual current volume level (0-100)."""

    mute_enabled: bool
    """Whether mute is enabled."""


# ============ Bass Models ============


@dataclass(frozen=True)
class BassCapabilities:
    """Bass control capabilities from the /bassCapabilities endpoint."""

    device_id: str
    """Device MAC address identifier."""

    bass_available: bool
    """Whether bass control is available."""

    bass_min: int
    """Minimum bass level."""

    bass_max: int
    """Maximum bass level."""

    bass_default: int
    """Default bass level."""


@dataclass(frozen=True)
class Bass:
    """Bass state from the /bass endpoint."""

    device_id: str
    """Device MAC address identifier."""

    target_bass: int
    """Target bass level."""

    actual_bass: int
    """Actual current bass level."""


# ============ Preset Models ============


@dataclass(frozen=True)
class Preset:
    """A preset slot (1-6)."""

    id: int
    """Preset ID (1-6)."""

    content_item: ContentItem | None = None
    """Content item saved to this preset."""

    created_on: int | None = None
    """Timestamp when preset was created."""

    updated_on: int | None = None
    """Timestamp when preset was last updated."""


@dataclass(frozen=True)
class Presets:
    """List of presets from the /presets endpoint."""

    items: list[Preset] = field(default_factory=list)
    """List of preset slots."""


# ============ Zone Models ============


@dataclass(frozen=True)
class ZoneMember:
    """A member of a multi-room zone."""

    mac_address: str
    """MAC address of the zone member."""

    ip_address: str
    """IP address of the zone member."""


@dataclass(frozen=True)
class Zone:
    """Multi-room zone configuration from the /getZone endpoint."""

    master_mac: str | None = None
    """MAC address of the zone master."""

    members: list[ZoneMember] = field(default_factory=list)
    """List of zone members."""


# ============ Capability Models ============


@dataclass(frozen=True)
class Capability:
    """A device capability."""

    name: str
    """Capability name."""

    url: str
    """URL endpoint for this capability."""

    info: str | None = None
    """Additional capability information."""


@dataclass(frozen=True)
class Capabilities:
    """Device capabilities from the /capabilities endpoint."""

    device_id: str
    """Device MAC address identifier."""

    items: list[Capability] = field(default_factory=list)
    """List of device capabilities."""


# ============ Audio DSP Models ============


@dataclass(frozen=True)
class AudioDspControls:
    """Audio DSP settings from the /audiodspcontrols endpoint."""

    audio_mode: AudioMode
    """Current audio mode."""

    video_sync_audio_delay: int
    """Video sync audio delay in milliseconds."""

    supported_audio_modes: list[AudioMode] = field(default_factory=list)
    """List of supported audio modes."""


# ============ Tone Control Models ============


@dataclass(frozen=True)
class ToneControl:
    """Bass or treble tone control setting."""

    value: int
    """Current value."""

    min_value: int
    """Minimum allowed value."""

    max_value: int
    """Maximum allowed value."""

    step: int
    """Step increment."""


@dataclass(frozen=True)
class ToneControls:
    """Tone controls from the /audioproducttonecontrols endpoint."""

    bass: ToneControl | None = None
    """Bass control settings."""

    treble: ToneControl | None = None
    """Treble control settings."""


# ============ Speaker Level Models ============


@dataclass(frozen=True)
class SpeakerLevel:
    """Speaker level setting."""

    value: int
    """Current value."""

    min_value: int
    """Minimum allowed value."""

    max_value: int
    """Maximum allowed value."""

    step: int
    """Step increment."""


@dataclass(frozen=True)
class LevelControls:
    """Level controls from the /audioproductlevelcontrols endpoint."""

    front_center: SpeakerLevel | None = None
    """Front center speaker level settings."""

    rear_surround: SpeakerLevel | None = None
    """Rear surround speakers level settings."""
