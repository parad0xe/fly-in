from __future__ import annotations

from collections import Counter
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

from flyin.exceptions.hub import (
    HubDuplicateLinkError,
    HubInsufficientCapacityError,
    HubSelfConnectionError,
)
from flyin.models.link import Link


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
    """Represent a spatial network node with operational constraints.

    Attributes:
        name: Unique identifier starting with a letter.
        x: X-coordinate in the spatial grid.
        y: Y-coordinate in the spatial grid.
        zone: Access level (defaults to NORMAL).
        color: Optional visual identifier.
        drones: Current number of drones stationed.
        max_drones: Maximum drone capacity.
        is_leaf: True if the hub has one or fewer connections.
        connections: List of peer hubs and their associated links.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, pattern=r"^[a-zA-Z]\w*$")
    x: int
    y: int

    zone: HubZoneType = HubZoneType.NORMAL
    color: str = "gray"
    drones: int = Field(default=0, ge=0)
    max_drones: int = Field(default=1, ge=0)

    is_dummy: bool = False

    connections: list[tuple[Hub, Link]] = Field(default_factory=lambda: [])

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.name))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Hub):
            return (
                self.x == other.x and self.y == other.y and
                self.name == other.name
            )
        return False

    def __lt__(self, other: Hub) -> bool:
        if self.x != other.x:
            return self.x < other.x
        if self.y != other.y:
            return self.y < other.y
        return self.name < other.name

    def model_post_init(self, context: Any) -> None:
        """Execute integrity checks after model initialization."""
        self.ensure_integrity()

        self.color = self.color.lower()
        return super().model_post_init(context)

    def ensure_integrity(self) -> Self:
        """
        Ensure connections are logically consistent.

        Updates the is_leaf status and prevents self-linking or
            duplicate connections.

        Returns:
            The current instance for chaining.

        Raises:
            HubDuplicateLinkError: If multiple links exist to same hub.
            HubSelfConnectionError: If a hub attempts to link to itself.
        """
        hub_names = [hub.name for hub, _ in self.connections]
        hub_name_counts = Counter(hub_names)

        for name, count in hub_name_counts.items():
            if count > 1:
                raise HubDuplicateLinkError(self.name, name)

        for hub, _ in self.connections:
            if hub.name == self.name:
                raise HubSelfConnectionError()

        if self.drones > self.max_drones:
            raise HubInsufficientCapacityError()

        return self

    def connect_to(self, hub: Hub, link: Link) -> None:
        """
        Add a directed connection to a peer hub.

        Args:
            hub: Target hub instance.
            link: Link properties for this connection.
        """
        self.connections.append((hub, link))
        self.ensure_integrity()

    def connect_both(self, hub: Hub, link: Link) -> None:
        """
        Establish a bidirectional connection between two hubs.

        Args:
            hub: Peer hub to connect with.
            link: Shared link instance for both directions.
        """
        self.connect_to(hub, link)
        hub.connect_to(self, link)
