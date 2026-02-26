from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsItem,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from flyin.ui.items.hub_item import HubItem
from flyin.ui.items.link_item import LinkItem


class MapInfoOverlay(QFrame):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.setStyleSheet(
            """
            QFrame {
                background-color: rgba(30, 30, 30, 200);
                color: white;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 50);
                padding: 2px;
            }
            QLabel { border: none; background: transparent; }
            """
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.title_label = QLabel("DETAILS")
        self.title_label.setStyleSheet(
            """
            font-weight: bold;
            font-size: 13px;
            color: #C46210;
            letter-spacing: 1px;
            border-radius: 0px;
            border-bottom: 1px solid rgba(196, 98, 16, 50);
            padding-bottom: 4px;
            """
        )

        self.content_label = QLabel("No selection")
        self.content_label.setStyleSheet(
            """
            font-size: 15px;
            """
        )
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.title_label)
        layout.addWidget(self.content_label)

        self.setFixedWidth(250)
        self.hide()

    def set_item(self, item: Optional[QGraphicsItem] = None) -> None:
        if item is None:
            self.hide()
            return

        if isinstance(item, HubItem):
            self.title_label.setText("HUB DETAILS")
            self._set_hub_item(item)
            self.show()
        elif isinstance(item, LinkItem):
            self.title_label.setText("LINK DETAILS")
            self._set_link_item(item)
            self.show()
        else:
            self.hide()

        self.adjustSize()

    def _set_hub_item(self, item: HubItem) -> None:
        lines = [
            f"Name: {item.hub.name}",
            f"Zone: {item.hub.zone.value}",
            f"Leaf: {item.hub.is_leaf}",
            f"Drones: {item.hub.drones}",
            f"Capacity: {item.hub.max_drones}",
        ]
        self.content_label.setText(self._format_html_content(lines))

    def _set_link_item(self, item: LinkItem) -> None:
        lines = [
            f"Path: {item.hub_a.name} &#8596; {item.hub_b.name}",
            f"Drones: {item.link.drones}",
            f"Capacity: {item.link.max_link_capacity}",
        ]
        self.content_label.setText(self._format_html_content(lines))

    def _format_html_content(self, lines: list[str]) -> str:
        style = """
            <style>
                div {
                    margin-bottom: 8px;
                }
            </style>
        """
        body = "".join(f"<div>{line}</div>" for line in lines)
        return style + body
