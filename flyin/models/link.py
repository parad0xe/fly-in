from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Link(BaseModel):
    """Represents a connection link with capacity constraints."""

    model_config = ConfigDict(extra="forbid")

    drones: int = Field(default=0, ge=0)
    max_link_capacity: int = Field(default=1, ge=0, frozen=True)
