from typing import cast

import arcade
from arcade.shape_list import (
    Shape,
    ShapeElementList,
    create_line,
    create_polygon,
)
from arcade.types import RGBA255
from typing_extensions import Self

from flyin.models.graph import Graph
from flyin.models.hub import Hub


class Triangle:

    @staticmethod
    def create(x: int, y: int, color: RGBA255, size: int = 50) -> Shape:
        points = [
            (x, y + size),
            (x - size, y - size),
            (x + size, y - size),
        ]

        return create_polygon(points, color)


class Line:

    @staticmethod
    def connect_hub(hub_a: Hub, hub_b: Hub, color: RGBA255) -> Shape:
        return create_line(
            200 * hub_a.x,
            200 * hub_a.y,
            200 * hub_b.x,
            200 * hub_b.y,
            color,
            5,
        )


class GraphWindow(arcade.Window):
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    WINDOW_TITLE = "Fly-In"

    @classmethod
    def load(cls, graph: Graph) -> Self:
        window = cls(graph)
        window.setup()
        return window

    def __init__(self, graph: Graph) -> None:
        super().__init__(
            self.WINDOW_WIDTH,
            self.WINDOW_HEIGHT,
            self.WINDOW_TITLE,
            resizable=True,
        )

        self.graph = graph
        self.background_color = arcade.color.BLACK

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.shapes: ShapeElementList = ShapeElementList()
        self.links: ShapeElementList = ShapeElementList()

        self.texts: dict[str, arcade.Text] = {
            "hubs_count": cast(arcade.Text, None),
            "links_count": cast(arcade.Text, None),
        }

    def setup(self) -> None:
        self.texts["hubs_count"] = arcade.Text(
            f"Nodes: {len(self.graph.hubs)}",
            x=20,
            y=self.WINDOW_HEIGHT - 40,
            color=arcade.color.WHITE,
            font_size=18,
        )

        self.texts["links_count"] = arcade.Text(
            f"Links: {len(self.graph.links)}",
            x=20,
            y=self.WINDOW_HEIGHT - 80,
            color=arcade.color.WHITE,
            font_size=18,
        )

        self.camera.position = (0, 0)
        self.camera.zoom = 0.7

        viewed_links: list[int] = []
        for hub in self.graph.hubs:
            shape = Triangle.create(
                200 * hub.x, 200 * hub.y, arcade.csscolor.PURPLE, size=20
            )

            self.shapes.append(shape)

            for to, link in hub.links:
                if link.id not in viewed_links:
                    viewed_links.append(link.id)
                    self.links.append(
                        Line.connect_hub(hub, to, arcade.color.GRAY)
                    )

    def on_mouse_drag(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        buttons: int,
        modifiers: int,
    ) -> None:
        self.camera.position = (
            self.camera.position.x - dx / self.camera.zoom,
            self.camera.position.y - dy / self.camera.zoom,
        )

    def on_draw(self) -> None:
        self.clear()

        self.camera.use()
        self.links.draw()
        self.shapes.draw()

        self.gui_camera.use()

        for text in self.texts.values():
            text.draw()
