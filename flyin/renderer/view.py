import arcade
from arcade.shape_list import (
    Shape,
    ShapeElementList,
)
from typing_extensions import Self

from flyin.models.graph import Graph
from flyin.renderer.camera import CameraController
from flyin.renderer.hud import Hud
from flyin.renderer.objects.hub import HubShape
from flyin.renderer.objects.link import LinkShape


class GraphRenderer(arcade.Window):
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

        self.background_color = arcade.color.DARK_LIVER

        self.shapes: ShapeElementList[Shape] = ShapeElementList()
        self.links: ShapeElementList[Shape] = ShapeElementList()

        self.camera = CameraController()
        self.hud = Hud(self.WINDOW_WIDTH, self.WINDOW_HEIGHT, self.graph)

    def setup(self) -> None:
        for hub in self.graph.hubs:
            self.shapes.append(HubShape.create(hub, size=22))

        for hub_a, hub_b, _ in self.graph.iter_unique_connections():
            self.links.append(
                LinkShape.connect_hub(hub_a, hub_b, arcade.color.GRAY)
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
        self.camera.move(dx, dy)

    def on_mouse_scroll(
        self, x: int, y: int, scroll_x: float, scroll_y: float
    ) -> None:
        self.camera.zoom(0.1 * scroll_y)

    def on_draw(self) -> None:
        self.clear()

        with self.camera.camera.activate():
            self.links.draw()
            self.shapes.draw()

        self.hud.render()
