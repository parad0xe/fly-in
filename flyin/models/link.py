import itertools
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

_id_counter = itertools.count(1)


class Link(BaseModel):
    """
    Represents a connection link with capacity constraints.

    Attributes:
        drones: Current number of drones traveling on this link.
        max_link_capacity: Maximum drone capacity allowed on the link.
    """

    WHITELIST: ClassVar[set[str]] = {
        "max_link_capacity",
    }

    model_config = ConfigDict(extra="forbid")

    id: int = Field(default_factory=lambda: next(_id_counter), frozen=True)
    drones: int = Field(default=0, ge=0)
    max_link_capacity: int = Field(default=1, ge=0, frozen=True)

    @model_validator(mode="before")
    @classmethod
    def force_whitelist_init(cls, data: Any) -> Any:
        """
        Restricts instantiation to a specific whitelist of fields.

        Args:
            data: Raw input dictionary before Pydantic validation.

        Returns:
            The original data if it only contains allowed keys.

        Raises:
            ValueError: If a field outside the whitelist is provided.
        """
        if isinstance(data, dict):
            provided = set(data.keys())
            forbidden = provided - cls.WHITELIST

            if forbidden:
                raise PydanticCustomError(
                    "initialization_error",
                    "Forbidden fields at instantiation: {forbidden}. "
                    "Allowed: {allowed}",
                    {
                        "forbidden": list(forbidden),
                        "allowed": list(cls.WHITELIST),
                    },
                )
        return data
