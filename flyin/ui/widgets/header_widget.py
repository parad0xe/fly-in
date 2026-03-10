from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel

from flyin.models.graph import Graph
from flyin.ui.bus_events import UIBus


class HeaderWidget(QFrame):
    """
    Top banner displaying global graph statistics and information.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the header widget with graph statistics.

        Args:
            graph: The graph model instance to extract stats from.
        """
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
        self.drones_label = QLabel(f"Drones: {graph.nb_drones}")
        self.info_label = QLabel("")

        layout.addWidget(self.nodes_label)
        layout.addWidget(self.links_label)
        layout.addWidget(self.drones_label)
        layout.addStretch()
        layout.addWidget(self.info_label)

        self.setLayout(layout)

        UIBus.get().info.connect(self._refresh)

    def _refresh(self, text: str) -> None:
        """
        Update the informational text displayed in the header.

        Args:
            text: The new string to display in the info label.
        """
        self.info_label.setText(f"{text}")
