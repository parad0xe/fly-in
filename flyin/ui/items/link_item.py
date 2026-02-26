from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainterPath, QPen
from PyQt6.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem

from flyin.models.hub import Hub, HubZoneType
from flyin.models.link import Link


class LinkItem(QGraphicsItemGroup):

    def __init__(self, hub_a: Hub, hub_b: Hub, link: Link) -> None:
        super().__init__()

        self.hub_a: Hub = hub_a
        self.hub_b: Hub = hub_b
        self.link: Link = link

        spacing = 520

        dx = (hub_b.x - hub_a.x) * spacing
        dy = (hub_b.y - hub_a.y) * spacing

        self.line = QGraphicsLineItem(0, 0, dx, dy)

        pen = QPen()
        pen.setWidth(10)
        pen.setColor(QColor(0, 0, 0, 50))

        if HubZoneType.PRIORITY in [hub_a.zone, hub_b.zone]:
            pen.setStyle(Qt.PenStyle.DashLine)
        elif HubZoneType.BLOCKED in [hub_a.zone, hub_b.zone]:
            pen.setStyle(Qt.PenStyle.DashDotDotLine)
        elif HubZoneType.RESTRICTED in [hub_a.zone, hub_b.zone]:
            pen.setStyle(Qt.PenStyle.DotLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)

        self.line.setPen(pen)

        self.addToGroup(self.line)

        self.setPos(hub_a.x * spacing, hub_a.y * spacing)

        self.setZValue(-1)

        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

    def shape(self) -> QPainterPath:
        return self.line.shape()
