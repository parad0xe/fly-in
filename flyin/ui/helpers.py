from PyQt6.QtGui import QColor


class UIHelper:

    @staticmethod
    def get_contrast_color(background_color: QColor) -> QColor:
        brightness = (
            0.299 * background_color.red() + 0.587 * background_color.green() +
            0.114 * background_color.blue()
        ) / 255
        return QColor("black") if brightness > 0.5 else QColor("white")
