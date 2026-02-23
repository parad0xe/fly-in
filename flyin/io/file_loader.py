from __future__ import annotations

import logging
from typing import Any

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
    """Utility class for loading and validating Graph data from files."""

    @classmethod
    def load(cls, file: str) -> Graph:
        """
        Loads a graph from a specified file path.

        Parses the file content and validates it against the Graph model.

        Args:
            file: Path to the source file containing graph data.

        Returns:
            A validated Graph instance.

        Raises:
            LoaderFileNotFoundError: If the specified file does not exist.
            LoaderFilePermissionError: If the file cannot be read.
            LoaderEmptyFileError: If the file contains no data.
            LoaderValidationError: If the data fails model validation.
            LoaderError: For any other OS-level input/output failures.
        """
        logger.debug(f"loading graph from '{file}'..")

        parser = GraphParser()

        try:
            try:
                with open(file) as f:
                    payload: dict[str, Any] | None = parser.parse_lines(f)
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
