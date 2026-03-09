from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QGraphicsItemGroup,
    QGraphicsLineItem,
)

from flyin.models.hub import Hub, HubZoneType
from flyin.models.link import Link
from flyin.ui.constants import (
    HUB_SPACING,
    LINK_BASE_WIDTH,
    LINK_MAX_WIDTH,
    LINK_STYLE_MAP,
    LINK_Z_VALUE,
)


class LinkItem(QGraphicsItemGroup):
    """Visual representation of a graphical link between two hubs."""

    def __init__(self, hub_a: Hub, hub_b: Hub, link: Link) -> None:
        """
        Initialize the link graphical item.

        Args:
            hub_a: The starting hub instance.
            hub_b: The ending hub instance.
            link: The link data model instance.
        """
        super().__init__()

        self.hub_a: Hub = hub_a
        self.hub_b: Hub = hub_b
        self.link: Link = link

        self.dx = (hub_b.x - hub_a.x) * HUB_SPACING
        self.dy = (hub_b.y - hub_a.y) * HUB_SPACING

        self._setup_line()

        self.setPos(hub_a.x * HUB_SPACING, hub_a.y * HUB_SPACING)
        self.setZValue(LINK_Z_VALUE)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

    def shape(self) -> QPainterPath:
        """
        Return the exact shape of the link item.

        Returns:
            The collision shape of the graphical line.
        """
        return self.line.shape()

    def get_details_html(self) -> tuple[str, list[str]]:
        """
        Get the HTML formatted details of the link.

        Returns:
            Title string and a list of detail lines.
        """
        lines = [
            f"Path: {self.hub_a.name} &#8596; {self.hub_b.name}",
            f"Drones: {self.link.drones}",
            f"Capacity: {self.link.max_link_capacity}",
        ]

        return "Link Details", lines

    def _setup_line(self) -> None:
        """
        Configure and add the graphical line to the group.
        """
        self.line = QGraphicsLineItem(0, 0, self.dx, self.dy)

        pen = QPen()
        line_width = min(
            LINK_BASE_WIDTH * self.link.max_link_capacity + LINK_BASE_WIDTH,
            LINK_MAX_WIDTH,
        )
        pen.setWidth(line_width)
        pen.setColor(QColor(0, 0, 0, 50))

        dominant_zone = self._get_dominant_zone()
        pen.setStyle(LINK_STYLE_MAP.get(dominant_zone, Qt.PenStyle.SolidLine))

        self.line.setPen(pen)
        self.addToGroup(self.line)

    def _get_dominant_zone(self) -> HubZoneType:
        """
        Determine the most restrictive zone type.

        Returns:
            The dominant zone for styling the link.
        """
        zones = {self.hub_a.zone, self.hub_b.zone}

        for zone_type in [
                HubZoneType.BLOCKED,
                HubZoneType.RESTRICTED,
                HubZoneType.PRIORITY,
        ]:
            if zone_type in zones:
                return zone_type

        return HubZoneType.NORMAL
