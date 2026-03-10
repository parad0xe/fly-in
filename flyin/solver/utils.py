from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from flyin.models.graph import Graph
from flyin.models.hub import Hub, HubZoneType
from flyin.solver.dist_table import DistanceTable
from flyin.solver.types import Config, Constraint, GraphItem

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LowLevelNode:
    """
    Representation of constraints for a single agent movement.

    Attributes:
        constraints: Mapping of agent indices to their restricted moves.
    """

    constraints: Constraint = field(default_factory=lambda: {})


@dataclass(slots=True)
class HighLevelNode:
    """
    Node in the high-level search tree for the LaCAM algorithm.

    Attributes:
        distance: Distance table for heuristic calculations.
        config: Current agent configuration (positions).
        graph: The environment graph.
        config_start: Starting configuration of agents.
        config_end: Target configuration of agents.
        g: Cost from the start node to this node.
        h: Heuristic estimate of cost to reach the target.
        f: Total estimated cost (g + h).
        tree: Queue of low-level constraint nodes to explore.
        parent: Reference to the predecessor node.
        neighbors: Collection of connected high-level nodes.
        failed_agent: Index of the agent that caused a collision.
    """

    distance: DistanceTable
    config: Config
    graph: Graph
    config_start: Config
    config_end: Config

    g: float = 0  # distance from start
    h: float = 0  # estimate sum of distance to target for all agent
    f: float = field(init=False)  # total estimated cost: sum of g + h

    tree: deque[LowLevelNode] = field(
        default_factory=lambda: deque([LowLevelNode()])
    )
    parent: Optional[HighLevelNode] = None
    neighbors: deque[HighLevelNode] = field(default_factory=lambda: deque())

    def __lt__(self, other: HighLevelNode) -> bool:
        """Comparison for priority queue based on f and h values."""
        if self.f != other.f:
            return self.f < other.f
        if self.h != other.h:
            return self.h < other.h
        return False

    def __post_init__(self) -> None:
        """Initialize heuristic and total cost after dataclass init."""
        self.h = Utils.get_h(self.distance, self.config)
        self.f = self.g + self.h

    def next_lazy_constraints(
        self,
        low_level_node: LowLevelNode,
        agent_index: Optional[int] = None,
    ) -> None:
        """
        Generate the next set of constraints for exploration.

        """
        if agent_index is None:
            for ak in range(len(self.config)):
                if ak not in low_level_node.constraints:
                    agent_index = ak
                    break

        if agent_index is None:
            return

        moves = Utils.get_moves(
            self.graph,
            self.distance,
            agent_index,
            self.config[agent_index],
        )
        for move in reversed(moves):
            current_constraints = low_level_node.constraints.copy()
            current_constraints[agent_index] = move
            self.tree.append(LowLevelNode(current_constraints))

    def backtrace(self) -> list[Config]:
        """
        Reconstruct the path from the start to this node.

        Returns:
            List of configurations from start to current state.
        """
        output: list[Config] = []
        current: Optional[HighLevelNode] = self
        while current:
            output.append(current.config)
            current = current.parent
        return output[::-1]


class Utils:
    """
    Utility functions for graph search and heuristic calculations.

    Attributes:
        _moves_cache: Internal cache for get_moves results.
    """

    _moves_cache: dict[tuple[int, Hub, bool], list[GraphItem]] = {}

    @staticmethod
    def get_h(distance: DistanceTable, config: Config) -> float:
        """
        Calculate the heuristic cost for a configuration.

        Args:
            distance: Precomputed distance table.
            config: Current agent positions.

        Returns:
            The sum of distances to targets for all agents.
        """
        num_agents: int = len(config)
        return sum(
            [
                distance.get(
                    agent_index, config[agent_index], default=float("inf")
                )
                for agent_index in range(num_agents)
            ]
        )

    @staticmethod
    def get_moves(
        graph: Graph,
        distance: DistanceTable,
        agent_index: int,
        hub: Hub,
        can_wait: bool = True,
    ) -> list[GraphItem]:
        """
        Retrieve and sort valid moves for a specific agent.

        Args:
            graph: The environment graph.
            distance: Heuristic distance table.
            agent_index: Index of the agent.
            hub: Current hub of the agent.
            can_wait: Whether the agent can stay at its hub.

        Returns:
            List of valid moves sorted by heuristic and priority.
        """

        cache_key = (agent_index, hub, can_wait)
        if cache_key in Utils._moves_cache:
            return Utils._moves_cache[cache_key]

        def _sort_by(data: GraphItem) -> tuple[float, int, int]:
            hub_to, _ = data
            dist = distance.get(agent_index, hub_to, default=float("inf"))
            priority_score = 0 if hub_to.zone == HubZoneType.PRIORITY else 1
            move_score = 1 if hub == hub_to else 0
            tie_breaker = hash((agent_index, hub_to.name, move_score))
            return (dist, priority_score, tie_breaker)

        moves: list[GraphItem] = list(graph.get(hub))
        if not hub.is_dummy and can_wait:
            moves.append((hub, None))

        moves.sort(key=_sort_by)
        Utils._moves_cache[cache_key] = moves
        return moves
