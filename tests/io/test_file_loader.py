from unittest.mock import patch

import pytest

from flyin.exceptions.loader import (
    LoaderEmptyFileError,
    LoaderError,
    LoaderFileNotFoundError,
    LoaderFilePermissionError,
    LoaderValidationError,
)
from flyin.io.file_loader import GraphFileLoader
from flyin.models.graph import Graph


def test_load_file_not_found():
    """Verify that a missing file raises LoaderFileNotFoundError."""
    with pytest.raises(LoaderFileNotFoundError):
        GraphFileLoader.load("non_existent.txt")


def test_load_permission_denied():
    """Ensure that restricted file access raises LoaderFilePermissionError."""
    with patch("builtins.open", side_effect=PermissionError):
        with pytest.raises(LoaderFilePermissionError):
            GraphFileLoader.load("restricted.txt")


def test_load_os_error():
    """Verify that generic system-level IO errors raise LoaderError."""
    with patch("builtins.open", side_effect=OSError):
        with pytest.raises(LoaderError):
            GraphFileLoader.load("system_error.txt")


def test_load_empty_file(tmp_path):
    """Confirm that empty files trigger a LoaderEmptyFileError."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")
    with pytest.raises(LoaderEmptyFileError):
        GraphFileLoader.load(str(empty_file))


def test_load_validation_error(tmp_path):
    """
    Ensure that invalid graph data structures raise LoaderValidationError.
    """
    invalid_file = tmp_path / "invalid.txt"
    content = "nb_drones: 1\nstart_hub: A 0 0"
    invalid_file.write_text(content)
    with patch("flyin.io.parser.GraphParser.parse_lines", return_value={}):
        with pytest.raises(LoaderValidationError):
            GraphFileLoader.load(str(invalid_file))

    content = "nb_drones: 1\nend_hub: A 0 0"
    invalid_file.write_text(content)
    with patch("flyin.io.parser.GraphParser.parse_lines", return_value={}):
        with pytest.raises(LoaderValidationError):
            GraphFileLoader.load(str(invalid_file))

    content = "nb_drones: 1"
    invalid_file.write_text(content)
    with patch("flyin.io.parser.GraphParser.parse_lines", return_value={}):
        with pytest.raises(LoaderValidationError):
            GraphFileLoader.load(str(invalid_file))


def test_load_success(tmp_path):
    """Verify that a valid configuration file returns a Graph instance."""
    valid_file = tmp_path / "valid.txt"
    content = "nb_drones: 1\nstart_hub: A 0 0\nend_hub: B 1 1"
    valid_file.write_text(content)

    graph = GraphFileLoader.load(str(valid_file))
    assert isinstance(graph, Graph)
    assert len(graph.hubs) == 2
    assert len(graph.links) == 0
