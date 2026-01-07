"""Tests for bose_soundtouch.xml_parser module."""

import pytest

from bose_soundtouch import xml_parser
from bose_soundtouch.enums import (
    ArtStatus,
    AudioMode,
    PlayStatus,
    SourceStatus,
)
from bose_soundtouch.exceptions import ApiError, XmlParseError
from bose_soundtouch.models import ContentItem, ZoneMember


class TestParseXml:
    """Tests for parse_xml function."""

    def test_valid_xml(self) -> None:
        """Test parsing valid XML."""
        xml = "<root><child>text</child></root>"
        root = xml_parser.parse_xml(xml)
        assert root.tag == "root"
        assert root.find("child") is not None

    def test_invalid_xml(self) -> None:
        """Test parsing invalid XML raises XmlParseError."""
        xml = "<root><unclosed>"
        with pytest.raises(XmlParseError):
            xml_parser.parse_xml(xml)


class TestCheckForErrors:
    """Tests for check_for_errors function."""

    def test_no_error(self) -> None:
        """Test that non-error responses pass through."""
        xml = "<status>OK</status>"
        root = xml_parser.parse_xml(xml)
        # Should not raise
        xml_parser.check_for_errors(root)

    def test_error_response(self, error_xml: str) -> None:
        """Test that error responses raise ApiError."""
        root = xml_parser.parse_xml(error_xml)
        with pytest.raises(ApiError) as exc_info:
            xml_parser.check_for_errors(root)
        assert exc_info.value.error_code == 1019
        assert exc_info.value.error_name == "CLIENT_XML_ERROR"

    def test_simple_error(self) -> None:
        """Test simple error format."""
        xml = "<error>Something went wrong</error>"
        root = xml_parser.parse_xml(xml)
        with pytest.raises(ApiError) as exc_info:
            xml_parser.check_for_errors(root)
        assert "Something went wrong" in str(exc_info.value)


class TestParseDeviceInfo:
    """Tests for parse_device_info function."""

    def test_parse_info(self, info_xml: str) -> None:
        """Test parsing /info response."""
        root = xml_parser.parse_xml(info_xml)
        info = xml_parser.parse_device_info(root)

        assert info.device_id == "AABBCCDDEEFF"
        assert info.name == "Living Room"
        assert info.type == "SoundTouch 10"
        assert info.account_uuid == "abc123"
        assert len(info.components) == 1
        assert info.components[0].category == "SCM"
        assert len(info.network_info) == 1
        assert info.network_info[0].type == "WIFI"


class TestParseNowPlaying:
    """Tests for parse_now_playing function."""

    def test_parse_now_playing(self, now_playing_xml: str) -> None:
        """Test parsing /now_playing response."""
        root = xml_parser.parse_xml(now_playing_xml)
        now = xml_parser.parse_now_playing(root)

        assert now.device_id == "AABBCCDDEEFF"
        assert now.source == "SPOTIFY"
        assert now.track == "Test Track"
        assert now.artist == "Test Artist"
        assert now.album == "Test Album"
        assert now.play_status == PlayStatus.PLAY_STATE
        assert now.art is not None
        assert now.art.status == ArtStatus.IMAGE_PRESENT
        assert now.content_item is not None
        assert now.content_item.is_presetable is True


class TestParseSources:
    """Tests for parse_sources function."""

    def test_parse_sources(self, sources_xml: str) -> None:
        """Test parsing /sources response."""
        root = xml_parser.parse_xml(sources_xml)
        sources = xml_parser.parse_sources(root)

        assert sources.device_id == "AABBCCDDEEFF"
        assert len(sources.items) == 3
        assert sources.items[0].source == "AUX"
        assert sources.items[0].status == SourceStatus.READY
        assert sources.items[2].status == SourceStatus.UNAVAILABLE


class TestParseVolume:
    """Tests for parse_volume function."""

    def test_parse_volume(self, volume_xml: str) -> None:
        """Test parsing /volume response."""
        root = xml_parser.parse_xml(volume_xml)
        volume = xml_parser.parse_volume(root)

        assert volume.device_id == "AABBCCDDEEFF"
        assert volume.target_volume == 50
        assert volume.actual_volume == 50
        assert volume.mute_enabled is False


class TestParseBass:
    """Tests for parse_bass function."""

    def test_parse_bass(self, bass_xml: str) -> None:
        """Test parsing /bass response."""
        root = xml_parser.parse_xml(bass_xml)
        bass = xml_parser.parse_bass(root)

        assert bass.device_id == "AABBCCDDEEFF"
        assert bass.target_bass == 0
        assert bass.actual_bass == 0


