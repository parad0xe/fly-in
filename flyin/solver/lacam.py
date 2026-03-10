from __future__ import annotations

import heapq
import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional

from flyin.exceptions.solver import SolverConfigurationMismatchError
from flyin.models.graph import Graph
from flyin.solver.dist_table import DistanceTable
from flyin.solver.pibt import Pibt
from flyin.solver.types import Config
from flyin.solver.utils import HighLevelNode

logger = logging.getLogger(__name__)


@dataclass()
class Lacam:
    """
    Multi-agent pathfinding solver using the LaCAM algorithm.
    """

    @classmethod
    def solve(
        cls,
        graph: Graph,
        config_start: Config,
        config_end: Config,
        max_duration: int = 5000,
    ) -> Optional[list[Config]]:
        """
        Initialize and run the LaCAM solver on the given graph.

        Args:
            graph: The network graph model.
            config_start: Starting hub assignments for agents.
            config_end: Target hub assignments for agents.

        Returns:
            A sequence of configurations solving the problem, or None.
        """
        lacam = cls(
            graph=graph,
            config_start=config_start,
            config_end=config_end,
            max_duration=max_duration,
        )

        return lacam.compute()

    def __init__(
        self,
        graph: Graph,
        config_start: Config,
        config_end: Config,
        max_duration: int = 5000,
    ) -> None:
        """
        Initialize the LaCAM algorithm state and precompute heuristics.

        Args:
            graph: The graph environment.
            config_start: The initial agent positions.
            config_end: The target agent positions.

        Raises:
            SolverConfigurationMismatchError: If configurations differ in size.
        """
        if len(config_start) != len(config_end):
            raise SolverConfigurationMismatchError()

        self.graph: Graph = graph

        self.config_start: Config = config_start
        self.config_end: Config = config_end
        self.num_agents: int = len(config_start)
        self.distance = DistanceTable.compute_heuristic_table(
            graph=graph,
            config_start=config_start,
            config_end=config_end,
        )
        self.max_duration: int = max_duration

    def get_edge_cost(self, config_from: Config, _: Config) -> float:
        """
        Compute the transition cost from a given configuration to another.

        Args:
            config_from: The source configuration.
            config_to: The destination configuration.

        Returns:
            The numerical cost of transitioning.
        """
        if config_from == self.config_end:
            return 0.0
        return 1.0

    def compute(self) -> Optional[list[Config]]:
        """
        Execute the core LaCAM search loop to find a valid path.

        Returns:
            A list of sequential configurations forming the path, or None.
        """

        high_level_node_init: HighLevelNode = HighLevelNode(
            graph=self.graph,
            distance=self.distance,
            config=self.config_start,
            config_start=self.config_start,
            config_end=self.config_end,
        )

        opens: list[HighLevelNode] = [high_level_node_init]
        explored: dict[Config, HighLevelNode] = {
            self.config_start: high_level_node_init
        }
        solution: Optional[HighLevelNode] = None

        start_time: float = time.time()

        def _get_elapsed() -> float:
            return (time.time() - start_time) * 1000

        while (len(opens) > 0) and _get_elapsed() < self.max_duration:
            high_level_node = heapq.heappop(opens)

            if high_level_node.config == self.config_end:
                if solution is not None and solution.g <= high_level_node.g:
                    continue
                solution = high_level_node
                logger.debug(
                    f"New solution found (cost={solution.g})! Refining..."
                )
                continue

            if len(high_level_node.tree) == 0:
                continue

            # check if actual solution is better than current tested branch
            if solution is not None and solution.g < high_level_node.f:
                continue

            low_level_node = high_level_node.tree.pop()

            config_new = Pibt.run(
                self.graph,
                self.distance,
                high_level_node,
                low_level_node,
            )

            if not config_new:
                heapq.heappush(opens, high_level_node)
                continue

            high_level_node.next_lazy_constraints(low_level_node)
            heapq.heappush(opens, high_level_node)

            if config_new in explored:
                high_level_node_to = explored[config_new]

                if high_level_node_to not in high_level_node.neighbors:
                    high_level_node.neighbors.append(high_level_node_to)

                new_g_for_to = high_level_node.g + self.get_edge_cost(
                    high_level_node.config, high_level_node_to.config
                )

                if new_g_for_to < high_level_node_to.g:
                    high_level_node_to.g = new_g_for_to
                    high_level_node_to.f = new_g_for_to + high_level_node_to.h
                    high_level_node_to.parent = high_level_node

                    update: deque[HighLevelNode] = deque([high_level_node_to])

                    while len(update) > 0:
                        high_level_node_from = update.popleft()
                        for n_neighbor in high_level_node_from.neighbors:
                            new_g = (
                                high_level_node_from.g + self.get_edge_cost(
                                    high_level_node_from.config,
                                    n_neighbor.config,
                                )
                            )
                            if new_g < n_neighbor.g:
                                n_neighbor.g = new_g
                                n_neighbor.f = new_g + n_neighbor.h
                                n_neighbor.parent = high_level_node_from
                                update.append(n_neighbor)

                    heapq.heapify(opens)

                continue

            high_level_node_new = HighLevelNode(
                graph=self.graph,
                distance=self.distance,
                config=config_new,
                config_start=self.config_start,
                config_end=self.config_end,
                parent=high_level_node,
                g=high_level_node.g +
                self.get_edge_cost(high_level_node.config, config_new),
            )
            heapq.heappush(opens, high_level_node_new)
            explored[config_new] = high_level_node_new
            high_level_node.neighbors.append(high_level_node_new)

        if solution is not None:
            logger.info(
                "LaCAM search successful. Final path cost: %.2f "
                "(computed in %.2f ms).",
                solution.g,
                _get_elapsed(),
            )
            return solution.backtrace()

        logger.warning(
            "LaCAM search exhausted or timed out after %.2f ms "
            "without finding a valid solution.",
            _get_elapsed(),
        )
        return None
