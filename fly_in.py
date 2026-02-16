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
    logging.config.dictConfig(LOGGING_CONFIG)

    logger.debug("Initial debug")


if __name__ == "__main__":
    main()
