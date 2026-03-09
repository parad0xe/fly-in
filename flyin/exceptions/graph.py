from flyin.exceptions.base import FlyInError


class GraphError(FlyInError):
    """
    Base class for all errors related to graph operations and validation.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "An unspecified graph error occurred."


class GraphHubNotFoundError(GraphError):
    """
    Raised when a specific hub cannot be located within the graph.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "The specified hub was not found within the graph."