class TestParseBassCapabilities:
    """Tests for parse_bass_capabilities function."""

    def test_parse_bass_capabilities(self, bass_capabilities_xml: str) -> None:
        """Test parsing /bassCapabilities response."""
        root = xml_parser.parse_xml(bass_capabilities_xml)
        caps = xml_parser.parse_bass_capabilities(root)

        assert caps.device_id == "AABBCCDDEEFF"
        assert caps.bass_available is True
        assert caps.bass_min == -9
        assert caps.bass_max == 9
        assert caps.bass_default == 0


class TestParsePresets:
    """Tests for parse_presets function."""

    def test_parse_presets(self, presets_xml: str) -> None:
        """Test parsing /presets response."""
        root = xml_parser.parse_xml(presets_xml)
        presets = xml_parser.parse_presets(root)

        assert len(presets.items) == 2
        assert presets.items[0].id == 1
        assert presets.items[0].content_item is not None
        assert presets.items[0].content_item.item_name == "NPR News"
        assert presets.items[0].created_on == 1234567890


class TestParseZone:
    """Tests for parse_zone function."""

    def test_parse_zone(self, zone_xml: str) -> None:
        """Test parsing /getZone response."""
        root = xml_parser.parse_xml(zone_xml)
        zone = xml_parser.parse_zone(root)

        assert zone.master_mac == "AABBCCDDEEFF"
        assert len(zone.members) == 2
        assert zone.members[0].ip_address == "192.168.1.100"


class TestParseCapabilities:
    """Tests for parse_capabilities function."""

    def test_parse_capabilities(self, capabilities_xml: str) -> None:
        """Test parsing /capabilities response."""
        root = xml_parser.parse_xml(capabilities_xml)
        caps = xml_parser.parse_capabilities(root)

        assert caps.device_id == "AABBCCDDEEFF"
        assert len(caps.items) == 2
        assert caps.items[0].name == "audiodspcontrols"
        assert caps.items[0].url == "/audiodspcontrols"


class TestParseAudioDspControls:
    """Tests for parse_audio_dsp_controls function."""

    def test_parse_audio_dsp_controls(self, audio_dsp_controls_xml: str) -> None:
        """Test parsing /audiodspcontrols response."""
        root = xml_parser.parse_xml(audio_dsp_controls_xml)
        controls = xml_parser.parse_audio_dsp_controls(root)

        assert controls.audio_mode == AudioMode.NORMAL
        assert controls.video_sync_audio_delay == 0
        assert len(controls.supported_audio_modes) == 3
        assert AudioMode.DIALOG in controls.supported_audio_modes


class TestParseToneControls:
    """Tests for parse_tone_controls function."""

    def test_parse_tone_controls(self, tone_controls_xml: str) -> None:
        """Test parsing /audioproducttonecontrols response."""
        root = xml_parser.parse_xml(tone_controls_xml)
        controls = xml_parser.parse_tone_controls(root)

        assert controls.bass is not None
        assert controls.bass.value == 0
        assert controls.bass.min_value == -10
        assert controls.bass.max_value == 10
        assert controls.treble is not None


class TestParseLevelControls:
    """Tests for parse_level_controls function."""

    def test_parse_level_controls(self, level_controls_xml: str) -> None:
        """Test parsing /audioproductlevelcontrols response."""
        root = xml_parser.parse_xml(level_controls_xml)
        controls = xml_parser.parse_level_controls(root)

        assert controls.front_center is not None
        assert controls.front_center.value == 0
        assert controls.rear_surround is not None


# ============ XML Builder Tests ============


class TestBuildKeyXml:
    """Tests for build_key_xml function."""

    def test_build_key_xml(self) -> None:
        """Test building /key XML."""
        xml = xml_parser.build_key_xml(
            key="PLAY",
            state="press",
            sender="test",
        )
        assert 'state="press"' in xml
        assert 'sender="test"' in xml
        assert "PLAY" in xml


class TestBuildVolumeXml:
    """Tests for build_volume_xml function."""

    def test_build_volume_only(self) -> None:
        """Test building /volume XML with volume only."""
        xml = xml_parser.build_volume_xml(volume=50, mute=None)
        assert "<volume>50</volume>" in xml

    def test_build_mute_only(self) -> None:
        """Test building /volume XML with mute only."""
        xml = xml_parser.build_volume_xml(volume=None, mute=True)
        assert "<muteenabled>true</muteenabled>" in xml

    def test_build_volume_and_mute(self) -> None:
        """Test building /volume XML with both."""
        xml = xml_parser.build_volume_xml(volume=50, mute=False)
        assert "50" in xml
        assert "<muteenabled>false</muteenabled>" in xml


