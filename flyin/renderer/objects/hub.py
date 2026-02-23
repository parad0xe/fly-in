from typing import Any

import arcade
from arcade.shape_list import (
    Shape,
    create_ellipse_filled,
    create_polygon,
    create_rectangle_filled,
)
from arcade.types import RGBA255

from flyin.models.hub import Hub, HubColorType, HubZoneType
from flyin.renderer.constants import RENDERER_DISTANCE_X, RENDERER_DISTANCE_Y


class HubColorAdapter:
    @staticmethod
    def to_arcade(color: HubColorType | None) -> RGBA255:
        if color is not None:
            if hasattr(arcade.color, color.name):
                v: RGBA255 = getattr(arcade.color, color.name)
                return v

            if color == HubColorType.RAINBOW:
                return arcade.color.DAFFODIL

        return arcade.color.GRAY


class HubShape:
    @staticmethod
    def create(hub: Hub, size: int = 50) -> Shape:
        if hub.zone == HubZoneType.BLOCKED:
            return Circle.create(
                hub.x,
                hub.y,
                HubColorAdapter.to_arcade(hub.color),
                size,
            )
        elif hub.zone == HubZoneType.RESTRICTED:
            return Diamond.create(
                hub.x,
                hub.y,
                size,
                size,
                HubColorAdapter.to_arcade(hub.color),
            )
        elif hub.zone == HubZoneType.PRIORITY:
            return Triangle.create(
                RENDERER_DISTANCE_X * hub.x,
                RENDERER_DISTANCE_Y * hub.y,
                HubColorAdapter.to_arcade(hub.color),
                size * 3,
            )
        elif hub.zone == HubZoneType.NORMAL:
            return Circle.create(
                hub.x,
                hub.y,
                HubColorAdapter.to_arcade(hub.color),
                size,
            )

        return Triangle.create(
            RENDERER_DISTANCE_X * hub.x,
            RENDERER_DISTANCE_Y * hub.y,
            arcade.color.AQUAMARINE,
            size * 3,
        )


class Diamond:
    @staticmethod
    def create(x: int, y: int, size_x: int, size_y: int, color: Any) -> Shape:
        return create_rectangle_filled(
            RENDERER_DISTANCE_X * x,
            RENDERER_DISTANCE_Y * y,
            size_x * 5,
            size_y * 5,
            color,
            tilt_angle=45,
        )


class Circle:
    @staticmethod
    def create(x: int, y: int, color: Any, size: int = 50) -> Shape:
        return create_ellipse_filled(
            RENDERER_DISTANCE_X * x,
            RENDERER_DISTANCE_Y * y,
            size * 5,
            size * 5,
            color,
        )


class Triangle:
    @staticmethod
    def create(x: int, y: int, color: Any, size: int = 50) -> Shape:
        points = [
            (x, y + size),
            (x - size, y - size),
            (x + size, y - size),
        ]

        return create_polygon(points, color)
