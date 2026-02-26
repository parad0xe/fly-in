from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from flyin.models.graph import Graph


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

        layout.addWidget(self.nodes_label)
        layout.addWidget(self.links_label)

        layout.addStretch()

        self.setLayout(layout)
