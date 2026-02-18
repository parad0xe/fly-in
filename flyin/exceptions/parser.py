from flyin.exceptions.base import FlyInError


class ParserError(FlyInError):
    """
    Base class for all errors occurring during graph parsing.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "An error occurred while parsing the graph data."

    def __init__(self, lineno: int, message: str | None = None) -> None:
        """
        Initialize the error with a specific line index.

        Args:
            lineno: The index of the line where the error occurred.
            message: An optional custom message describing the error.
        """
        message = message or self.default_message
        super().__init__(f"{message} (line: {lineno})")


class ParserMissingSeparatorError(ParserError):
    """Error raised when a mandatory separator is missing from a line."""

    def __init__(
        self, lineno: int, separator: str, message: str | None = None
    ) -> None:
        """
        Initialize the error with the missing separator character.

        Args:
            lineno: The index of the line where the separator is missing.
            separator: The specific character that was expected.
            message: An optional custom message for the missing separator.
        """
        message = (
            message
            or f"Required separator '{separator}' not found on this line."
        )
        super().__init__(lineno, message)


class ParserUnknownKeyError(ParserError):
    """Error raised when a configuration key is not recognized."""

    def __init__(
        self, lineno: int, key: str, message: str | None = None
    ) -> None:
        """
        Initialize the error with the unrecognized key detected.

        Args:
            lineno: The index of the line containing the unknown key.
            key: The string value of the unrecognized key.
            message: An optional custom message for the unknown key.
        """
        message = message or f"Unknown configuration key: '{key}'."
        super().__init__(lineno, message)


class ParserUnhandledKeyError(ParserError):
    """Error raised when a recognized key has no associated parsing logic."""

    def __init__(
        self, lineno: int, key: str, message: str | None = None
    ) -> None:
        """
        Initialize the error for a key lacking an implementation handler.

        Args:
            lineno: The index of the line where the handler is missing.
            key: The key that has no associated parsing logic.
            message: An optional custom message for the missing handler.
        """
        message = message or f"No handler defined to process the key: '{key}'."
        super().__init__(lineno, message)


class ParserMissingHubError(ParserError):
    """Error raised when a link refers to a non-existent hub name."""

    def __init__(
        self, lineno: int, hub_name: str, message: str | None = None
    ) -> None:
        """
        Initialize the error for an undefined hub reference.

        Args:
            lineno: The index of the line where the error occurred.
            hub_name: The name of the hub that was not found.
            message: An optional custom message for the reference error.
        """
        message = message or f"Reference to undefined hub: '{hub_name}'."
        super().__init__(lineno, message)
