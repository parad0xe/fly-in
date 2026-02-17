from __future__ import annotations

import logging
import logging.config

from flyin.arguments import Args


class LoggingSystem:
    CONFIG = {
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
                "level": logging.DEBUG,
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": logging.ERROR,
            },
        },
    }

    @classmethod
    def global_setup(
        cls: type[LoggingSystem],
        args: Args,
    ) -> None:
        level: int = cls._get_level(args.verbose)

        logging.config.dictConfig(LoggingSystem.CONFIG)

        loggers = [
            logging.getLogger(name) for name in logging.root.manager.loggerDict
        ]
        for logger in loggers:
            logger.setLevel(level)

    @staticmethod
    def _get_level(verbose: int) -> int:
        match verbose:
            case 0:
                return logging.ERROR
            case 1:
                return logging.INFO
            case _:
                return logging.DEBUG
