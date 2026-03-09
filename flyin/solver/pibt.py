from __future__ import annotations

import heapq
from typing import Optional, cast

from flyin.models.graph import Graph
from flyin.models.hub import Hub, HubZoneType
from flyin.solver.dist_table import DistanceTable
from flyin.solver.types import Config, WipConfig
from flyin.solver.utils import HighLevelNode, LowLevelNode, Utils


class Pibt:
    """
    Priority Inheritance with Backtracking algorithm for MAPF.
    """

    @classmethod
    def run(
        cls,
        graph: Graph,
        distance: DistanceTable,
        high_level_node: HighLevelNode,
        low_level_node: LowLevelNode,
    ) -> tuple[Optional[Config], Optional[int]]:
        """
        Execute PIBT to find the next valid agent configuration.

        Args:
            graph: The network graph model.
            distance: The precomputed distances.
            high_level_node: Current node in the high-level search.
            low_level_node: Node containing low-level constraints.

        Returns:
            A tuple of the new Config (if valid) and failing agent ID.
        """
        return cls(graph, distance, high_level_node, low_level_node).step()

    def __init__(
        self,
        graph: Graph,
        distance: DistanceTable,
        high_level_node: HighLevelNode,
        low_level_node: LowLevelNode,
    ) -> None:
        """
        Initialize the PIBT state with node data and constraints.

        Args:
            graph: The network graph model.
            distance: The heuristic distance table.
            high_level_node: The high-level state context.
            low_level_node: The low-level constraints context.
        """
        self.graph = graph
        self.distance: DistanceTable = distance
        self.high_level_node: HighLevelNode = high_level_node
        self.low_level_node: LowLevelNode = low_level_node
        self.num_agents = len(high_level_node.config)
        self.config_new: WipConfig = [None] * self.num_agents
        self.priorities: list[tuple[float, int]] = []
        self.active_agents: set[int] = set()

        self.initial_occupants: dict[Hub, list[int]] = {}

        for i, hub in enumerate(high_level_node.config):
            if hub not in self.initial_occupants:
                self.initial_occupants[hub] = []
            self.initial_occupants[hub].append(i)

        self.committed_count: dict[Hub, int] = {}
        self.committed_moving_count: dict[Hub, int] = {}
        self.sleeping_count: dict[Hub, int] = {
            hub: len(agents) for hub, agents in self.initial_occupants.items()
        }

        self.restricted_incoming: dict[Hub, int] = {}

    def step(self) -> tuple[Optional[Config], Optional[int]]:
        """
        Process agents by priority to compute the next valid step.

        Returns:
            The resolved configuration or None, and failing agent ID.
        """
        self._update_priorities()

        while len(self.priorities) > 0:
            _, a = heapq.heappop(self.priorities)
            if (a is not None and self.config_new[a] is None and
                    not self._run_pibt(a)):
                return None, a

        return (tuple(cast(Config, self.config_new)), None)

    def _update_priorities(self) -> None:
        """
        Assign and sort agent priorities based on heuristics.
        """
        for agent_index in range(self.num_agents):
            if agent_index in self.low_level_node.constraints:
                heapq.heappush(self.priorities, (-float("inf"), agent_index))
            else:
                dist = self.distance.get(
                    agent_index,
                    self.high_level_node.config[agent_index],
                    default=float("inf"),
                )

                heapq.heappush(self.priorities, (-dist, agent_index))

    def _run_pibt(self, agent_index: int, depth: int = 0) -> bool:
        """
        Recursively assign movements using priority inheritance.

        Args:
            agent_index: ID of the agent to resolve.
            depth: Current recursion depth for backtracking.

        Returns:
            True if a valid move was found and committed, else False.
        """
        if self.config_new[agent_index] is not None:
            return False

        if agent_index in self.active_agents:
            return False

        self.active_agents.add(agent_index)
        hub_from = self.high_level_node.config[agent_index]
        can_wait: bool = depth == 0

        if agent_index in self.low_level_node.constraints:
            constraint_hub = self.low_level_node.constraints[agent_index]
            valid_moves = Utils.get_moves(
                self.graph, self.distance, agent_index, hub_from, can_wait
            )
            if constraint_hub in valid_moves:
                moves = [constraint_hub]
            else:
                moves = []
        else:
            moves = Utils.get_moves(
                self.graph,
                self.distance,
                agent_index,
                hub_from,
                can_wait=can_wait,
            )

        for hub_to, link in moves:
            is_waiting = hub_from == hub_to

            if hub_to.zone == HubZoneType.BLOCKED:
                continue

            # hub_to has potential capacity?
            if (not is_waiting and
                    self.committed_count.get(hub_to, 0) >= hub_to.max_drones):
                continue
            if (not is_waiting and link is not None and
                    self.committed_moving_count.get(
                        hub_to, 0) >= link.max_link_capacity):
                continue

            # resolve swap collision conflict
            has_swap_conflict = False
            if not is_waiting:
                for ak in self.initial_occupants.get(hub_to, []):
                    if self.config_new[ak] == hub_from:
                        has_swap_conflict = True
                        break
            if has_swap_conflict:
                continue

            # agent can move to dummy hub? restricted has capacity at T + 2?
            restricted_at_t2 = None
            if not is_waiting and hub_to.is_dummy:
                restricted_at_t2, _ = hub_to.connections[0]

                if restricted_at_t2 == hub_from:
                    continue

                restricted_incoming_count = self.restricted_incoming.get(
                    restricted_at_t2, 0
                )

                if restricted_incoming_count >= restricted_at_t2.max_drones:
                    continue

            self.config_new[agent_index] = hub_to

            if not is_waiting:
                self.committed_moving_count[hub_to] = (
                    self.committed_moving_count.get(hub_to, 0) + 1
                )

            # update virtual location of agent
            self.committed_count[hub_to] = (
                self.committed_count.get(hub_to, 0) + 1
            )
            self.sleeping_count[hub_from] -= 1

            if restricted_at_t2 is not None:
                self.restricted_incoming[restricted_at_t2] = (
                    self.restricted_incoming.get(restricted_at_t2, 0) + 1
                )

            # resolve hub_to capacity conflict if possible
            projected_count = self.committed_count.get(
                hub_to, 0
            ) + self.sleeping_count.get(hub_to, 0)
            success = True

            # apply priority inheritance (PIBT core)
            if projected_count > hub_to.max_drones:
                for ak in self.initial_occupants.get(hub_to, []):
                    if projected_count <= hub_to.max_drones:
                        break

                    if self.config_new[ak] is None:
                        if self._run_pibt(ak, depth + 1):
                            projected_count = self.committed_count.get(
                                hub_to, 0
                            ) + self.sleeping_count.get(hub_to, 0)
                        else:
                            success = False
                            break

            if success and projected_count <= hub_to.max_drones:
                self.active_agents.remove(agent_index)
                return True
            else:
                # rollback if hub_to is not reachable
                self.config_new[agent_index] = None
                self.committed_count[hub_to] -= 1
                if not is_waiting:
                    self.committed_moving_count[hub_to] -= 1
                self.sleeping_count[hub_from] += 1

                if restricted_at_t2 is not None:
                    self.restricted_incoming[restricted_at_t2] -= 1

        self.active_agents.remove(agent_index)
        return False
