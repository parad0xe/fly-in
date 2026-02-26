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

        if hasattr(item, "get_details_html"):
            title, lines = item.get_details_html()  # type: ignore
            self.title_label.setText(title)
            self.content_label.setText(self._format_html_content(lines))
            self.show()
            self.adjustSize()
        else:
            self.hide()

        self.adjustSize()

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
