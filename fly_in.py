import logging

from srcs.arguments import Args
from srcs.logging import LoggingSystem

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    args = Args.parse_arguments()

    LoggingSystem.global_setup(
        root_logger=logger,
        args=args,
    )

    # graph = load_graph(args)

    logger.debug("Initial debug")
    logger.info("Info")


if __name__ == "__main__":
    main()
