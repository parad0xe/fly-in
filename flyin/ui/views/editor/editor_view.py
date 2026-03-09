from typing import cast

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent, QWheelEvent
from PyQt6.QtWidgets import QFrame, QGraphicsView

from flyin.models.graph import Graph
from flyin.models.hub import Hub
from flyin.ui.bus_events import UIBus
from flyin.ui.items.agent_item import AgentItem
from flyin.ui.views.editor.overlays.map_details_overlay import (
    MapDetailsOverlay,
)
from flyin.ui.views.editor.scenes.map_scene import MapScene


class EditorView(QGraphicsView):
    """
    Interactive graphical view for the editor's map scene.

    Attributes:
        ZOOM_FACTOR: Multiplier step for zooming in or out.
        MAX_ZOOM: Maximum allowed zoom scale factor.
        MIN_ZOOM: Minimum allowed zoom scale factor.
    """

    ZOOM_FACTOR = 0.1
    MAX_ZOOM = 1.5
    MIN_ZOOM = 0.2

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the editor view with the provided graph.

        Args:
            graph: The graph model containing the network data.
        """
        scene = MapScene(graph)
        super().__init__(scene)

        self.agent_items: dict[int, AgentItem] = {}

        scene.selectionChanged.connect(self._on_selection_changed)

        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse,
        )
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.overlay = MapDetailsOverlay(self)

        if scene.start_hub_item is not None:
            self.centerOn(scene.start_hub_item)

        UIBus.get().graph_updated.connect(self._refresh)

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        """
        Handle mouse wheel events for zooming the view.

        Args:
            event: The mouse wheel event containing scroll delta.
        """
        if event is None:
            return

        current_zoom = self.transform().m11()

        if event.angleDelta().y() > 0:
            factor = 1.0 + 1.0 * self.ZOOM_FACTOR
            if current_zoom < self.MAX_ZOOM:
                self.scale(factor, factor)
        else:
            factor = 1.0 - 1.0 * self.ZOOM_FACTOR
            if current_zoom > self.MIN_ZOOM:
                self.scale(factor, factor)

    def resizeEvent(self, event: QResizeEvent | None) -> None:
        """
        Handle view resize events to update UI overlays.

        Args:
            event: The resize event data.
        """
        super().resizeEvent(event)
        self.update_overlay_position()

    def update_overlay_position(self) -> None:
        """
        Update the overlay position to stay in the bottom-right.
        """
        margin = 20
        x = self.width() - self.overlay.width() - margin
        y = self.height() - self.overlay.height() - margin
        self.overlay.move(x, y)

    def _refresh(self, args: tuple[Hub, ...]) -> None:
        """
        Refresh the view with new agent positions.

        Args:
            args: Tuple of updated Hub states for the agents.
        """
        scene: MapScene = cast(MapScene, self.scene())

        for agent_index, hub in enumerate(args):
            if agent_index not in self.agent_items:
                agent_item = AgentItem(hub, agent_index)
                scene.addItem(agent_item)
                self.agent_items[agent_index] = agent_item
            else:
                self.agent_items[agent_index].update_hub(hub)

            UIBus.get().hub_updated.emit()

        if self.overlay.isVisible():
            selected = scene.selectedItems()
            if selected:
                self.overlay.set_item(selected[0])

    def _on_selection_changed(self) -> None:
        """
        Handle item selection changes to update the overlay.
        """
        scene = self.scene()

        if not scene:
            return

        selected_items = scene.selectedItems()

        if not selected_items:
            self.overlay.set_item()
            return

        item = selected_items[0]
        self.overlay.set_item(item)
        self.update_overlay_position()
