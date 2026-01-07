"""Tests for bose_soundtouch.client module."""

from unittest.mock import MagicMock, patch

import pytest

from bose_soundtouch import SoundTouch
from bose_soundtouch.enums import AudioMode, KeyValue, PlayStatus
from bose_soundtouch.exceptions import ConnectionError, TimeoutError
from bose_soundtouch.models import ZoneMember


class TestSoundTouchInit:
    """Tests for SoundTouch initialization."""

    def test_init_with_host(self) -> None:
        """Test initializing with just a host."""
        speaker = SoundTouch(host="192.168.1.100")
        assert speaker.host == "192.168.1.100"
        assert speaker.port == 8090
        speaker.close()

    def test_init_with_custom_port(self) -> None:
        """Test initializing with a custom port."""
        speaker = SoundTouch(host="192.168.1.100", port=9090)
        assert speaker.port == 9090
        speaker.close()

    def test_init_with_custom_timeout(self) -> None:
        """Test initializing with a custom timeout."""
        speaker = SoundTouch(host="192.168.1.100", timeout=5.0)
        speaker.close()

    def test_context_manager(self) -> None:
        """Test using as context manager."""
        with SoundTouch(host="192.168.1.100") as speaker:
            assert speaker.host == "192.168.1.100"

    def test_repr(self) -> None:
        """Test string representation."""
        speaker = SoundTouch(host="192.168.1.100")
        assert "192.168.1.100" in repr(speaker)
        speaker.close()


class TestSoundTouchGetMethods:
    """Tests for SoundTouch GET methods."""

    @patch.object(SoundTouch, "_get")
    def test_get_info(self, mock_get: MagicMock, info_xml: str) -> None:
        """Test get_info method."""
        mock_get.return_value = info_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            info = speaker.get_info()
            assert info.name == "Living Room"
            assert info.device_id == "AABBCCDDEEFF"
            mock_get.assert_called_once_with("/info")

    @patch.object(SoundTouch, "_get")
    def test_get_now_playing(self, mock_get: MagicMock, now_playing_xml: str) -> None:
        """Test get_now_playing method."""
        mock_get.return_value = now_playing_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            now = speaker.get_now_playing()
            assert now.track == "Test Track"
            assert now.play_status == PlayStatus.PLAY_STATE
            mock_get.assert_called_once_with("/now_playing")

    @patch.object(SoundTouch, "_get")
    def test_get_sources(self, mock_get: MagicMock, sources_xml: str) -> None:
        """Test get_sources method."""
        mock_get.return_value = sources_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            sources = speaker.get_sources()
            assert len(sources.items) == 3
            mock_get.assert_called_once_with("/sources")

    @patch.object(SoundTouch, "_get")
    def test_get_volume(self, mock_get: MagicMock, volume_xml: str) -> None:
        """Test get_volume method."""
        mock_get.return_value = volume_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            volume = speaker.get_volume()
            assert volume.actual_volume == 50
            assert volume.mute_enabled is False
            mock_get.assert_called_once_with("/volume")

    @patch.object(SoundTouch, "_get")
    def test_get_bass(self, mock_get: MagicMock, bass_xml: str) -> None:
        """Test get_bass method."""
        mock_get.return_value = bass_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            bass = speaker.get_bass()
            assert bass.actual_bass == 0
            mock_get.assert_called_once_with("/bass")

    @patch.object(SoundTouch, "_get")
    def test_get_presets(self, mock_get: MagicMock, presets_xml: str) -> None:
        """Test get_presets method."""
        mock_get.return_value = presets_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            presets = speaker.get_presets()
            assert len(presets.items) == 2
            mock_get.assert_called_once_with("/presets")

    @patch.object(SoundTouch, "_get")
    def test_get_zone(self, mock_get: MagicMock, zone_xml: str) -> None:
        """Test get_zone method."""
        mock_get.return_value = zone_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            zone = speaker.get_zone()
            assert zone.master_mac == "AABBCCDDEEFF"
            mock_get.assert_called_once_with("/getZone")

    @patch.object(SoundTouch, "_get")
    def test_get_capabilities(self, mock_get: MagicMock, capabilities_xml: str) -> None:
        """Test get_capabilities method."""
        mock_get.return_value = capabilities_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            caps = speaker.get_capabilities()
            assert len(caps.items) == 2
            mock_get.assert_called_once_with("/capabilities")


