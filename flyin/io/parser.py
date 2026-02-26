from __future__ import annotations

import logging
import re
from typing import Any, Callable, Iterable

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
    """
    Parser for converting raw line-based input into Graph components.

    Attributes:
        KV_SEP: Separator between key and value (default ':').
        META_SEP: Separator for metadata pairs (default '=').
        HUB_PATTERN: Regex for parsing hub definitions.
        CONNECTION_PATTERN: Regex for parsing link definitions.
    """

    KV_SEP = ":"
    META_SEP = "="

    HUB_PATTERN = re.compile(
        r"^\s*([a-z][\w-]*)\s*(-?\d+)\s*(-?\d+)\s*(?:\[\s*(.*)\s*\])?\s*$",
        re.I,
    )
    CONNECTION_PATTERN = re.compile(
        r"^\s*([a-z][\w]*)-([a-z][\w]*)\s*(?:\[\s*(.*)\s*\])?\s*$", re.I
    )

    def parse_lines(self, lines: Iterable[str]) -> dict[str, Any] | None:
        """
        Parses lines into graph data.

        Args:
            lines: Iterable of strings to be parsed.

        Returns:
            Dictionary of graph components or None if no hubs found.

        Raises:
            ParserMissingSeparatorError: If ':' is missing in a line.
            ParserUnhandledKeyError: If a key has no associated handler.
            ParserError: If 'nb_drones' is not first or data is invalid.
        """
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
        """
        Processes and stores the total number of drones.

        Args:
            lineno: Current line number for error reporting.
            data: Raw string value representing the drone count.

        Raises:
            ParserError: If the data cannot be converted to an integer.
        """
        try:
            nb_drones: int = int(data)
        except ValueError as e:
            raise ParserError(
                lineno, f"Invalid 'nb_drones' integer: '{data}'."
            ) from e
        self.nb_drones = nb_drones
        logger.info(f"Number of drones set to: {self.nb_drones}")

    def _handle_connection(self, lineno: int, data: str) -> None:
        """
        Handles hub connection logic and updates hub adjacency.

        Args:
            lineno: Current line number for error reporting.
            data: Raw string representing the connection and metadata.
        """
        hub_a, hub_b, link = self._parse_connection(lineno, data)
        hub_a.connect_both(hub_b, link)
        self.links.append(link)
        logger.debug(
            f"Connected hubs: '{hub_a.name}' <-> '{hub_b.name}' "
            f"(capacity: {link.max_link_capacity})"
        )

    def _handle_hub(self, lineno: int, data: str, hub_type: str) -> None:
        """
        Creates a hub and assigns it as start, end, or normal.

        Args:
            lineno: Current line number for error reporting.
            data: Raw string containing name, coordinates, and metadata.
            hub_type: Role of the hub ('start', 'end', or 'normal').
        """
        payload = self._parse_hub_payload(lineno, data)

        if hub_type == "start":
            payload["drones"] = self.nb_drones
            if "max_drones" not in payload:
                payload["max_drones"] = self.nb_drones

        hub = Hub(**payload)
        logger.debug(f"Hub ({hub_type}) '{hub.name}' created.")

        if hub_type == "start":
            logger.info(f"Start hub defined: '{hub.name}'")
            self.start_hub = hub
        elif hub_type == "end":
            logger.info(f"End hub defined: '{hub.name}'")
            self.end_hub = hub

        self.hubs[hub.name] = hub

    def _parse_connection(self, lineno: int,
                          data: str) -> tuple[Hub, Hub, Link]:
        """
        Extracts connection details and validates hub existence.

        Args:
            lineno: Current line number for error reporting.
            data: Raw string to match against CONNECTION_PATTERN.

        Returns:
            A tuple containing (source_hub, target_hub, created_link).

        Raises:
            ParserError: If the format is invalid.
            ParserMissingHubError: If a referenced hub is not defined.
        """
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

        payload: dict[str, Any] = {}

        if metadata_str:
            metadata = self._parse_metadata(lineno, metadata_str)
            payload = {**metadata, **payload}

        hub_a = self.hubs[name_a]
        hub_b = self.hubs[name_b]
        link = Link(**payload)

        return hub_a, hub_b, link

    def _parse_hub_payload(self, lineno: int, data: str) -> dict[str, Any]:
        """
        Parses raw hub data into a dictionary for instantiation.

        Args:
            lineno: Current line number for error reporting.
            data: Raw string to match against HUB_PATTERN.

        Returns:
            A dictionary containing 'name', 'x', 'y', and metadata.

        Raises:
            ParserError: If the format is invalid
                or name contains invalid char.
        """
        if match := self.HUB_PATTERN.match(data):
            name, x, y, metadata_str = match.groups()
        else:
            raise ParserError(lineno, "Invalid hub format: 'name x y'.")

        if "-" in name:
            raise ParserError(
                lineno, f"Invalid hub name <{name}>: invalid char <->."
            )

        payload: dict[str, Any] = {"name": name, "x": x, "y": y}

        if metadata_str:
            metadata = self._parse_metadata(lineno, metadata_str)
            payload = {**metadata, **payload}

        return payload

    def _parse_metadata(self, lineno: int,
                        metadata_str: str) -> dict[str, Any]:
        """
        Converts metadata string [k=v ...] into a dictionary.

        Args:
            lineno: Current line number for error reporting.
            metadata_str: Raw string containing key-value pairs.

        Returns:
            A dictionary of extracted metadata.

        Raises:
            ParserError: If a pair does not contain the key-value separator.
        """
        metadata: dict[str, Any] = {}
        for part in metadata_str.split():
            if self.META_SEP not in part:
                raise ParserError(
                    lineno,
                    "Invalid metadata requires format: [key1=value ...].",
                )
            metadata_key, metadata_value = part.split(self.META_SEP, 1)
            metadata[metadata_key] = metadata_value
        return metadata

    def _build_graph_payload(self) -> dict[str, Any]:
        """
        Aggregates all parsed components into a final payload.

        Returns:
            A dictionary structured for Graph model instantiation.
        """
        return {
            "hubs": list(self.hubs.values()),
            "links": self.links,
            "start_hub": self.start_hub,
            "end_hub": self.end_hub,
        }
