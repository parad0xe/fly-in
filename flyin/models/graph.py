from __future__ import annotations

import logging

from pydantic import BaseModel

from flyin.exceptions.graph import (
    GraphEmptyFileError,
    GraphFileNotFoundError,
    GraphFilePermissionError,
    GraphLoadError,
    GraphParseError,
)
from flyin.models.hub import Hub
from flyin.models.link import Link

logger: logging.Logger = logging.getLogger(__name__)


class Graph(BaseModel):
    hubs: list[Hub]
    links: list[Link]
    start_hub: Hub
    end_hub: Hub


class GraphLoader:
    KV_SEPARATOR = ":"
    METADATA_SEPARATOR = "="

    @classmethod
    def load(cls, file: str) -> Graph:
        logger.debug(f"loading graph from file.. {file}")

        loader = cls()
        graph_data = loader._parse_file(file)

        return Graph(**graph_data)

    def _parse_file(self, file: str) -> dict:
        self.nb_drones: str | None = None
        self.hubs: list[Hub] = []
        self.links: list[Link] = []
        self.start_hub: Hub
        self.end_hub: Hub

        self.line_index: int = 0
        self.nb_drones_loaded: bool = False

        try:
            with open(file) as f:
                for line in f:
                    self.line_index += 1
                    line = line.strip()

                    if line == "":
                        continue

                    if line.startswith("#"):
                        continue
                    try:
                        self._parse_line(line)
                    except GraphParseError as e:
                        raise e
        except FileNotFoundError as e:
            raise GraphFileNotFoundError() from e
        except PermissionError as e:
            raise GraphFilePermissionError() from e
        except OSError as e:
            raise GraphLoadError() from e

        if self.line_index == 0:
            raise GraphEmptyFileError()

        return {
            "hubs": self.hubs,
            "links": self.links,
            "start_hub": self.start_hub,
            "end_hub": self.end_hub,
        }

    def _parse_line(self, line: str) -> None:
        if self.KV_SEPARATOR not in line:
            raise GraphParseError(
                self.line_index, f"Missing separator '{self.KV_SEPARATOR}'"
            )

        key, value = [s.strip() for s in line.split(self.KV_SEPARATOR, 1)]
        logger.debug(f"parse: key=<{key}> value=<{value}>")

        if not self.nb_drones_loaded and key != "nb_drones":
            raise GraphParseError(
                self.line_index,
                "Key 'nb_drones' must be declared at the first line",
            )

        match key:
            case "nb_drones":
                self.nb_drones = value
                self.nb_drones_loaded = True
            case "start_hub":
                self._parse_hub(value)
            case "hub":
                self._parse_hub(value)
            case "end_hub":
                self._parse_hub(value)
            case _:
                raise GraphParseError(
                    self.line_index,
                    f"Unknow key: '{key}'",
                )

    def _parse_hub(self, value) -> Hub:
        parts: list[str] = value.split()

        if len(parts) < 3:
            raise GraphParseError(self.line_index, "Hub requires: name x y")

        payload: dict = {
            "name": parts[0],
            "x": parts[1],
            "y": parts[2],
        }

        for metadata in list(map(lambda x: x.strip("[]"), parts[3:])):
            if self.METADATA_SEPARATOR in metadata:
                metadata_key, metadata_value = metadata.split(
                    self.METADATA_SEPARATOR, 1
                )
                payload[metadata_key] = metadata_value
            else:
                raise GraphParseError(
                    self.line_index,
                    "Metadata requires: [key1=value key2=value2]",
                )

        hub = Hub.model_validate(payload)
        logger.debug(f"hub created: Hub({hub})")
        return hub
