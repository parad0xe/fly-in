from arcade import Camera2D


class CameraController:
    def __init__(
        self,
        camera: Camera2D,
        position: tuple[float, float] = (0, 0),
        default_zoom: float = 0.7,
    ) -> None:
        self.camera: Camera2D = camera

        self.camera.position = position
        self.camera.zoom = default_zoom

    def move(self, dx: float, dy: float) -> None:
        self.camera.position = (
            self.camera.position.x - dx / self.camera.zoom,
            self.camera.position.y - dy / self.camera.zoom,
        )

    def zoom(self, delta: float) -> None:
        if self.camera.zoom < 0.4 and delta < 0:
            return

        if self.camera.zoom > 1.5 and delta > 0:
            return

        self.camera.zoom += delta
