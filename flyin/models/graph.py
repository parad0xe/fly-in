from typing import Any, Iterator

from pydantic import BaseModel, ConfigDict

from flyin.exceptions.graph import GraphInsufficientHubCapacityError
from flyin.models.hub import Hub
from flyin.models.link import Link


class Graph(BaseModel):
    """
    Represents the complete network topology for drone routing.

    Attributes:
        hubs: List of all hubs (nodes) within the graph.
        links: List of all connections (edges) between hubs.
        start_hub: The designated hub where the drone fleet starts.
        end_hub: The designated target hub for the drone fleet.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hubs: list[Hub]
    links: list[Link]
    start_hub: Hub
    end_hub: Hub

    def model_post_init(self, context: Any) -> None:
        if self.start_hub.drones > self.end_hub.max_drones:
            raise GraphInsufficientHubCapacityError()
        return super().model_post_init(context)

    def iter_unique_connections(self) -> Iterator[tuple[Hub, Hub, Link]]:
        """
        Yields unique connections between hubs in the graph.

        Returns:
            An iterator of hub A, hub B, and unique link triplets.
        """
        viewed_links: set[int] = set()
        for hub in self.hubs:
            for to, link in hub.connections:
                if link.id not in viewed_links:
                    viewed_links.add(link.id)
                    yield (hub, to, link)
