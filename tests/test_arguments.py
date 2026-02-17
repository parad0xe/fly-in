import sys
from dataclasses import is_dataclass

import pytest

from flyin.arguments import Args


@pytest.mark.parametrize(
    "input_args, expected_file, expected_verbose",
    [
        (["prog", "config.json"], "config.json", 0),
        (["prog", "data.txt", "-v"], "data.txt", 1),
        (["prog", "test.yaml", "-vvv"], "test.yaml", 3),
    ],
)
def test_parse_arguments_success(
    monkeypatch, input_args, expected_file, expected_verbose
):
    """Test standard parsing for different verbosity levels."""
    monkeypatch.setattr(sys, "argv", input_args)

    args = Args.parse_arguments()

    assert isinstance(args, Args)
    assert is_dataclass(args)
    assert args.file == expected_file
    assert args.verbose == expected_verbose


def test_parse_arguments_missing_file(monkeypatch):
    """Verify that missing positional argument raises SystemExit."""
    monkeypatch.setattr(sys, "argv", ["prog"])

    with pytest.raises(SystemExit):
        Args.parse_arguments()


def test_parse_arguments_immutability():
    """Ensure the frozen dataclass property is respected."""
    args = Args(verbose=1, file="test.txt")
    with pytest.raises(AttributeError):
        args.verbose = 2  # type: ignore
