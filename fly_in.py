import logging

from PyQt6.QtWidgets import QApplication

from flyin.arguments import Args
from flyin.exceptions.base import FlyInError
from flyin.io.file_loader import GraphFileLoader
from flyin.logging import LoggingSystem
from flyin.models.hub import Hub
from flyin.solver.lacam import Lacam
from flyin.ui.window import GraphWindow

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    args = Args.parse_arguments()

    LoggingSystem.global_setup(args)

    try:
        graph = GraphFileLoader.load(args.file)
    except FlyInError as e:
        logger.exception(e)
        exit(1)
    except Exception as e:
        logger.exception(e)
        exit(2)

    is_special_case = args.file.endswith("00_custom-tunnel.txt")

    if is_special_case:
        config_start: tuple[Hub, ...] = (
            graph.hubs[5],
            graph.hubs[4],
            graph.hubs[3],
            graph.hubs[1],
        )
        config_end: tuple[Hub, ...] = (
            graph.hubs[2],
            graph.hubs[3],
            graph.hubs[4],
            graph.hubs[5],
        )
    else:
        config_start = (graph.start_hub,) * graph.nb_drones
        config_end = (graph.end_hub,) * graph.nb_drones

    solution = Lacam.solve(
        graph=graph,
        config_start=config_start,
        config_end=config_end,
        max_duration=5000 if is_special_case else 400,
    )

    app = QApplication([])
    window = GraphWindow(graph, solution)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
