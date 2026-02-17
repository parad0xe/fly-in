from __future__ import annotations

from pydantic import BaseModel, Field


class Link(BaseModel):
    """Represents a connection link with capacity constraints."""

    max_link_capacity: int = Field(default=1, ge=0)
