from PyQt6.QtGui import QColor


class UIHelper:
    """Provides utility functions for UI-related calculations."""

    @staticmethod
    def get_contrast_color(background_color: QColor) -> QColor:
        """
        Calculates and returns a contrasting text color (black or white).

        Args:
            background_color: The QColor of the background to evaluate.

        Returns:
            A QColor representing the best contrast (black or white).
        """
        brightness = (
            0.299 * background_color.red() + 0.587 * background_color.green() +
            0.114 * background_color.blue()
        ) / 255
        return QColor("black") if brightness > 0.5 else QColor("white")

    @staticmethod
    def get_outline_color(color: QColor, factor: int = 150) -> QColor:
        """
        Returns a darker or lighter version of a color for outlining.

        Args:
            color: The base QColor used to derive the outline color.
            factor: Intensity factor (smaller is darker, larger is lighter).

        Returns:
            A QColor that is lighter if the base is dark, else darker.
        """
        if color.lightness() < 50:
            return color.lighter(factor)
        return color.darker(factor)
