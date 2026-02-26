from PyQt6.QtCore import QObject, pyqtSignal


class _BusEvents(QObject):
    graph_updated = pyqtSignal()


_bus = _BusEvents()


class UIBus:

    @staticmethod
    def get() -> _BusEvents:
        return _bus


__all__ = ["UIBus"]
