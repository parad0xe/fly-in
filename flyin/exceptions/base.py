from __future__ import annotations


class FlyInError(Exception):
    """Base class for all domain-specific errors in the system."""

    default_message = "An unspecified error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)
