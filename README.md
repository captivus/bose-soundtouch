# bose-soundtouch

A Python library for controlling Bose SoundTouch speakers via the local REST API.

## Background

On January 7, 2026, Bose announced that cloud support for SoundTouch products will end on May 6, 2026. After this date:

**What will continue to work:**
- Streaming via Bluetooth, AirPlay, Spotify Connect, and AUX
- Setting up and configuring your system
- Remote control features (play, pause, skip, volume)
- Grouping multiple speakers together

**What will stop working:**
- Presets (preset buttons and app presets)
- Browsing music services from the SoundTouch app

As part of this transition, Bose released their [SoundTouch API Documentation](https://assets.bosecreative.com/m/496577402d128874/original/SoundTouch-Web-API.pdf) to enable independent developers to create their own SoundTouch-compatible tools.

This library provides a clean, Pythonic interface to control SoundTouch speakers over your local network, ensuring your speakers remain fully functional even after cloud services end.

## Installation

```bash
pip install bose-soundtouch
```

## Quick Start

```python
from bose_soundtouch import SoundTouch

# Connect to a speaker by IP address
with SoundTouch(host="192.168.1.100") as speaker:
    # Get device info
    info = speaker.get_info()
    print(f"Connected to: {info.name} ({info.type})")

    # Control playback
    speaker.play()
    speaker.set_volume(level=30)

    # Check what's playing
    now_playing = speaker.get_now_playing()
    print(f"Playing: {now_playing.track} by {now_playing.artist}")
```

## Demo Script

A comprehensive demo script is included to test the library against a real device:

```bash
uv run python demo.py 192.168.1.100
```

The demo walks through device info, capabilities, sources, presets, volume control, mute, and playback controls.

## Features

- Control playback (play, pause, stop, next/previous track)
- Adjust volume and mute
- Select presets (1-6)
- Select sources (AUX, Bluetooth, etc.)
- Get now playing information
- Control bass and tone settings
- Multi-room zone management
- Full type hints and dataclass models

## Usage Examples

### Playback Control

```python
from bose_soundtouch import SoundTouch

with SoundTouch(host="192.168.1.100") as speaker:
    speaker.play()
    speaker.pause()
    speaker.play_pause()  # Toggle
    speaker.stop()
    speaker.next_track()
    speaker.previous_track()
```

### Volume Control

```python
from bose_soundtouch import SoundTouch

with SoundTouch(host="192.168.1.100") as speaker:
    # Get current volume
    volume = speaker.get_volume()
    print(f"Volume: {volume.actual_volume}, Muted: {volume.mute_enabled}")

    # Set volume (0-100)
    speaker.set_volume(level=50)

    # Mute/unmute
    speaker.mute()
    speaker.unmute()

    # Volume up/down buttons
    speaker.volume_up()
    speaker.volume_down()
```

### Presets

```python
from bose_soundtouch import SoundTouch

with SoundTouch(host="192.168.1.100") as speaker:
    # Get all presets
    presets = speaker.get_presets()
    for preset in presets.items:
        if preset.content_item:
            print(f"Preset {preset.id}: {preset.content_item.item_name}")

    # Select a preset
    speaker.select_preset(preset_id=1)
```

### Now Playing

```python
from bose_soundtouch import SoundTouch, PlayStatus

with SoundTouch(host="192.168.1.100") as speaker:
    now = speaker.get_now_playing()

    print(f"Source: {now.source}")
    print(f"Track: {now.track}")
    print(f"Artist: {now.artist}")
    print(f"Album: {now.album}")

    if now.play_status == PlayStatus.PLAY_STATE:
        print("Currently playing")
    elif now.play_status == PlayStatus.PAUSE_STATE:
        print("Paused")
```

### Source Selection

```python
from bose_soundtouch import SoundTouch

with SoundTouch(host="192.168.1.100") as speaker:
    # List available sources
    sources = speaker.get_sources()
    for source in sources.items:
        print(f"{source.source}: {source.status}")

    # Select a source
    speaker.select_source(source="AUX", source_account="AUX")
    speaker.select_source(source="BLUETOOTH")
```

### Device Information

```python
from bose_soundtouch import SoundTouch

with SoundTouch(host="192.168.1.100") as speaker:
    info = speaker.get_info()

    print(f"Name: {info.name}")
    print(f"Type: {info.type}")
    print(f"Device ID: {info.device_id}")

    for net in info.network_info:
        print(f"  {net.type}: {net.ip_address}")
```

### Raw Key Press

For advanced use cases, you can send raw key presses:

```python
from bose_soundtouch import SoundTouch, KeyValue

with SoundTouch(host="192.168.1.100") as speaker:
    # Using enum
    speaker.send_key(key=KeyValue.THUMBS_UP)

    # Using string
    speaker.send_key(key="POWER")
```

### Error Handling

```python
from bose_soundtouch import (
    SoundTouch,
    ConnectionError,
    TimeoutError,
    ApiError,
)

try:
    with SoundTouch(host="192.168.1.100", timeout=5.0) as speaker:
        speaker.set_volume(level=50)
except ConnectionError:
    print("Could not connect to speaker")
except TimeoutError:
    print("Request timed out")
except ApiError as e:
    print(f"API error: {e.error_name} (code {e.error_code})")
```

## API Reference

### SoundTouch Class

```python
SoundTouch(
    host: str,           # IP address or hostname
    port: int = 8090,    # HTTP port (default 8090)
    timeout: float = 10.0  # Request timeout in seconds
)
```

### Methods

| Method | Description |
|--------|-------------|
| `get_info()` | Get device information |
| `get_capabilities()` | Get device capabilities |
| `set_name(name=...)` | Set device name |
| `get_now_playing()` | Get current playback state |
| `get_sources()` | Get available sources |
| `select_source(source=..., ...)` | Select a source |
| `get_volume()` | Get volume state |
| `set_volume(level=...)` | Set volume (0-100) |
| `mute()` / `unmute()` | Mute/unmute |
| `get_presets()` | Get preset slots |
| `select_preset(preset_id=...)` | Select preset (1-6) |
| `play()` / `pause()` / `stop()` | Playback control |
| `next_track()` / `previous_track()` | Track navigation |
| `get_bass()` / `set_bass(level=...)` | Bass control |
| `send_key(key=...)` | Send raw key press |

## Documentation

The `docs/` directory contains API documentation:

- **[SoundTouch Web API (PDF)](docs/2025.12.18%20SoundTouch%20Web%20API.pdf)** - Official API documentation released by Bose
- **[SoundTouch Web API (Markdown)](docs/soundtouch-web-api.md)** - Markdown version of the API documentation

## Requirements

- Python 3.12+
- httpx

## License

MIT License

---

Not affiliated with, endorsed, sponsored, or approved by Bose. Bose and SoundTouch are trademarks of Bose Corporation.
