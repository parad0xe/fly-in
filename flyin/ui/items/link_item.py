import math

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItemGroup,
    QGraphicsLineItem,
)

from flyin.models.hub import Hub, HubZoneType
from flyin.models.link import Link
from flyin.ui.constants import (
    HUB_SPACING,
    LINK_RESTRICTED_MARKER_DISTANCE,
    LINK_RESTRICTED_MARKER_SIZE,
)


class LinkItem(QGraphicsItemGroup):

    def __init__(self, hub_a: Hub, hub_b: Hub, link: Link) -> None:
        super().__init__()

        self.hub_a: Hub = hub_a
        self.hub_b: Hub = hub_b
        self.link: Link = link

        self.dx = (hub_b.x - hub_a.x) * HUB_SPACING
        self.dy = (hub_b.y - hub_a.y) * HUB_SPACING

        self._setup_line()
        self._setup_markers()

        self.setPos(hub_a.x * HUB_SPACING, hub_a.y * HUB_SPACING)
        self.setZValue(-1)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

    def shape(self) -> QPainterPath:
        return self.line.shape()

    def get_details_html(self) -> tuple[str, list[str]]:
        lines = [
            f"Path: {self.hub_a.name} &#8596; {self.hub_b.name}",
            f"Drones: {self.link.drones}",
            f"Capacity: {self.link.max_link_capacity}",
        ]

        return "Link Details", lines

    def _setup_line(self) -> None:
        self.line = QGraphicsLineItem(0, 0, self.dx, self.dy)

        pen = QPen()
        pen.setWidth(10)
        pen.setColor(QColor(0, 0, 0, 50))

        zones = [self.hub_a.zone, self.hub_b.zone]

        if HubZoneType.BLOCKED in zones:
            pen.setStyle(Qt.PenStyle.DashDotDotLine)
        elif HubZoneType.RESTRICTED in zones:
            pen.setStyle(Qt.PenStyle.DotLine)
        elif HubZoneType.PRIORITY in zones:
            pen.setStyle(Qt.PenStyle.DashLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)

        self.line.setPen(pen)
        self.addToGroup(self.line)

    def _setup_markers(self) -> None:
        length = math.hypot(self.dx, self.dy)

        nx = self.dx / length
        ny = self.dy / length

        offset_x = nx * LINK_RESTRICTED_MARKER_DISTANCE
        offset_y = ny * LINK_RESTRICTED_MARKER_DISTANCE

        if self.hub_a.zone == HubZoneType.RESTRICTED:
            self._add_circle_marker(offset_x, offset_y)

        if self.hub_b.zone == HubZoneType.RESTRICTED:
            self._add_circle_marker(self.dx - offset_x, self.dy - offset_y)

    def _add_circle_marker(self, center_x: float, center_y: float) -> None:
        offset = LINK_RESTRICTED_MARKER_SIZE / 2
        circle = QGraphicsEllipseItem(
            center_x - offset,
            center_y - offset,
            LINK_RESTRICTED_MARKER_SIZE,
            LINK_RESTRICTED_MARKER_SIZE,
        )
        circle.setBrush(QBrush(QColor(0, 0, 0, 160)))
        circle.setPen(QPen(Qt.PenStyle.NoPen))
        self.addToGroup(circle)
