import itertools
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

_id_counter = itertools.count(1)


class Link(BaseModel):
    """
    Represents a connection link with capacity constraints.

    Attributes:
        drones: Current number of drones traveling on this link.
        max_link_capacity: Maximum drone capacity allowed on the link.
    """

    model_config = ConfigDict(extra="forbid")

    id: int = Field(default_factory=lambda: next(_id_counter), frozen=True)
    drones: int = Field(default=0, ge=0)
    max_link_capacity: int = Field(default=1, ge=0, frozen=True)

    @model_validator(mode="before")
    @classmethod
    def prevent_id_injection(cls, data: Any) -> Any:
        """
        Removes 'id' from input data to ensure auto-generation is used.

        Args:
            data: Raw input dictionary before Pydantic model validation.

        Returns:
            The sanitized input dictionary without the 'id' key.
        """
        if isinstance(data, dict) and "id" in data:
            data.pop("id")
        return data
