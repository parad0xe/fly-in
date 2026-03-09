from flyin.exceptions.base import FlyInError


class SolverError(FlyInError):
    """
    Base class for all errors related to solve operations.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "Failed to solve the graph."


class SolverConfigurationMismatchError(SolverError):
    """
    Error raised when start and end configurations have different sizes.

    Attributes:
        default_message: Fallback message used when no message is provided.
    """

    default_message = "Invalid configuration: start and end lengths differ."
