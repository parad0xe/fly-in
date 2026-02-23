from __future__ import annotations

from collections import Counter
from enum import Enum
from typing import Any, Generator

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
    DARK_RED = "darkred"
    VIOLET = "violet"
    CRIMSON = "crimson"
    RAINBOW = "rainbow"
    CYAN = "cyan"


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
    color: HubColorType | None = None
    drones: int = Field(default=0, ge=0)
    max_drones: int = Field(default=1, ge=0)

    is_leaf: bool = True

    connections: list[tuple[Hub, Link]] = Field(default_factory=lambda: [])

    def model_post_init(self, context: Any) -> None:
        """Execute integrity checks after model initialization."""
        self.ensure_integrity()
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

        if len(self.connections) > 1:
            self.is_leaf = False
        else:
            self.is_leaf = True

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

    def iter_unique_connections(self) -> Generator[tuple[Hub, Link]]:
        viewed_links: list[int] = []
        for to, link in self.connections:
            if link.id not in viewed_links:
                viewed_links.append(link.id)
                yield (to, link)
