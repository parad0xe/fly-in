from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from flyin.exceptions.hub import HubSelfConnectionError
from flyin.models.link import Link


class HubColorType(str, Enum):
    """Define the available categorical colors for hub identification."""

    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    GRAY = "gray"


class HubZoneType(str, Enum):
    """
    Specify the operational security and access levels for a hub location.
    """

    RESTRICTED = "restricted"
    NORMAL = "normal"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class HubMetadataType(str, Enum):
    """Categorize the types of metadata attributes associated with a hub."""

    ZONE = "zone"
    COLOR = "color"
    MAX_DRONE = "max_drone"


class Hub(BaseModel):
    """
    Represent a spatial network node with
        operational constraints and peer connections.
    """

    name: str = Field(min_length=1, pattern=r"^[a-zA-Z]\w*$")
    x: int
    y: int

    zone: HubZoneType = HubZoneType.NORMAL
    color: HubColorType | None = None
    max_drones: int = Field(default=1, ge=0)

    links: list[tuple[Hub, Link]] = Field(default_factory=lambda: [])

    @model_validator(mode="after")
    def validate_link_integrity(self) -> Self:
        """
        Ensure all peer connections are logically
            consistent and prevent self-linking.
        """
        for hub, _ in self.links:
            if hub.name == self.name:
                raise HubSelfConnectionError()
        return self
