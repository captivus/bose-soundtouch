"""Tests for bose_soundtouch.models module."""

import pytest

from bose_soundtouch.enums import ArtStatus, PlayStatus, SourceStatus
from bose_soundtouch.models import (
    Art,
    Bass,
    BassCapabilities,
    Component,
    ContentItem,
    DeviceInfo,
    NetworkInfo,
    NowPlaying,
    Preset,
    Presets,
    SourceItem,
    Sources,
    Volume,
    Zone,
    ZoneMember,
)


class TestNetworkInfo:
    """Tests for NetworkInfo dataclass."""

    def test_creation(self) -> None:
        """Test creating a NetworkInfo instance."""
        info = NetworkInfo(
            type="WIFI",
            mac_address="AABBCCDDEEFF",
            ip_address="192.168.1.100",
        )
        assert info.type == "WIFI"
        assert info.mac_address == "AABBCCDDEEFF"
        assert info.ip_address == "192.168.1.100"

    def test_frozen(self) -> None:
        """Test that NetworkInfo is immutable."""
        info = NetworkInfo(
            type="WIFI",
            mac_address="AABBCCDDEEFF",
            ip_address="192.168.1.100",
        )
        with pytest.raises(AttributeError):
            info.type = "ETHERNET"  # type: ignore


class TestComponent:
    """Tests for Component dataclass."""

    def test_creation_with_serial(self) -> None:
        """Test creating a Component with serial number."""
        comp = Component(
            category="SCM",
            software_version="1.0.0",
            serial_number="SN123",
        )
        assert comp.category == "SCM"
        assert comp.software_version == "1.0.0"
        assert comp.serial_number == "SN123"

    def test_creation_without_serial(self) -> None:
        """Test creating a Component without serial number."""
        comp = Component(
            category="SCM",
            software_version="1.0.0",
        )
        assert comp.serial_number is None


class TestDeviceInfo:
    """Tests for DeviceInfo dataclass."""

    def test_creation(self) -> None:
        """Test creating a DeviceInfo instance."""
        info = DeviceInfo(
            device_id="AABBCCDDEEFF",
            name="Living Room",
            type="SoundTouch 10",
        )
        assert info.device_id == "AABBCCDDEEFF"
        assert info.name == "Living Room"
        assert info.type == "SoundTouch 10"
        assert info.components == []
        assert info.network_info == []

    def test_with_components(self) -> None:
        """Test DeviceInfo with components."""
        comp = Component(category="SCM", software_version="1.0.0")
        info = DeviceInfo(
            device_id="AABBCCDDEEFF",
            name="Living Room",
            type="SoundTouch 10",
            components=[comp],
        )
        assert len(info.components) == 1
        assert info.components[0].category == "SCM"


class TestContentItem:
    """Tests for ContentItem dataclass."""

    def test_minimal_creation(self) -> None:
        """Test creating a minimal ContentItem."""
        item = ContentItem(source="AUX")
        assert item.source == "AUX"
        assert item.location is None
        assert item.source_account is None
        assert item.is_presetable is False
        assert item.item_name is None

    def test_full_creation(self) -> None:
        """Test creating a full ContentItem."""
        item = ContentItem(
            source="SPOTIFY",
            location="playlist:123",
            source_account="user@example.com",
            is_presetable=True,
            item_name="My Playlist",
        )
        assert item.source == "SPOTIFY"
        assert item.location == "playlist:123"
        assert item.source_account == "user@example.com"
        assert item.is_presetable is True
        assert item.item_name == "My Playlist"


class TestArt:
    """Tests for Art dataclass."""

    def test_default_status(self) -> None:
        """Test Art with default status."""
        art = Art()
        assert art.url is None
        assert art.status == ArtStatus.INVALID

    def test_with_url_and_status(self) -> None:
        """Test Art with URL and status."""
        art = Art(
            url="https://example.com/art.jpg",
            status=ArtStatus.IMAGE_PRESENT,
        )
        assert art.url == "https://example.com/art.jpg"
        assert art.status == ArtStatus.IMAGE_PRESENT


