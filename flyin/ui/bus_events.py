from PyQt6.QtCore import QObject, pyqtSignal


class _BusEvents(QObject):
    """Internal event bus defining global application signals."""

    graph_updated = pyqtSignal(tuple)
    hub_updated = pyqtSignal()
    info = pyqtSignal(str)


_bus = _BusEvents()


class UIBus:
    """Singleton accessor for the global UI event bus."""

    @staticmethod
    def get() -> _BusEvents:
        """Returns the shared instance of the event bus."""
        return _bus


__all__ = ["UIBus"]
