from __future__ import annotations

from collections import Counter
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

from flyin.exceptions.hub import HubDuplicateLinkError, HubSelfConnectionError
from flyin.models.link import Link


class HubColorType(str, Enum):
    """Define the available categorical colors for hub identification."""

    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    GRAY = "gray"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    BLACK = "black"
    BROWN = "brown"
    MAROON = "maroon"
    GOLD = "gold"
    DARKRED = "darkred"
    VIOLET = "violet"
    CRIMSON = "crimson"
    rainbow = "rainbow"


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

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, pattern=r"^[a-zA-Z]\w*$")
    x: int
    y: int

    zone: HubZoneType = HubZoneType.NORMAL
    color: HubColorType | None = None
    drones: int = Field(default=0, ge=0)
    max_drones: int = Field(default=1, ge=0)

    is_leaf: bool = True

    links: list[tuple[Hub, Link]] = Field(default_factory=lambda: [])

    def model_post_init(self, context: Any) -> None:
        self.ensure_integrity()
        return super().model_post_init(context)

    def ensure_integrity(self) -> Self:
        """
        Ensure all peer connections are logically
            consistent and prevent self-linking.
        """
        hub_names = [hub.name for hub, _ in self.links]
        hub_name_counts = Counter(hub_names)

        for name, count in hub_name_counts.items():
            if count > 1:
                raise HubDuplicateLinkError(self.name, name)

        for hub, _ in self.links:
            if hub.name == self.name:
                raise HubSelfConnectionError()

        if len(self.links) > 1:
            self.is_leaf = False
        else:
            self.is_leaf = True

        return self

    def connect_to(self, hub: Hub, link: Link) -> None:
        self.links.append((hub, link))
        self.ensure_integrity()

    def connect_both(self, hub: Hub, link: Link) -> None:
        self.connect_to(hub, link)
        hub.connect_to(self, link)
