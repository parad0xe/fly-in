from PyQt6.QtCore import Qt

from flyin.models.hub import HubZoneType

HUB_SIZE = 120
HUB_MARGIN = 400
HUB_SPACING = HUB_SIZE + HUB_MARGIN

SCENE_PADDING = 2000
AGENT_SIZE = 50
ANIMATION_DURATION = 600

LINK_Z_VALUE = -1
LINK_BASE_WIDTH = 5
LINK_MAX_WIDTH = 40

LINK_STYLE_MAP = {
    HubZoneType.BLOCKED: Qt.PenStyle.DashDotDotLine,
    HubZoneType.RESTRICTED: Qt.PenStyle.DotLine,
    HubZoneType.PRIORITY: Qt.PenStyle.DashLine,
    HubZoneType.NORMAL: Qt.PenStyle.SolidLine,
}
