from typing import Any

import arcade
from arcade import Camera2D, Section, SectionManager, Text, View
from arcade.shape_list import Shape, ShapeElementList

from flyin.models.graph import Graph
from flyin.renderer.camera import CameraController
from flyin.renderer.objects.hub import HubShape
from flyin.renderer.objects.link import LinkShape


class InfobarSection(Section):
    def __init__(
        self,
        graph: Graph,
        left: int,
        bottom: int,
        width: int,
        height: int,
        **kwargs: Any,
    ) -> None:
        super().__init__(left, bottom, width, height, **kwargs)

        self.graph: Graph = graph

        self.node_text = Text(
            f"Nodes: {len(self.graph.hubs)}",
            x=20,
            y=self.window.height - 40,
            color=arcade.color.WHITE,
            font_size=18,
        )

        self.link_text = Text(
            f"Links: {len(self.graph.links)}",
            x=200,
            y=self.window.height - 40,
            color=arcade.color.WHITE,
            font_size=18,
        )

    def on_resize(self, _: int, height: int) -> None:
        self.node_text.y = height - 40
        self.link_text.y = height - 40

    def on_draw(self) -> None:
        self.node_text.draw()
        self.link_text.draw()


class MapSection(Section):
    def __init__(
        self,
        graph: Graph,
        left: int,
        bottom: int,
        width: int,
        height: int,
        **kwargs: Any,
    ) -> None:
        super().__init__(left, bottom, width, height, **kwargs)

        self.graph: Graph = graph

        self.background_color = arcade.color.DARK_LIVER

        self.shapes: ShapeElementList[Shape] = ShapeElementList()
        self.links: ShapeElementList[Shape] = ShapeElementList()

        self.camera: Camera2D = Camera2D()
        self.camera_controller = CameraController(self.camera)

        for hub in self.graph.hubs:
            self.shapes.append(HubShape.create(hub, size=23))

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
        self.camera_controller.move(dx, dy)

    def on_mouse_scroll(
        self, x: int, y: int, scroll_x: float, scroll_y: float
    ) -> None:
        self.camera_controller.zoom(0.1 * scroll_y)

    def on_draw(self) -> None:
        with self.camera.activate():
            self.links.draw()
            self.shapes.draw()


class EditorView(View):
    def __init__(self, graph: Graph) -> None:
        super().__init__()

        self.graph = graph

        self.background_color = arcade.color.DARK_LIVER

        self.map = MapSection(
            graph,
            0,
            0,
            self.window.width,
            self.window.height - 60,
        )

        self.infobar = InfobarSection(
            graph,
            0,
            0,
            self.window.width,
            60,
        )
        self.section_manager = SectionManager(self)
        self.section_manager.add_section(self.map)
        self.section_manager.add_section(self.infobar)

    def on_show_view(self) -> None:
        self.section_manager.enable()

    def on_hide_view(self) -> None:
        self.section_manager.disable()

    def on_resize(self, width: int, height: int) -> None:
        self.map.width = width
        self.map.height = height - 60

    def on_draw(self) -> None:
        self.clear()
