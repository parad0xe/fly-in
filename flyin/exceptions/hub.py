from flyin.exceptions.base import FlyInError


class HubError(FlyInError):
    """
    Base class for all errors related to hub operations and validation.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "An unspecified hub error occurred."


class HubSelfConnectionError(HubError):
    """
    Error raised when a hub attempt to establish a connection with itself.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "A hub cannot be connected to itself."


class HubDuplicateLinkError(HubError):
    """Error raised when a duplicate link is defined between two hubs."""

    def __init__(
        self, hub_a: str, hub_b: str, message: str | None = None
    ) -> None:
        """
        Initialize the error for a redundant connection.

        Args:
            hub_a: The name of the first hub in the duplicate link.
            hub_b: The name of the second hub in the duplicate link.
            message: An optional custom message for the duplicate link.
        """
        msg = (
            message
            or f"Duplicate link detected between '{hub_a}' and '{hub_b}'."
        )
        super().__init__(msg)
