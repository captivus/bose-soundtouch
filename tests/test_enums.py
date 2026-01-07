"""Tests for bose_soundtouch.enums module."""

from bose_soundtouch.enums import (
    ArtStatus,
    AudioMode,
    KeyState,
    KeyValue,
    PlayStatus,
    SourceStatus,
)


class TestKeyValue:
    """Tests for KeyValue enum."""

    def test_play_value(self) -> None:
        """Test PLAY key value."""
        assert KeyValue.PLAY == "PLAY"
        assert KeyValue.PLAY.value == "PLAY"

    def test_preset_values(self) -> None:
        """Test preset key values."""
        assert KeyValue.PRESET_1 == "PRESET_1"
        assert KeyValue.PRESET_6 == "PRESET_6"

    def test_all_keys_are_strings(self) -> None:
        """Test that all key values are strings."""
        for key in KeyValue:
            assert isinstance(key.value, str)


class TestKeyState:
    """Tests for KeyState enum."""

    def test_press_state(self) -> None:
        """Test press state value."""
        assert KeyState.PRESS == "press"

    def test_release_state(self) -> None:
        """Test release state value."""
        assert KeyState.RELEASE == "release"


class TestPlayStatus:
    """Tests for PlayStatus enum."""

    def test_play_state(self) -> None:
        """Test PLAY_STATE value."""
        assert PlayStatus.PLAY_STATE == "PLAY_STATE"

    def test_pause_state(self) -> None:
        """Test PAUSE_STATE value."""
        assert PlayStatus.PAUSE_STATE == "PAUSE_STATE"

    def test_invalid_status(self) -> None:
        """Test INVALID_PLAY_STATUS value."""
        assert PlayStatus.INVALID_PLAY_STATUS == "INVALID_PLAY_STATUS"


class TestSourceStatus:
    """Tests for SourceStatus enum."""

    def test_ready_status(self) -> None:
        """Test READY value."""
        assert SourceStatus.READY == "READY"

    def test_unavailable_status(self) -> None:
        """Test UNAVAILABLE value."""
        assert SourceStatus.UNAVAILABLE == "UNAVAILABLE"


class TestArtStatus:
    """Tests for ArtStatus enum."""

    def test_image_present(self) -> None:
        """Test IMAGE_PRESENT value."""
        assert ArtStatus.IMAGE_PRESENT == "IMAGE_PRESENT"

    def test_invalid(self) -> None:
        """Test INVALID value."""
        assert ArtStatus.INVALID == "INVALID"


class TestAudioMode:
    """Tests for AudioMode enum."""

    def test_normal_mode(self) -> None:
        """Test NORMAL mode value."""
        assert AudioMode.NORMAL == "AUDIO_MODE_NORMAL"

    def test_dialog_mode(self) -> None:
        """Test DIALOG mode value."""
        assert AudioMode.DIALOG == "AUDIO_MODE_DIALOG"

    def test_night_mode(self) -> None:
        """Test NIGHT mode value."""
        assert AudioMode.NIGHT == "AUDIO_MODE_NIGHT"

    def test_direct_mode(self) -> None:
        """Test DIRECT mode value."""
        assert AudioMode.DIRECT == "AUDIO_MODE_DIRECT"
