from typing import Optional, TypeAlias

from flyin.models.hub import Hub
from flyin.models.link import Link

# Partial position of all agents a instant T
WipConfig: TypeAlias = list[Optional[Hub]]

# Position of all agents a instant T
Config: TypeAlias = tuple[Hub, ...]

GraphItem: TypeAlias = tuple[Hub, Optional[Link]]
GraphType: TypeAlias = dict[Hub, list[GraphItem]]

# Dict of constraints by agent { agent_id: forced hub }
Constraint: TypeAlias = dict[int, GraphItem]
