import arcade
from arcade import Text

from flyin.models.graph import Graph


class Hud:
    def __init__(self, w: int, h: int, graph: Graph) -> None:
        self.hubs_count = Text(
            f"Nodes: {len(graph.hubs)}",
            x=20,
            y=h - 40,
            color=arcade.color.WHITE,
            font_size=18,
        )

        self.links_count = Text(
            f"Links: {len(graph.links)}",
            x=20,
            y=h - 80,
            color=arcade.color.WHITE,
            font_size=18,
        )

    def render(self) -> None:
        self.hubs_count.draw()
        self.links_count.draw()
