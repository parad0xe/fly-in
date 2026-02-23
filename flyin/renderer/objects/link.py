from arcade.shape_list import (
    Shape,
    create_line,
)
from arcade.types import RGBA255

from flyin.models.hub import Hub
from flyin.renderer.constants import (
    RENDERER_DISTANCE_X,
    RENDERER_DISTANCE_Y,
)


class LinkShape:
    @staticmethod
    def connect_hub(hub_a: Hub, hub_b: Hub, color: RGBA255) -> Shape:
        return create_line(
            RENDERER_DISTANCE_X * hub_a.x,
            RENDERER_DISTANCE_Y * hub_a.y,
            RENDERER_DISTANCE_X * hub_b.x,
            RENDERER_DISTANCE_Y * hub_b.y,
            color,
            5,
        )