class TestNowPlaying:
    """Tests for NowPlaying dataclass."""

    def test_minimal_creation(self) -> None:
        """Test creating a minimal NowPlaying."""
        now = NowPlaying(
            device_id="AABBCCDDEEFF",
            source="SPOTIFY",
        )
        assert now.device_id == "AABBCCDDEEFF"
        assert now.source == "SPOTIFY"
        assert now.play_status == PlayStatus.INVALID_PLAY_STATUS

    def test_full_creation(self) -> None:
        """Test creating a full NowPlaying."""
        art = Art(url="https://example.com/art.jpg", status=ArtStatus.IMAGE_PRESENT)
        content = ContentItem(source="SPOTIFY", item_name="My Playlist")
        now = NowPlaying(
            device_id="AABBCCDDEEFF",
            source="SPOTIFY",
            content_item=content,
            track="Test Track",
            artist="Test Artist",
            album="Test Album",
            art=art,
            play_status=PlayStatus.PLAY_STATE,
        )
        assert now.track == "Test Track"
        assert now.artist == "Test Artist"
        assert now.album == "Test Album"
        assert now.play_status == PlayStatus.PLAY_STATE


class TestSourceItem:
    """Tests for SourceItem dataclass."""

    def test_creation(self) -> None:
        """Test creating a SourceItem."""
        item = SourceItem(
            source="AUX",
            source_account="AUX",
            status=SourceStatus.READY,
            display_name="AUX Input",
        )
        assert item.source == "AUX"
        assert item.status == SourceStatus.READY


class TestVolume:
    """Tests for Volume dataclass."""

    def test_creation(self) -> None:
        """Test creating a Volume."""
        vol = Volume(
            device_id="AABBCCDDEEFF",
            target_volume=50,
            actual_volume=50,
            mute_enabled=False,
        )
        assert vol.target_volume == 50
        assert vol.actual_volume == 50
        assert vol.mute_enabled is False


class TestBass:
    """Tests for Bass dataclass."""

    def test_creation(self) -> None:
        """Test creating a Bass."""
        bass = Bass(
            device_id="AABBCCDDEEFF",
            target_bass=0,
            actual_bass=0,
        )
        assert bass.target_bass == 0
        assert bass.actual_bass == 0


class TestBassCapabilities:
    """Tests for BassCapabilities dataclass."""

    def test_creation(self) -> None:
        """Test creating a BassCapabilities."""
        caps = BassCapabilities(
            device_id="AABBCCDDEEFF",
            bass_available=True,
            bass_min=-9,
            bass_max=9,
            bass_default=0,
        )
        assert caps.bass_available is True
        assert caps.bass_min == -9
        assert caps.bass_max == 9


class TestPreset:
    """Tests for Preset dataclass."""

    def test_empty_preset(self) -> None:
        """Test creating an empty preset."""
        preset = Preset(id=1)
        assert preset.id == 1
        assert preset.content_item is None

    def test_preset_with_content(self) -> None:
        """Test creating a preset with content."""
        content = ContentItem(source="TUNEIN", item_name="NPR")
        preset = Preset(
            id=1,
            content_item=content,
            created_on=1234567890,
            updated_on=1234567890,
        )
        assert preset.content_item is not None
        assert preset.content_item.item_name == "NPR"


class TestZoneMember:
    """Tests for ZoneMember dataclass."""

    def test_creation(self) -> None:
        """Test creating a ZoneMember."""
        member = ZoneMember(
            mac_address="AABBCCDDEEFF",
            ip_address="192.168.1.100",
        )
        assert member.mac_address == "AABBCCDDEEFF"
        assert member.ip_address == "192.168.1.100"


class TestZone:
    """Tests for Zone dataclass."""

    def test_empty_zone(self) -> None:
        """Test creating an empty zone."""
        zone = Zone()
        assert zone.master_mac is None
        assert zone.members == []

    def test_zone_with_members(self) -> None:
        """Test creating a zone with members."""
        members = [
            ZoneMember(mac_address="AABBCCDDEEFF", ip_address="192.168.1.100"),
            ZoneMember(mac_address="112233445566", ip_address="192.168.1.101"),
        ]
        zone = Zone(master_mac="AABBCCDDEEFF", members=members)
        assert zone.master_mac == "AABBCCDDEEFF"
        assert len(zone.members) == 2
