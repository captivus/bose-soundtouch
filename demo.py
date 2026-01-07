"""
Demo script to test the bose-soundtouch library against a real device.

Usage:
    uv run python demo.py <speaker-ip>

Example:
    uv run python demo.py 192.168.1.100
"""

import argparse
import time

from bose_soundtouch import (
    SoundTouch,
    PlayStatus,
    SourceStatus,
    ConnectionError,
    TimeoutError,
    ApiError,
)


def separator(title: str) -> None:
    """Print a section separator."""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def wait_for_user(prompt: str = "Press Enter to continue...") -> None:
    """Wait for user input."""
    input(f"\n{prompt}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Demo script to test the bose-soundtouch library against a real device."
    )
    parser.add_argument(
        "host",
        help="IP address or hostname of the SoundTouch speaker",
    )
    args = parser.parse_args()

    print("Bose SoundTouch Library Demo")
    print(f"Target: {args.host}")

    try:
        with SoundTouch(host=args.host, timeout=10.0) as speaker:

            # ============ DEVICE INFO ============
            separator("1. Device Information")

            info = speaker.get_info()
            print(f"Name:      {info.name}")
            print(f"Type:      {info.type}")
            print(f"Device ID: {info.device_id}")

            if info.network_info:
                print("Network:")
                for net in info.network_info:
                    print(f"  {net.type}: {net.ip_address} ({net.mac_address})")

            if info.components:
                print("Components:")
                for comp in info.components:
                    print(f"  {comp.category}: v{comp.software_version}")

            # ============ CAPABILITIES ============
            separator("2. Device Capabilities")

            caps = speaker.get_capabilities()
            print(f"Capabilities ({len(caps.items)}):")
            for cap in caps.items:
                print(f"  - {cap.name}: {cap.url}")

            # ============ SOURCES ============
            separator("3. Available Sources")

            sources = speaker.get_sources()
            print(f"Sources ({len(sources.items)}):")
            for src in sources.items:
                status = "READY" if src.status == SourceStatus.READY else "UNAVAILABLE"
                name = src.display_name or src.source
                print(f"  - {name}: {status}")

            # ============ PRESETS ============
            separator("4. Presets")

            presets = speaker.get_presets()
            print("Presets (1-6):")
            for i in range(1, 7):
                preset = next((p for p in presets.items if p.id == i), None)
                if preset and preset.content_item:
                    print(f"  {i}: {preset.content_item.item_name} ({preset.content_item.source})")
                else:
                    print(f"  {i}: (empty)")

            # ============ VOLUME ============
            separator("5. Volume Status")

            volume = speaker.get_volume()
            print(f"Current volume: {volume.actual_volume}")
            print(f"Target volume:  {volume.target_volume}")
            print(f"Muted:          {volume.mute_enabled}")

            original_volume = volume.actual_volume

            # ============ BASS ============
            separator("6. Bass Capabilities")

            bass_caps = speaker.get_bass_capabilities()
            print(f"Bass available: {bass_caps.bass_available}")
            if bass_caps.bass_available:
                print(f"Bass range:     {bass_caps.bass_min} to {bass_caps.bass_max}")
                print(f"Bass default:   {bass_caps.bass_default}")

                bass = speaker.get_bass()
                print(f"Current bass:   {bass.actual_bass}")

            # ============ NOW PLAYING ============
            separator("7. Now Playing")

            now = speaker.get_now_playing()
            print(f"Source: {now.source}")
            print(f"Status: {now.play_status}")
            if now.track:
                print(f"Track:  {now.track}")
            if now.artist:
                print(f"Artist: {now.artist}")
            if now.album:
                print(f"Album:  {now.album}")
            if now.station_name:
                print(f"Station: {now.station_name}")

            # ============ VOLUME TEST ============
            separator("8. Volume Control Test")

            wait_for_user("Ready to test volume controls. Press Enter...")

            print(f"Current volume: {original_volume}")

            # Set to 20
            test_volume = 20
            print(f"Setting volume to {test_volume}...")
            speaker.set_volume(level=test_volume)
            time.sleep(0.5)

            vol = speaker.get_volume()
            print(f"Volume is now: {vol.actual_volume}")

            # Volume up
            print("Pressing volume up...")
            speaker.volume_up()
            time.sleep(0.5)

            vol = speaker.get_volume()
            print(f"Volume is now: {vol.actual_volume}")

            # Volume down
            print("Pressing volume down...")
            speaker.volume_down()
            time.sleep(0.5)

            vol = speaker.get_volume()
            print(f"Volume is now: {vol.actual_volume}")

            # Restore original
            print(f"Restoring volume to {original_volume}...")
            speaker.set_volume(level=original_volume)
            time.sleep(0.5)

            vol = speaker.get_volume()
            print(f"Volume restored to: {vol.actual_volume}")

            # ============ MUTE TEST ============
            separator("9. Mute Control Test")

            wait_for_user("Ready to test mute. Press Enter...")

            print("Muting...")
            speaker.mute()
            time.sleep(1)

            vol = speaker.get_volume()
            print(f"Muted: {vol.mute_enabled}")

            print("Unmuting...")
            speaker.unmute()
            time.sleep(0.5)

            vol = speaker.get_volume()
            print(f"Muted: {vol.mute_enabled}")

            # ============ PLAYBACK TEST ============
            separator("10. Playback Control Test")

            print()
            print("For this test, please start Spotify on your computer")
            print("and use Spotify Connect to play to the speaker.")
            print()
            wait_for_user("Press Enter once music is playing on the speaker...")

            # Check what's playing now
            now = speaker.get_now_playing()
            print(f"Now playing: {now.track} by {now.artist}")
            print(f"Status: {now.play_status}")

            if now.play_status == PlayStatus.PLAY_STATE:
                # Pause
                wait_for_user("Press Enter to PAUSE...")
                print("Pausing...")
                speaker.pause()
                time.sleep(1)

                now = speaker.get_now_playing()
                print(f"Status: {now.play_status}")

                # Resume
                wait_for_user("Press Enter to PLAY...")
                print("Playing...")
                speaker.play()
                time.sleep(1)

                now = speaker.get_now_playing()
                print(f"Status: {now.play_status}")

                # Next track
                wait_for_user("Press Enter for NEXT TRACK...")
                print("Skipping to next track...")
                speaker.next_track()
                time.sleep(2)

                now = speaker.get_now_playing()
                print(f"Now playing: {now.track} by {now.artist}")

                # Previous track
                wait_for_user("Press Enter for PREVIOUS TRACK...")
                print("Going to previous track...")
                speaker.previous_track()
                time.sleep(2)

                now = speaker.get_now_playing()
                print(f"Now playing: {now.track} by {now.artist}")

            else:
                print("No music playing - skipping playback controls test")

            # ============ DONE ============
            separator("Demo Complete!")

            print()
            print("All tests completed successfully.")
            print("The bose-soundtouch library is working correctly.")
            print()

    except ConnectionError as e:
        print(f"Connection failed: {e}")
        print("Make sure the speaker is on and reachable.")
    except TimeoutError as e:
        print(f"Request timed out: {e}")
    except ApiError as e:
        print(f"API error: {e}")
        if e.error_code:
            print(f"  Code: {e.error_code}")
        if e.error_name:
            print(f"  Name: {e.error_name}")


if __name__ == "__main__":
    main()
