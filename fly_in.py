import argparse
import logging
import logging.config
import os

from dotenv import load_dotenv

load_dotenv()

env = os.getenv("ENV", "").lower()

logger: logging.Logger = logging.getLogger(__name__)
log_level: int = logging.INFO if env == "production" else logging.DEBUG

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": (
                "%(asctime)s [%(levelname)s] %(name)s "
                "(%(filename)s:%(lineno)d): %(message)s"
            ),
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": log_level,
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": log_level,
        },
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="FlyIn",
        description="Design a system that efficiently routes a fleet of \
                drones from a central base (start) to a target location (end)",
        epilog="created by nlallema",
    )

    args = parser.parse_args()
    print(args)

    logging.config.dictConfig(LOGGING_CONFIG)

    logger.debug("Initial debug")


if __name__ == "__main__":
    main()
