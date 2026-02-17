from __future__ import annotations

import argparse
import textwrap
from dataclasses import dataclass

from typing_extensions import Self


@dataclass(frozen=True)
class Args:
    verbose: int
    file: str

    @classmethod
    def parse_arguments(cls) -> Self:
        parser = argparse.ArgumentParser(
            prog="FlyIn",
            description=textwrap.dedent(
                """
                Design a system that efficiently routes a fleet of drones
                from a central base (start) to a target location (end)
            """
            ).strip(),
            epilog="created by nlallema",
        )
        parser.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=0,
            help="increase output verbosity (e.g., -v, -vv, -vvv)",
        )
        parser.add_argument(
            "file",
            help="path to the input configuration file",
        )
        args = parser.parse_args()
        return cls(**vars(args))
