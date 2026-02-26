from typing import Optional

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from flyin.models.graph import Graph
from flyin.ui.items.hub_item import HubItem
from flyin.ui.items.link_item import LinkItem


class HudWidget(QWidget):

    def __init__(self, graph: Graph) -> None:
        super().__init__()

        self.setFixedHeight(60)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#C46210"))
        self.setPalette(palette)

        layout = QHBoxLayout()
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(50)

        font = QFont("Arial", 15, QFont.Weight.Bold)

        self.nodes_label = QLabel(f"Nodes: {len(graph.hubs)}")
        self.nodes_label.setFont(font)
        self.nodes_label.setStyleSheet("color: white;")

        self.links_label = QLabel(f"Links: {len(graph.links)}")
        self.links_label.setFont(font)
        self.links_label.setStyleSheet("color: white;")

        self.selected_label = QLabel("Selected Node: None")
        self.selected_label.setFont(font)
        self.selected_label.setStyleSheet("color: white;")
        self.selected_label.hide()

        layout.addWidget(self.nodes_label)
        layout.addWidget(self.links_label)
        layout.addWidget(self.selected_label)

        layout.addStretch()

        self.setLayout(layout)

    def set_selected_hub(self, item: Optional[HubItem] = None) -> None:
        if item is None:
            self.selected_label.hide()
            return

        self.selected_label.setText(
            f"Selected node: {item.hub.name} "
            f"(drones: {item.hub.drones}) "
            f"(capacity: {item.hub.max_drones})"
        )
        self.selected_label.show()

    def set_selected_link(self, item: Optional[LinkItem] = None) -> None:
        if item is None:
            self.selected_label.hide()
            return

        self.selected_label.setText(
            f"Selected link: {item.hub_a.name} <> {item.hub_b.name} "
            f"(drones: {item.link.drones}) "
            f"(capacity: {item.link.max_link_capacity})"
        )
        self.selected_label.show()
