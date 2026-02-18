from pydantic import BaseModel, ConfigDict

from flyin.models.hub import Hub
from flyin.models.link import Link


class Graph(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    hubs: list[Hub]
    links: list[Link]
    start_hub: Hub
    end_hub: Hub
