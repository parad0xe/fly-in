from arcade import Window

from flyin.models.graph import Graph
from flyin.renderer.views.editor_view import EditorView


class GraphWindow(Window):
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    WINDOW_TITLE = "Fly-In"

    @classmethod
    def load(cls, graph: Graph) -> Window:
        window = Window(
            cls.WINDOW_WIDTH,
            cls.WINDOW_HEIGHT,
            cls.WINDOW_TITLE,
            resizable=True,
        )
        window.show_view(EditorView(graph))
        return window
