import logging
from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from flyin.models.graph import Graph
from flyin.solver.lacam import Lacam
from flyin.solver.types import Config
from flyin.ui.bus_events import UIBus
from flyin.ui.constants import ANIMATION_DURATION
from flyin.ui.views.editor.editor_view import EditorView
from flyin.ui.widgets.header_widget import HeaderWidget

logger: logging.Logger = logging.getLogger(__name__)


class GraphWindow(QMainWindow):
    """
    Main application window displaying the drone network graph.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initializes the main window and sets up the layout.

        Args:
            graph: The drone network graph to display and solve.
        """
        super().__init__()

        self.graph: Graph = graph
        self.solution: Optional[list[Config]] = None
        self.solution_index: int = 0

        self.setWindowTitle("Fly-In")
        self.resize(1280, 720)

        self._setup_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timeout)

        self.start()

    def _setup_ui(self) -> None:
        """
        Configures the central widget and its vertical layout.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.header = HeaderWidget(self.graph)
        main_layout.addWidget(self.header)

        self.editor = EditorView(self.graph)
        main_layout.addWidget(self.editor)

        central_widget.setLayout(main_layout)

    def start(self) -> None:
        """
        Computes the Lacam solution and starts the visualizer.
        """
        config_start = (self.graph.start_hub,) * self.graph.nb_drones
        config_end = (self.graph.end_hub,) * self.graph.nb_drones

        UIBus.get().info.emit("Solving..")
        self.solution = Lacam.solve(
            graph=self.graph,
            config_start=config_start,
            config_end=config_end,
        )

        if not self.solution:
            UIBus.get().info.emit("No solution founded")
        else:
            untracked: set[int] = set()

            for config in self.solution:
                for agent_index in range(self.graph.nb_drones):
                    if agent_index not in untracked:
                        print(
                            f"D{agent_index}-{config[agent_index].name}",
                            end=" ",
                        )
                        if config[agent_index] == config_end[agent_index]:
                            untracked.add(agent_index)
                print("")

            self._update_state(0)

    def _update_state(self, index: int) -> None:
        """
        Safely updates the step index and emits the graph event.

        Args:
            index: Target step index within the calculated solution.
        """
        if not self.solution:
            return

        max_idx = len(self.solution) - 1
        self.solution_index = max(0, min(index, max_idx))

        nb_drones_moved: int = 0
        if self.solution_index > 0:
            for agent_index in range(self.graph.nb_drones):
                if (self.solution[self.solution_index - 1][agent_index]
                        != self.solution[self.solution_index][agent_index]):
                    nb_drones_moved += 1

        step_data = self.solution[self.solution_index]
        UIBus.get().graph_updated.emit(step_data)
        UIBus.get().info.emit(
            f"Steps: {self.solution_index} / {len(self.solution) - 1} "
            f"({nb_drones_moved} moved)"
        )

    def _on_timeout(self) -> None:
        """
        Advances the simulation by one step during auto-playback.
        """
        self._update_state(self.solution_index + 1)

    def keyPressEvent(self, event: Optional[QKeyEvent]) -> None:
        """
        Handles keyboard inputs for playback controls and exit.

        Args:
            event: Qt key event containing the pressed key info.
        """
        if event is None or not self.solution:
            return super().keyPressEvent(event)

        key = event.key()

        if key == Qt.Key.Key_D:
            self._update_state(self.solution_index + 1)
        elif key == Qt.Key.Key_A:
            self._update_state(self.solution_index - 1)
        elif key == Qt.Key.Key_R:
            self.timer.stop()
            self._update_state(0)
        elif key == Qt.Key.Key_Q:
            self.close()
        elif key == Qt.Key.Key_Space:
            if self.timer.isActive():
                self.timer.stop()
            else:
                self.timer.start(ANIMATION_DURATION)
        else:
            return super().keyPressEvent(event)
