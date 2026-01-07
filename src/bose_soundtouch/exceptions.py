"""Exception hierarchy for the bose_soundtouch library."""

from __future__ import annotations


class SoundTouchError(Exception):
    """Base exception for all SoundTouch errors."""


class ConnectionError(SoundTouchError):
    """Failed to connect to the SoundTouch device."""


class TimeoutError(SoundTouchError):
    """Request to device timed out."""


class ApiError(SoundTouchError):
    """Device returned an error response."""

    def __init__(
        self,
        message: str,
        *,
        device_id: str | None = None,
        error_code: int | None = None,
        error_name: str | None = None,
        severity: str | None = None,
    ) -> None:
        """
        Initialize an API error.

        Args:
            message: Error message.
            device_id: Device MAC address that returned the error.
            error_code: Numeric error code from the device.
            error_name: Named error code (e.g., CLIENT_XML_ERROR).
            severity: Error severity level.
        """
        super().__init__(message)
        self.device_id = device_id
        self.error_code = error_code
        self.error_name = error_name
        self.severity = severity

    def __str__(self) -> str:
        """Return a formatted error message."""
        parts = [super().__str__()]
        if self.error_name:
            parts.append(f"[{self.error_name}]")
        if self.error_code is not None:
            parts.append(f"(code={self.error_code})")
        return " ".join(parts)


class XmlParseError(SoundTouchError):
    """Failed to parse XML response from device."""


class InvalidResponseError(SoundTouchError):
    """Response from device was not in expected format."""
