from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel

from flyin.models.graph import Graph
from flyin.ui.bus_events import UIBus


class HeaderWidget(QFrame):

    def __init__(self, graph: Graph) -> None:
        super().__init__()

        self.graph: Graph = graph

        self.setFixedHeight(60)

        self.setStyleSheet(
            """
            QFrame {
                background-color: #C46210;
            }
            QLabel {
                color: white;
                font-family: Arial;
                font-size: 15px;
                font-weight: bold;
            }
            """
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(50)

        self.nodes_label = QLabel(f"Nodes: {len(graph.hubs)}")
        self.links_label = QLabel(f"Links: {len(graph.links)}")

        layout.addWidget(self.nodes_label)
        layout.addWidget(self.links_label)
        layout.addStretch()

        self.setLayout(layout)

        UIBus.get().graph_updated.connect(self._refresh)

    def _refresh(self) -> None:
        self.nodes_label.setText(f"Nodes: {len(self.graph.hubs)}")
        self.links_label.setText(f"Links: {len(self.graph.links)}")
