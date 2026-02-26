from typing import Optional

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsScene

from flyin.models.graph import Graph
from flyin.ui.items.hub_item import HubItem
from flyin.ui.items.link_item import LinkItem


class MapScene(QGraphicsScene):

    def __init__(self, graph: Graph):
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
        items_rect = self.itemsBoundingRect()

        padding = 2000
        new_rect = items_rect.adjusted(-padding, -padding, padding, padding)

        self.setSceneRect(new_rect)
