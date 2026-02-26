import logging

from PyQt6.QtWidgets import QApplication

from flyin.arguments import Args
from flyin.exceptions.base import FlyInError
from flyin.io.file_loader import GraphFileLoader
from flyin.logging import LoggingSystem
from flyin.ui.window import GraphWindow

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    args = Args.parse_arguments()

    LoggingSystem.global_setup(args)

    # load data from file
    # validate data from file
    # create graph
    try:
        graph = GraphFileLoader.load(args.file)
    except FlyInError as e:
        logger.exception(e)
        exit(1)
    except Exception as e:
        logger.exception(e)
        exit(2)

    app = QApplication([])
    window = GraphWindow(graph)
    window.show()
    app.exec()
    # render graph
    # update graph (+render graph)
    # create solutions


if __name__ == "__main__":
    main()
