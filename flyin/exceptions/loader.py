from pydantic import ValidationError

from flyin.exceptions.base import FlyInError


class LoaderError(FlyInError):
    """
    Base class for all errors related to graph operations and integrity.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "Failed to load the graph data."


class LoaderFileNotFoundError(LoaderError):
    """
    Error raised when the target graph file does not exist on the filesystem.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "The specified graph file was not found."


class LoaderFilePermissionError(LoaderError):
    """
    Error raised when the application lacks permissions to access the file.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "Permission denied for the specified graph file."


class LoaderEmptyFileError(LoaderError):
    """
    Error raised when the provided graph file contains no data to parse.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "The graph file is empty."


class LoaderValidationError(LoaderError):
    """Error raised when configuration data fails validation checks."""

    def __init__(self, e: ValidationError) -> None:
        """
        Formats and initializes validation error details.

        Args:
            e: The validation error object containing a
                collection of failures (pydantic.ValidationError).
        """
        messages: list[str] = []

        messages.append("")
        for error in e.errors():
            messages.append(f"- (field: '{error['loc'][0]}') {error['msg']}")
        super().__init__("\n".join(messages))
