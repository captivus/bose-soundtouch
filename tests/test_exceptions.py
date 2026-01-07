"""Tests for bose_soundtouch.exceptions module."""

from bose_soundtouch.exceptions import (
    ApiError,
    ConnectionError,
    InvalidResponseError,
    SoundTouchError,
    TimeoutError,
    XmlParseError,
)


class TestExceptionHierarchy:
    """Tests for exception inheritance."""

    def test_connection_error_inherits_from_base(self) -> None:
        """Test ConnectionError inherits from SoundTouchError."""
        assert issubclass(ConnectionError, SoundTouchError)

    def test_timeout_error_inherits_from_base(self) -> None:
        """Test TimeoutError inherits from SoundTouchError."""
        assert issubclass(TimeoutError, SoundTouchError)

    def test_api_error_inherits_from_base(self) -> None:
        """Test ApiError inherits from SoundTouchError."""
        assert issubclass(ApiError, SoundTouchError)

    def test_xml_parse_error_inherits_from_base(self) -> None:
        """Test XmlParseError inherits from SoundTouchError."""
        assert issubclass(XmlParseError, SoundTouchError)

    def test_invalid_response_error_inherits_from_base(self) -> None:
        """Test InvalidResponseError inherits from SoundTouchError."""
        assert issubclass(InvalidResponseError, SoundTouchError)


class TestApiError:
    """Tests for ApiError exception."""

    def test_basic_message(self) -> None:
        """Test ApiError with just a message."""
        error = ApiError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.device_id is None
        assert error.error_code is None
        assert error.error_name is None
        assert error.severity is None

    def test_with_all_attributes(self) -> None:
        """Test ApiError with all attributes."""
        error = ApiError(
            "Invalid request",
            device_id="AABBCCDDEEFF",
            error_code=1019,
            error_name="CLIENT_XML_ERROR",
            severity="Unknown",
        )
        assert error.device_id == "AABBCCDDEEFF"
        assert error.error_code == 1019
        assert error.error_name == "CLIENT_XML_ERROR"
        assert error.severity == "Unknown"

    def test_str_with_error_name(self) -> None:
        """Test string representation with error name."""
        error = ApiError(
            "Invalid request",
            error_name="CLIENT_XML_ERROR",
        )
        assert "CLIENT_XML_ERROR" in str(error)

    def test_str_with_error_code(self) -> None:
        """Test string representation with error code."""
        error = ApiError(
            "Invalid request",
            error_code=1019,
        )
        assert "1019" in str(error)

    def test_str_with_name_and_code(self) -> None:
        """Test string representation with both name and code."""
        error = ApiError(
            "Invalid request",
            error_name="CLIENT_XML_ERROR",
            error_code=1019,
        )
        error_str = str(error)
        assert "Invalid request" in error_str
        assert "CLIENT_XML_ERROR" in error_str
        assert "1019" in error_str
