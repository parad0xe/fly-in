from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel

from flyin.models.graph import Graph


class InfobarWidget(QFrame):

    def __init__(self, graph: Graph) -> None:
        super().__init__()

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