class TestBuildBassXml:
    """Tests for build_bass_xml function."""

    def test_build_bass_xml(self) -> None:
        """Test building /bass XML."""
        xml = xml_parser.build_bass_xml(bass=5)
        assert "<bass>5</bass>" in xml
        assert xml.startswith("<?xml")


class TestBuildNameXml:
    """Tests for build_name_xml function."""

    def test_build_name_xml(self) -> None:
        """Test building /name XML."""
        xml = xml_parser.build_name_xml(name="Living Room")
        assert "<name>Living Room</name>" in xml
        assert xml.startswith("<?xml")

    def test_build_name_xml_escapes(self) -> None:
        """Test that special characters are escaped."""
        xml = xml_parser.build_name_xml(name="Room <1>")
        assert "&lt;" in xml
        assert "&gt;" in xml


class TestBuildSelectXml:
    """Tests for build_select_xml function."""

    def test_build_select_xml_minimal(self) -> None:
        """Test building /select XML with minimal content."""
        content = ContentItem(source="AUX")
        xml = xml_parser.build_select_xml(content_item=content)
        assert 'source="AUX"' in xml
        assert "<ContentItem" in xml

    def test_build_select_xml_full(self) -> None:
        """Test building /select XML with full content."""
        content = ContentItem(
            source="SPOTIFY",
            source_account="user@example.com",
            location="playlist:123",
            item_name="My Playlist",
        )
        xml = xml_parser.build_select_xml(content_item=content)
        assert 'source="SPOTIFY"' in xml
        assert 'sourceAccount="user@example.com"' in xml
        assert "<itemName>My Playlist</itemName>" in xml


class TestBuildZoneXml:
    """Tests for build_zone_xml function."""

    def test_build_zone_xml(self) -> None:
        """Test building /setZone XML."""
        members = [
            ZoneMember(mac_address="AABBCCDDEEFF", ip_address="192.168.1.100"),
        ]
        xml = xml_parser.build_zone_xml(
            master_mac="AABBCCDDEEFF",
            members=members,
            sender_ip="192.168.1.1",
        )
        assert 'master="AABBCCDDEEFF"' in xml
        assert 'senderIPAddress="192.168.1.1"' in xml
        assert "<member" in xml


class TestBuildZoneMemberXml:
    """Tests for build_zone_member_xml function."""

    def test_build_zone_member_xml(self) -> None:
        """Test building /addZoneSlave or /removeZoneSlave XML."""
        members = [
            ZoneMember(mac_address="112233445566", ip_address="192.168.1.101"),
        ]
        xml = xml_parser.build_zone_member_xml(
            master_mac="AABBCCDDEEFF",
            members=members,
        )
        assert 'master="AABBCCDDEEFF"' in xml
        assert "112233445566" in xml


class TestBuildAudioDspXml:
    """Tests for build_audio_dsp_xml function."""

    def test_build_audio_mode_only(self) -> None:
        """Test building with audio mode only."""
        xml = xml_parser.build_audio_dsp_xml(
            audio_mode=AudioMode.DIALOG,
            delay=None,
        )
        assert 'audiomode="AUDIO_MODE_DIALOG"' in xml

    def test_build_delay_only(self) -> None:
        """Test building with delay only."""
        xml = xml_parser.build_audio_dsp_xml(
            audio_mode=None,
            delay=100,
        )
        assert 'videosyncaudiodelay="100"' in xml


class TestBuildToneControlsXml:
    """Tests for build_tone_controls_xml function."""

    def test_build_bass_only(self) -> None:
        """Test building with bass only."""
        xml = xml_parser.build_tone_controls_xml(bass=5, treble=None)
        assert '<bass value="5"' in xml
        assert "treble" not in xml

    def test_build_both(self) -> None:
        """Test building with both bass and treble."""
        xml = xml_parser.build_tone_controls_xml(bass=5, treble=-3)
        assert '<bass value="5"' in xml
        assert '<treble value="-3"' in xml


class TestBuildLevelControlsXml:
    """Tests for build_level_controls_xml function."""

    def test_build_front_center_only(self) -> None:
        """Test building with front center only."""
        xml = xml_parser.build_level_controls_xml(front_center=5, rear_surround=None)
        assert '<frontCenterSpeakerLevel value="5"' in xml
        assert "rearSurroundSpeakersLevel" not in xml

    def test_build_both(self) -> None:
        """Test building with both levels."""
        xml = xml_parser.build_level_controls_xml(front_center=5, rear_surround=-3)
        assert '<frontCenterSpeakerLevel value="5"' in xml
        assert '<rearSurroundSpeakersLevel value="-3"' in xml
