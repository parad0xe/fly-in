from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QConicalGradient, QFont, QPen
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGraphicsEllipseItem,
    QGraphicsItemGroup,
    QGraphicsTextItem,
)

from flyin.models.hub import HubColorType
from flyin.ui.constants import (
    HUB_SIZE,
    SPACING,
)
from flyin.ui.helpers import UIHelper


class HubItem(QGraphicsItemGroup):

    def __init__(self, hub):
        super().__init__()
        self.hub = hub

        self._setup_shape()
        self._setup_labels()

        self.setPos(hub.x * SPACING, hub.y * SPACING)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

    def _setup_shape(self) -> None:
        if self.hub.color == HubColorType.RAINBOW:
            gradient = QConicalGradient(0, 0, 0)
            colors = [
                "red",
                "orange",
                "yellow",
                "green",
                "blue",
                "indigo",
                "red",
            ]
            for k, color in enumerate(colors):
                gradient.setColorAt(
                    float(k) / (len(colors) - 1), QColor(color)
                )
            self.brush = QBrush(gradient)
            self.text_color = QColor("white")
        else:
            bg_color = QColor(self.hub.color)
            self.brush = QBrush(bg_color)
            self.text_color = UIHelper.get_contrast_color(bg_color)

        self.circle = QGraphicsEllipseItem(
            -HUB_SIZE / 2, -HUB_SIZE / 2, HUB_SIZE, HUB_SIZE
        )
        self.circle.setBrush(self.brush)
        self.circle.setPen(QPen(Qt.PenStyle.NoPen))

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.circle.setGraphicsEffect(shadow)

        self.addToGroup(self.circle)

    def _setup_labels(self) -> None:
        font = QFont("Arial", 25, QFont.Weight.Bold)

        self.name_label = QGraphicsTextItem(self.hub.name)
        self.name_label.setFont(font)
        self.name_label.setDefaultTextColor(QColor("white"))
        rect_name = self.name_label.boundingRect()
        self.name_label.setPos(-rect_name.width() / 2, HUB_SIZE / 2 + 5)

        self.drone_label = QGraphicsTextItem(
            f"{self.hub.drones} / {self.hub.max_drones}"
        )
        self.drone_label.setFont(font)
        self.drone_label.setDefaultTextColor(self.text_color)
        rect_drone = self.drone_label.boundingRect()
        self.drone_label.setPos(
            -rect_drone.width() / 2, -rect_drone.height() / 2
        )

        self.addToGroup(self.name_label)
        self.addToGroup(self.drone_label)

    def get_details_html(self) -> tuple[str, list[str]]:
        lines = [
            f"Name: {self.hub.name}",
            f"Zone: {self.hub.zone.value}",
            f"Leaf: {self.hub.is_leaf}",
            f"Drones: {self.hub.drones}",
            f"Capacity: {self.hub.max_drones}",
        ]

        return "Hub Details", lines
