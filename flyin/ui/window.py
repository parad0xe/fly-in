import logging
from typing import Optional

from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from flyin.models.graph import Graph
from flyin.ui.views.editor.editor_view import EditorView
from flyin.ui.widgets.header_widget import HeaderWidget

logger: logging.Logger = logging.getLogger(__name__)


class GraphWindow(QMainWindow):

    def __init__(self, graph: Graph) -> None:
        super().__init__()

        self.graph: Graph = graph

        self.setWindowTitle("Fly-In")
        self.resize(1280, 720)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.header = HeaderWidget(graph)
        main_layout.addWidget(self.header)

        self.editor = EditorView(graph)
        main_layout.addWidget(self.editor)

        central_widget.setLayout(main_layout)

    def keyPressEvent(self, event: Optional[QKeyEvent]) -> None:
        return super().keyPressEvent(event)
