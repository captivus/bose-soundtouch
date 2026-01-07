"""
Bose SoundTouch Python Library

A Python library for controlling Bose SoundTouch speakers via the REST API.

Example:
    >>> from bose_soundtouch import SoundTouch
    >>> with SoundTouch(host="192.168.1.100") as speaker:
    ...     speaker.set_volume(level=30)
    ...     speaker.play()
"""

from bose_soundtouch.client import SoundTouch
from bose_soundtouch.enums import (
    ArtStatus,
    AudioMode,
    KeyState,
    KeyValue,
    PlayStatus,
    SourceStatus,
)
from bose_soundtouch.exceptions import (
    ApiError,
    ConnectionError,
    InvalidResponseError,
    SoundTouchError,
    TimeoutError,
    XmlParseError,
)
from bose_soundtouch.models import (
    Art,
    AudioDspControls,
    Bass,
    BassCapabilities,
    Capabilities,
    Capability,
    Component,
    ContentItem,
    DeviceInfo,
    LevelControls,
    NetworkInfo,
    NowPlaying,
    Preset,
    Presets,
    SourceItem,
    Sources,
    SpeakerLevel,
    ToneControl,
    ToneControls,
    Volume,
    Zone,
    ZoneMember,
)

__version__ = "0.1.0"

__all__ = [
    # Main client
    "SoundTouch",
    # Models
    "Art",
    "AudioDspControls",
    "Bass",
    "BassCapabilities",
    "Capabilities",
    "Capability",
    "Component",
    "ContentItem",
    "DeviceInfo",
    "LevelControls",
    "NetworkInfo",
    "NowPlaying",
    "Preset",
    "Presets",
    "SourceItem",
    "Sources",
    "SpeakerLevel",
    "ToneControl",
    "ToneControls",
    "Volume",
    "Zone",
    "ZoneMember",
    # Enums
    "ArtStatus",
    "AudioMode",
    "KeyState",
    "KeyValue",
    "PlayStatus",
    "SourceStatus",
    # Exceptions
    "ApiError",
    "ConnectionError",
    "InvalidResponseError",
    "SoundTouchError",
    "TimeoutError",
    "XmlParseError",
    # Version
    "__version__",
]
