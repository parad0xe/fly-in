from pydantic import BaseModel, ConfigDict, Field


class Link(BaseModel):
    """
    Represents a connection link with capacity constraints.

    Attributes:
        drones: Current number of drones traveling on this link.
        max_link_capacity: Maximum drone capacity allowed on the link.
    """

    model_config = ConfigDict(extra="forbid")

    drones: int = Field(default=0, ge=0)
    max_link_capacity: int = Field(default=1, ge=0, frozen=True)