class TestSoundTouchPostMethods:
    """Tests for SoundTouch POST methods."""

    @patch.object(SoundTouch, "_post")
    def test_set_volume(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test set_volume method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.set_volume(level=50)
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "/volume"
            assert "50" in call_args[0][1]

    @patch.object(SoundTouch, "_post")
    def test_mute(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test mute method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.mute()
            call_args = mock_post.call_args
            assert "<muteenabled>true</muteenabled>" in call_args[0][1]

    @patch.object(SoundTouch, "_post")
    def test_unmute(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test unmute method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.unmute()
            call_args = mock_post.call_args
            assert "<muteenabled>false</muteenabled>" in call_args[0][1]

    @patch.object(SoundTouch, "_post")
    def test_set_bass(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test set_bass method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.set_bass(level=5)
            call_args = mock_post.call_args
            assert call_args[0][0] == "/bass"
            assert "<bass>5</bass>" in call_args[0][1]

    @patch.object(SoundTouch, "_post")
    def test_set_name(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test set_name method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.set_name(name="Bedroom")
            call_args = mock_post.call_args
            assert call_args[0][0] == "/name"
            assert "<name>Bedroom</name>" in call_args[0][1]


class TestSoundTouchKeyMethods:
    """Tests for SoundTouch key press methods."""

    @patch.object(SoundTouch, "_post")
    def test_send_key(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test send_key method sends press and release."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.send_key(key=KeyValue.PLAY)
            # Should be called twice (press and release)
            assert mock_post.call_count == 2

    @patch.object(SoundTouch, "_post")
    def test_send_key_with_string(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test send_key method with string key."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.send_key(key="PLAY")
            assert mock_post.call_count == 2

    @patch.object(SoundTouch, "_post")
    def test_play(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test play convenience method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.play()
            assert mock_post.call_count == 2
            # Check that PLAY key was sent
            calls = mock_post.call_args_list
            assert "PLAY" in calls[0][0][1]

    @patch.object(SoundTouch, "_post")
    def test_pause(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test pause convenience method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.pause()
            calls = mock_post.call_args_list
            assert "PAUSE" in calls[0][0][1]

    @patch.object(SoundTouch, "_post")
    def test_select_preset(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test select_preset method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.select_preset(preset_id=3)
            calls = mock_post.call_args_list
            assert "PRESET_3" in calls[0][0][1]

    def test_select_preset_invalid_id(self) -> None:
        """Test select_preset with invalid preset ID."""
        with SoundTouch(host="192.168.1.100") as speaker:
            with pytest.raises(ValueError):
                speaker.select_preset(preset_id=0)
            with pytest.raises(ValueError):
                speaker.select_preset(preset_id=7)


class TestSoundTouchSourceMethods:
    """Tests for SoundTouch source selection methods."""

    @patch.object(SoundTouch, "_post")
    def test_select_source(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test select_source method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.select_source(source="AUX", source_account="AUX")
            call_args = mock_post.call_args
            assert call_args[0][0] == "/select"
            assert 'source="AUX"' in call_args[0][1]


class TestSoundTouchZoneMethods:
    """Tests for SoundTouch zone methods."""

    @patch.object(SoundTouch, "_post")
    def test_set_zone(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test set_zone method."""
        mock_post.return_value = status_xml
        members = [ZoneMember(mac_address="112233445566", ip_address="192.168.1.101")]
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.set_zone(master_mac="AABBCCDDEEFF", members=members)
            call_args = mock_post.call_args
            assert call_args[0][0] == "/setZone"

    @patch.object(SoundTouch, "_post")
    def test_add_zone_slave(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test add_zone_slave method."""
        mock_post.return_value = status_xml
        members = [ZoneMember(mac_address="112233445566", ip_address="192.168.1.101")]
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.add_zone_slave(master_mac="AABBCCDDEEFF", members=members)
            call_args = mock_post.call_args
            assert call_args[0][0] == "/addZoneSlave"


class TestSoundTouchAudioMethods:
    """Tests for SoundTouch audio DSP and tone methods."""

    @patch.object(SoundTouch, "_get")
    def test_get_audio_dsp_controls(
        self, mock_get: MagicMock, audio_dsp_controls_xml: str
    ) -> None:
        """Test get_audio_dsp_controls method."""
        mock_get.return_value = audio_dsp_controls_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            controls = speaker.get_audio_dsp_controls()
            assert controls.audio_mode == AudioMode.NORMAL
            mock_get.assert_called_once_with("/audiodspcontrols")

    @patch.object(SoundTouch, "_post")
    def test_set_audio_mode(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test set_audio_mode method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.set_audio_mode(mode=AudioMode.DIALOG)
            call_args = mock_post.call_args
            assert "AUDIO_MODE_DIALOG" in call_args[0][1]

    @patch.object(SoundTouch, "_get")
    def test_get_tone_controls(
        self, mock_get: MagicMock, tone_controls_xml: str
    ) -> None:
        """Test get_tone_controls method."""
        mock_get.return_value = tone_controls_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            controls = speaker.get_tone_controls()
            assert controls.bass is not None
            assert controls.bass.value == 0
            mock_get.assert_called_once_with("/audioproducttonecontrols")

    @patch.object(SoundTouch, "_post")
    def test_set_tone_controls(self, mock_post: MagicMock, status_xml: str) -> None:
        """Test set_tone_controls method."""
        mock_post.return_value = status_xml
        with SoundTouch(host="192.168.1.100") as speaker:
            speaker.set_tone_controls(bass=5, treble=-3)
            call_args = mock_post.call_args
            assert '<bass value="5"' in call_args[0][1]
            assert '<treble value="-3"' in call_args[0][1]


class TestSoundTouchErrorHandling:
    """Tests for SoundTouch error handling."""

    @patch.object(SoundTouch, "_get")
    def test_connection_error(self, mock_get: MagicMock) -> None:
        """Test that connection errors are raised properly."""
        import httpx

        mock_get.side_effect = httpx.ConnectError("Connection refused")
        with SoundTouch(host="192.168.1.100") as speaker:
            with pytest.raises((ConnectionError, httpx.ConnectError)):
                speaker.get_info()

    @patch.object(SoundTouch, "_get")
    def test_timeout_error(self, mock_get: MagicMock) -> None:
        """Test that timeout errors are raised properly."""
        import httpx

        mock_get.side_effect = httpx.TimeoutException("Request timed out")
        with SoundTouch(host="192.168.1.100") as speaker:
            with pytest.raises((TimeoutError, httpx.TimeoutException)):
                speaker.get_info()
