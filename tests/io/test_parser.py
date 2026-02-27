import pytest

from flyin.exceptions.parser import (
    ParserError,
    ParserMissingHubError,
    ParserMissingSeparatorError,
    ParserUnhandledKeyError,
)
from flyin.io.parser import GraphParser


@pytest.fixture
def parser() -> GraphParser:
    """Provide a fresh instance of GraphParser for each test."""
    return GraphParser()


def test_parser_handles_valid_input(parser):
    """Verify that a complete valid graph input is parsed correctly."""
    lines = [
        "nb_drones: 10",
        "start_hub: Alpha 0 0",
        "end_hub: Beta 10 10 [color=red]",
        "hub: Gamma -5 5",
        "connection: Alpha-Gamma [max_link_capacity=5]",
        "connection: Gamma-Beta",
    ]
    result = parser.parse_lines(lines)

    assert result["start_hub"].name == "Alpha"
    assert result["start_hub"].drones == 10
    assert result["end_hub"].color.value == "red"
    assert len(result["hubs"]) == 3
    assert len(result["links"]) == 2

    assert result["links"][0].max_link_capacity == 5
    assert len(result["hubs"][0].connections) == 1
    assert len(result["hubs"][1].connections) == 1
    assert len(result["hubs"][2].connections) == 2


def test_parser_enforces_nb_drones_precedence(parser):
    """Ensure any key before 'nb_drones' raises a ParserError."""
    lines = ["hub: A 0 0"]
    with pytest.raises(ParserError, match="must be defined first"):
        parser.parse_lines(lines)


def test_parser_validates_nb_drones_integer(parser):
    """Verify that non-integer drone counts trigger a ParserError."""
    with pytest.raises(ParserError, match="Invalid 'nb_drones' integer"):
        parser.parse_lines(["nb_drones: invalid"])


def test_parser_rejects_missing_separator(parser):
    """Ensure lines without the KV_SEP trigger the appropriate error."""
    with pytest.raises(ParserMissingSeparatorError):
        parser.parse_lines(["nb_drones 10"])


def test_parser_rejects_unhandled_keys(parser):
    """Verify that unknown keys trigger a ParserUnhandledKeyError."""
    lines = ["nb_drones: 1", "unknown_key: value"]
    with pytest.raises(ParserUnhandledKeyError):
        parser.parse_lines(lines)


def test_parser_validates_hub_format(parser):
    """Ensure malformed hub definitions raise a ParserError."""
    lines = ["nb_drones: 1", "hub: NameOnly"]
    with pytest.raises(ParserError, match="Invalid hub format"):
        parser.parse_lines(lines)


def test_parser_prevents_hub_names_with_hyphens(parser):
    """Verify that hub names containing hyphens are rejected."""
    lines = ["nb_drones: 1", "hub: Invalid-Name 0 0"]
    with pytest.raises(ParserError, match="Invalid hub format"):
        parser.parse_lines(lines)


def test_parser_handles_missing_hubs_in_connection(parser):
    """Ensure connections to undefined hubs raise ParserMissingHubError."""
    lines = ["nb_drones: 1", "hub: A 0 0", "connection: A-B"]
    with pytest.raises(ParserMissingHubError):
        parser.parse_lines(lines)


def test_parser_validates_metadata_syntax(parser):
    """Verify that metadata without separators raises a ParserError."""
    lines = ["nb_drones: 1", "hub: A 0 0 [invalid_meta]"]
    with pytest.raises(ParserError, match="Invalid metadata requires format"):
        parser.parse_lines(lines)


def test_parser_returns_none_for_empty_input(parser):
    """Confirm that empty or comment-only input returns None."""
    assert parser.parse_lines([]) is None
    assert parser.parse_lines(["# Comment", "  "]) is None
