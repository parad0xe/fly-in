from flyin.exceptions.base import FlyInError


class GraphError(FlyInError):
    """
    Base class for all errors related to graph operations and validation.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "An unspecified graph error occurred."
