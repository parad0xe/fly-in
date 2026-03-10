import logging
from collections import deque
from typing import TypeAlias

from typing_extensions import Self

from flyin.exceptions.solver import SolverConfigurationMismatchError
from flyin.models.graph import Graph
from flyin.models.hub import Hub
from flyin.solver.types import Config, GraphType

TableType: TypeAlias = dict[int, dict[Hub, float]]

logger = logging.getLogger(__name__)


class DistanceTable:
    """
    Table holding precomputed heuristic distances for agents.
    """

    def __init__(self, table: TableType) -> None:
        """
        Initialize the distance table with precomputed values.

        Args:
            table: Precomputed mapping of agent to hub distances.
        """
        self.table: dict[int, dict[Hub, float]] = table

    def __getitem__(self, agent_index: int) -> dict[Hub, float]:
        """
        Get the distance dictionary for a specific agent.

        Args:
            key: The index of the agent.

        Returns:
            A dictionary mapping hubs to their heuristic distance.
        """
        return self.table[agent_index]

    def get(self, agent_index: int, hub_from: Hub, default: float) -> float:
        """
        Retrieve distance for an agent from a hub with a fallback.

        Args:
            agent_index: The index of the agent.
            hub_from: The current hub to evaluate.
            default: The fallback distance if not found.

        Returns:
            The calculated distance or the default value.
        """
        return self.table[agent_index].get(hub_from, default)

    @classmethod
    def compute_heuristic_table(
        cls,
        graph: Graph,
        config_start: Config,
        config_end: Config,
    ) -> Self:
        """
        Compute backward BFS heuristic distances for all agents.

        Args:
            graph: The network graph containing hubs and links.
            config_start: Initial configuration of agents.
            config_end: Target configuration of agents.

        Returns:
            A new instance of DistanceTable with computed values.

        Raises:
            SolverConfigurationMismatchError: If configurations differ in size.
        """
        logger.debug(
            "Generating distance table (Global Optimized Backward BFS)..."
        )

        if len(config_end) != len(config_start):
            raise SolverConfigurationMismatchError()

        reverse_graph: GraphType = {}
        for hub in graph.hubs:
            if hub not in reverse_graph:
                reverse_graph[hub] = []
            for neighbor, link in hub.connections:
                if neighbor not in reverse_graph:
                    reverse_graph[neighbor] = []
                reverse_graph[neighbor].append((hub, link))

        distance_table = {}
        distance_cache: dict[Hub, dict[Hub, float]] = {}

        for agent_index in range(len(config_start)):
            end_hub = config_end[agent_index]

            if end_hub in distance_cache:
                distance_table[agent_index] = distance_cache[end_hub]
                continue

            distances_to_end: dict[Hub, float] = {end_hub: 0.0}
            queue = deque([end_hub])

            while queue:
                current_hub = queue.popleft()
                current_cost = distances_to_end[current_hub]

                for neighbor, _ in reverse_graph.get(current_hub, []):
                    if neighbor not in distances_to_end:
                        distances_to_end[neighbor] = current_cost + 1.0
                        queue.append(neighbor)

            distance_cache[end_hub] = distances_to_end
            distance_table[agent_index] = distances_to_end

        logger.info("Distance table generated")
        return cls(table=distance_table)
