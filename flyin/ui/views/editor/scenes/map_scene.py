from typing import Optional

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsScene

from flyin.models.graph import Graph
from flyin.ui.constants import SCENE_PADDING
from flyin.ui.items.hub_item import HubItem
from flyin.ui.items.link_item import LinkItem


class MapScene(QGraphicsScene):
    """
    Graphical scene managing and displaying graph hubs and links.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the map scene with graph data.

        Args:
            graph: The graph model containing hubs and connections.
        """
        super().__init__()

        self.start_hub_item: Optional[HubItem] = None
        self.setBackgroundBrush(QColor("#534b4f"))

        for hub in graph.hubs:
            hub_item = HubItem(hub)
            if graph.start_hub == hub:
                self.start_hub_item = hub_item
            self.addItem(hub_item)

        for hub_a, hub_b, link in graph.iter_unique_connections():
            self.addItem(LinkItem(hub_a, hub_b, link))

        self.update_bounds()

    def update_bounds(self) -> None:
        """
        Recalculate and update the scene boundaries with padding.
        """
        items_rect = self.itemsBoundingRect()

        new_rect = items_rect.adjusted(
            -SCENE_PADDING,
            -SCENE_PADDING,
            SCENE_PADDING,
            SCENE_PADDING,
        )

        self.setSceneRect(new_rect)
