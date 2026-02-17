from flyin.exceptions.base import FlyInError


class GraphError(FlyInError):
    """Base class for all errors related to graph operations and integrity."""

    default_message = "An unspecified graph error occurred."


class GraphLoadError(GraphError):
    """Raised when a graph fails to be loaded or parsed from its source."""

    default_message = "Failed to load the graph data."


class GraphParseError(GraphLoadError):
    """Raised when a graph fails to be parsed from its source."""

    default_message = "Failed to parse the graph data."

    def __init__(self, line_index: int, message: str | None = None) -> None:
        message = message or self.default_message
        super().__init__(f"{message} (line: {line_index})")


class GraphFileNotFoundError(GraphLoadError):
    """Raised when the target graph file does not exist on the filesystem."""

    default_message = "The specified graph file was not found."


class GraphFilePermissionError(GraphLoadError):
    """Raised when the application lacks permissions to access the file."""

    default_message = "Permission denied for the specified graph file."


class GraphEmptyFileError(GraphLoadError):
    """Raised when the provided graph file contains no data to parse."""

    default_message = "The graph file is empty."
