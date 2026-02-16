import logging

from srcs.arguments import Args
from srcs.logging import LoggingSystem

logger: logging.Logger = logging.getLogger(__name__)


class Graph:

    @classmethod
    def load_from_file(cls, file: str) -> None:
        print(file)


def main() -> None:
    args = Args.parse_arguments()

    LoggingSystem.global_setup(
        root_logger=logger,
        args=args,
    )

    # load data from file
    # validate data from file
    # create graph
    # render graph
    # update graph (+render graph)
    # create solutions

    # graph = Graph.load_from_file(args.file)

    logger.debug("Initial debug")
    logger.info("Info")


if __name__ == "__main__":
    main()
