from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from flyin.models.graph import Graph
from flyin.ui.views.map_view import MapView
from flyin.ui.widgets.hud_widget import HudWidget


class Hud:
    pass


class GraphWindow(QMainWindow):

    def __init__(self, graph: Graph) -> None:
        super().__init__()

        self.setWindowTitle("Fly-In")
        self.resize(1280, 720)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.hud = HudWidget(graph)
        main_layout.addWidget(self.hud)

        self.map = MapView(graph)
        main_layout.addWidget(self.map)

        central_widget.setLayout(main_layout)
