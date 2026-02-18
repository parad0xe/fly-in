from __future__ import annotations

import logging
import re
from typing import Callable, Iterable

from flyin.exceptions.parser import (
    ParserError,
    ParserMissingHubError,
    ParserMissingSeparatorError,
    ParserUnhandledKeyError,
)
from flyin.models.hub import Hub
from flyin.models.link import Link

logger: logging.Logger = logging.getLogger(__name__)


class GraphParser:
    KV_SEP = ":"
    META_SEP = "="

    HUB_PATTERN = re.compile(
        r"^\s*([a-z][\w-]*)\s*(-?\d+)\s*(-?\d+)\s*(?:\[\s*(.*)\s*\])?\s*$",
        re.I,
    )
    CONNECTION_PATTERN = re.compile(
        r"^\s*([a-z][\w]*)-([a-z][\w]*)\s*(?:\[\s*(.*)\s*\])?\s*$", re.I
    )

    def parse_lines(self, lines: Iterable[str]) -> dict | None:
        logger.info("Starting graph parsing process.")

        self.nb_drones: int | None = None
        self.hubs: dict[str, Hub] = {}
        self.links: list[Link] = []
        self.start_hub: Hub
        self.end_hub: Hub

        self.handlers: dict[str, Callable[[int, str], None]] = {
            "nb_drones": self._handle_nb_drones,
            "hub": lambda ln, d: self._handle_hub(ln, d, "normal"),
            "start_hub": lambda ln, d: self._handle_hub(ln, d, "start"),
            "end_hub": lambda ln, d: self._handle_hub(ln, d, "end"),
            "connection": self._handle_connection,
        }

        for ln, line in enumerate(lines):
            lineno = ln + 1
            line = line.strip()

            if line == "" or line.startswith("#"):
                continue

            if self.KV_SEP not in line:
                raise ParserMissingSeparatorError(lineno, self.KV_SEP)

            key, value = [s.strip() for s in line.split(self.KV_SEP, 1)]
            logger.debug(f"Line {lineno}: Processing <{line}>")

            if not self.nb_drones and key != "nb_drones":
                raise ParserError(
                    lineno, "The 'nb_drones' key must be defined first."
                )

            handler = self.handlers.get(key, None)
            if handler is not None:
                handler(lineno, value)
            else:
                raise ParserUnhandledKeyError(lineno, key)

        if len(self.hubs) == 0:
            return None

        return self._build_graph_payload()

    def _handle_nb_drones(self, lineno: int, data: str) -> None:
        try:
            nb_drones: int = int(data)
        except ValueError as e:
            raise ParserError(
                lineno, f"Invalid 'nb_drones' integer: '{data}'."
            ) from e
        self.nb_drones = nb_drones
        logger.info(f"Number of drones set to: {self.nb_drones}")

    def _handle_connection(self, lineno: int, data: str) -> None:
        hub_a, hub_b, link = self._parse_connection(lineno, data)
        hub_a.connect_both(hub_b, link)
        self.links.append(link)
        logger.debug(
            f"Connected hubs: '{hub_a.name}' <-> '{hub_b.name}' "
            f"(capacity: {link.max_link_capacity})"
        )

    def _handle_hub(self, lineno: int, data: str, hub_type: str) -> None:
        payload = self._parse_hub_payload(lineno, data)

        if hub_type == "start":
            payload["drones"] = self.nb_drones

        hub = Hub(**payload)
        logger.debug(f"Hub ({hub_type}) '{hub.name}' created.")

        if hub_type == "start":
            logger.info(f"Start hub defined: '{hub.name}'")
            self.start_hub = hub
        elif hub_type == "end":
            logger.info(f"End hub defined: '{hub.name}'")
            self.end_hub = hub

        self.hubs[hub.name] = hub

    def _parse_connection(
        self, lineno: int, data: str
    ) -> tuple[Hub, Hub, Link]:
        if match := self.CONNECTION_PATTERN.match(data):
            name_a, name_b, metadata_str = match.groups()
        else:
            raise ParserError(
                lineno, "Invalid connection format: '<name1>-<name2>'."
            )

        if name_a not in self.hubs:
            raise ParserMissingHubError(lineno, name_a)
        if name_b not in self.hubs:
            raise ParserMissingHubError(lineno, name_b)

        payload: dict = {}

        if metadata_str:
            metadata = self._parse_metadata(lineno, metadata_str)
            payload = {**metadata, **payload}

        hub_a = self.hubs[name_a]
        hub_b = self.hubs[name_b]
        link = Link(**payload)

        return hub_a, hub_b, link

    def _parse_hub_payload(self, lineno: int, data: str) -> dict:
        if match := self.HUB_PATTERN.match(data):
            name, x, y, metadata_str = match.groups()
        else:
            raise ParserError(lineno, "Invalid hub format: 'name x y'.")

        if "-" in name:
            raise ParserError(
                lineno, f"Invalid hub name <{name}>: invalid char <->."
            )

        payload: dict = {"name": name, "x": x, "y": y}

        if metadata_str:
            metadata = self._parse_metadata(lineno, metadata_str)
            payload = {**metadata, **payload}

        return payload

    def _parse_metadata(self, lineno: int, metadata_str: str) -> dict:
        metadata: dict = {}
        for part in metadata_str.split():
            if self.META_SEP not in part:
                raise ParserError(
                    lineno,
                    "Invalid metadata requires format: [key1=value ...].",
                )
            metadata_key, metadata_value = part.split(self.META_SEP, 1)
            metadata[metadata_key] = metadata_value
        return metadata

    def _build_graph_payload(self) -> dict:
        return {
            "hubs": list(self.hubs.values()),
            "links": self.links,
            "start_hub": self.start_hub,
            "end_hub": self.end_hub,
        }
