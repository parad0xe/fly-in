from flyin.exceptions.base import FlyInError


class HubError(FlyInError):
    """Base class for all errors related to hub operations and validation."""

    default_message = "An unspecified hub error occurred."


class HubSelfConnectionError(HubError):
    """Raised when a hub attempt to establish a connection with itself."""

    default_message = "A hub cannot be connected to itself."
