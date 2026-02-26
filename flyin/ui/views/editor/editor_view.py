from typing import cast

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent, QWheelEvent
from PyQt6.QtWidgets import QFrame, QGraphicsView

from flyin.models.graph import Graph
from flyin.ui.bus_events import UIBus
from flyin.ui.views.editor.overlays.map_details_overlay import (
    MapDetailsOverlay,
)
from flyin.ui.views.editor.scenes.map_scene import MapScene


class EditorView(QGraphicsView):
    ZOOM_FACTOR = 0.1
    MAX_ZOOM = 1.5
    MIN_ZOOM = 0.2

    def __init__(self, graph: Graph) -> None:
        scene = MapScene(graph)
        super().__init__(scene)

        scene.selectionChanged.connect(self._on_selection_changed)

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

    def resizeEvent(self, event: QResizeEvent | None):
        super().resizeEvent(event)
        self.update_overlay_position()

    def update_overlay_position(self):
        margin = 20
        x = self.width() - self.overlay.width() - margin
        y = self.height() - self.overlay.height() - margin
        self.overlay.move(x, y)

    def _refresh(self) -> None:
        scene: MapScene = cast(MapScene, self.scene())

        if self.overlay.isVisible():
            selected = scene.selectedItems()
            if selected:
                self.overlay.set_item(selected[0])

    def _on_selection_changed(self) -> None:
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
