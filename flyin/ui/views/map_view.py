from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QResizeEvent, QWheelEvent
from PyQt6.QtWidgets import QFrame, QGraphicsScene, QGraphicsView

from flyin.models.graph import Graph
from flyin.ui.items.hub_item import HubItem
from flyin.ui.items.link_item import LinkItem
from flyin.ui.overlays.map_info_overlay import MapInfoOverlay


class MapView(QGraphicsView):

    def __init__(self, graph: Graph) -> None:
        scene = QGraphicsScene()
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

        scene.setBackgroundBrush(QColor("#534b4f"))

        self.overlay = MapInfoOverlay(self)

        for hub in graph.hubs:
            scene.addItem(HubItem(hub))

        for hub_a, hub_b, link in graph.iter_unique_connections():
            scene.addItem(LinkItem(hub_a, hub_b, link))

        self.update_scene_bounds()

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        if event is None:
            return

        current_zoom = self.transform().m11()

        zoom_in_factor = 1.1
        zoom_out_factor = 0.9

        if event.angleDelta().y() > 0:
            if current_zoom < 1.5:
                self.scale(zoom_in_factor, zoom_in_factor)
        else:
            if current_zoom > 0.2:
                self.scale(zoom_out_factor, zoom_out_factor)

    def resizeEvent(self, event: QResizeEvent | None):
        super().resizeEvent(event)
        self.update_overlay_position()

    def update_overlay_position(self):
        margin = 20
        x = self.width() - self.overlay.width() - margin
        y = self.height() - self.overlay.height() - margin
        self.overlay.move(x, y)

    def update_scene_bounds(self) -> None:
        scene = self.scene()

        if scene is None:
            return

        items_rect = scene.itemsBoundingRect()

        padding = 2000
        new_rect = items_rect.adjusted(-padding, -padding, padding, padding)

        scene.setSceneRect(new_rect)

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
