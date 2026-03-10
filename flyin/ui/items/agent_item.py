import math
import random

from PyQt6.QtCore import QEasingCurve, QPointF, Qt, QVariantAnimation
from PyQt6.QtGui import QBrush, QColor, QFont, QPen
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItemGroup,
    QGraphicsTextItem,
)

from flyin.models.hub import Hub
from flyin.ui.constants import (
    AGENT_SIZE,
    ANIMATION_DURATION,
    HUB_SIZE,
    HUB_SPACING,
)
from flyin.ui.helpers import UIHelper


class AgentItem(QGraphicsItemGroup):
    """Visual representation of an active drone agent."""

    def __init__(self, hub: Hub, uid: int) -> None:
        """
        Initializes the agent at a specific hub with random colors.

        Args:
            hub: The initial Hub object where the agent spawns.
            uid: Unique identifier for the agent.
        """
        super().__init__()

        self.current_hub: Hub = hub

        self.grid_x = hub.x
        self.grid_y = hub.y
        self.uid = uid

        self.color = QColor(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

        self._setup_shape()
        self._setup_labels()

        angle_deg = self.grid_x + self.uid * self.current_hub.drones
        angle_rad = math.radians(angle_deg)
        radius = (HUB_SIZE / 2.0) + 20.0

        self.setPos(
            self.grid_x * HUB_SPACING + math.cos(angle_rad) * radius,
            self.grid_y * HUB_SPACING + math.sin(angle_rad) * radius,
        )

        self.setZValue(1)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

        self.anim = QVariantAnimation()
        self.anim.setDuration(ANIMATION_DURATION)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.valueChanged.connect(self._on_anim_step)

    def _on_anim_step(self, pos: QPointF) -> None:
        """
        Updates the item position during the animation sequence.

        Args:
            pos: The new interpolated position from the animation.
        """
        self.setPos(pos)

    def _setup_shape(self) -> None:
        """Draws the main circular body of the agent."""
        self.circle = QGraphicsEllipseItem(
            -AGENT_SIZE / 2, -AGENT_SIZE / 2, AGENT_SIZE, AGENT_SIZE
        )

        self.circle.setBrush(QBrush(self.color))

        pen = QPen(QColor("black"))
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        self.circle.setPen(pen)

        self.addToGroup(self.circle)

    def _setup_labels(self) -> None:
        """Creates the inner text label showing the agent's UID."""
        font = QFont("Arial", 12, QFont.Weight.Bold)

        self.index_label = QGraphicsTextItem(str(self.uid))
        self.index_label.setFont(font)

        text_color = UIHelper.get_contrast_color(self.color)
        self.index_label.setDefaultTextColor(text_color)

        rect_index = self.index_label.boundingRect()
        self.index_label.setPos(
            -rect_index.width() / 2, -rect_index.height() / 2
        )

        self.addToGroup(self.index_label)

    def update_hub(self, hub: Hub) -> None:
        """
        Moves the agent to a new hub and triggers the animation.

        Args:
            hub: The destination Hub object for the agent.
        """
        self.current_hub.drones -= 1
        self.current_hub = hub
        self.current_hub.drones += 1

        self.grid_x = hub.x
        self.grid_y = hub.y

        angle_deg = self.grid_x + self.uid * self.current_hub.drones
        angle_rad = math.radians(angle_deg)
        radius = (HUB_SIZE / 2.0) + 20.0

        end_pos = QPointF(
            self.grid_x * HUB_SPACING + math.cos(angle_rad) * radius,
            self.grid_y * HUB_SPACING + math.sin(angle_rad) * radius,
        )

        self.anim.stop()

        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(end_pos)

        self.anim.start()

    def get_details_html(self) -> tuple[str, list[str]]:
        """
        Provides formatted HTML details for the overlay.

        Returns:
            A tuple containing the title and a list of detail lines.
        """
        lines = [
            f"Agent UID: {self.uid}",
            f"Position: ({self.grid_x}, {self.grid_y})",
        ]
        return "Agent Details", lines
