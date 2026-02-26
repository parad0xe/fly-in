from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QConicalGradient, QFont, QPen
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGraphicsEllipseItem,
    QGraphicsItemGroup,
    QGraphicsTextItem,
)

from flyin.models.hub import HubColorType


class HubItem(QGraphicsItemGroup):

    def __init__(self, hub, size: int = 120, margin: int = 400):
        super().__init__()
        self.hub = hub

        bg_color = QColor("black")
        brush = QBrush()

        if hub.color == HubColorType.RAINBOW:
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

            brush = QBrush(gradient)
            text_color = QColor("white")
        else:
            bg_color = QColor(hub.color)
            brush = QBrush(bg_color)
            text_color = self.get_contrast_color(bg_color)

        self.circle = QGraphicsEllipseItem(-size / 2, -size / 2, size, size)
        self.circle.setBrush(brush)
        self.circle.setPen(QPen(Qt.PenStyle.NoPen))

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.circle.setGraphicsEffect(shadow)

        font = QFont("Arial", 25, QFont.Weight.Bold)

        self.name_label = QGraphicsTextItem(hub.name)
        self.name_label.setFont(font)
        self.name_label.setDefaultTextColor(QColor("white"))

        self.drone_label = QGraphicsTextItem(
            f"{hub.drones} / {hub.max_drones}"
        )
        self.drone_label.setFont(font)
        self.drone_label.setDefaultTextColor(text_color)

        rect_name = self.name_label.boundingRect()
        self.name_label.setPos(-rect_name.width() / 2, size / 2 + 5)

        rect_drone = self.drone_label.boundingRect()
        self.drone_label.setPos(
            -rect_drone.width() / 2, -rect_drone.height() / 2
        )

        self.addToGroup(self.circle)
        self.addToGroup(self.name_label)
        self.addToGroup(self.drone_label)

        spacing = size + margin
        self.setPos(hub.x * spacing, hub.y * spacing)

        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

    def get_contrast_color(self, background_color: QColor) -> QColor:
        brightness = (
            0.299 * background_color.red() + 0.587 * background_color.green() +
            0.114 * background_color.blue()
        ) / 255
        return QColor("black") if brightness > 0.5 else QColor("white")
