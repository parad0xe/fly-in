from pydantic import BaseModel, ConfigDict

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
