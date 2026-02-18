from __future__ import annotations

import logging

from pydantic import ValidationError

from flyin.exceptions.loader import (
    LoaderEmptyFileError,
    LoaderError,
    LoaderFileNotFoundError,
    LoaderFilePermissionError,
    LoaderValidationError,
)
from flyin.io.parser import GraphParser
from flyin.models.graph import Graph

logger: logging.Logger = logging.getLogger(__name__)


class GraphFileLoader:
    @classmethod
    def load(cls, file: str) -> Graph:
        logger.debug(f"loading graph from '{file}'..")

        parser = GraphParser()

        try:
            try:
                with open(file) as f:
                    payload: dict | None = parser.parse_lines(f)
            except FileNotFoundError as e:
                raise LoaderFileNotFoundError() from e
            except PermissionError as e:
                raise LoaderFilePermissionError() from e
            except OSError as e:
                raise LoaderError() from e

            if payload is None:
                raise LoaderEmptyFileError()

            return Graph(**payload)
        except ValidationError as e:
            raise LoaderValidationError(e) from e
