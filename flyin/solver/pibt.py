from __future__ import annotations

from typing import Optional, cast

from flyin.models.graph import Graph
from flyin.models.hub import Hub, HubZoneType
from flyin.solver.dist_table import DistanceTable
from flyin.solver.types import Config, GraphItem, WipConfig
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
    ) -> Optional[Config]:
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
        return cls(
            graph,
            distance,
            high_level_node,
            low_level_node,
        ).compute_next_config()

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

        self.active_agents: list[bool] = [False] * self.num_agents

        self.initial_occupants: dict[Hub, list[int]] = {}

        for i, hub in enumerate(high_level_node.config):
            if hub not in self.initial_occupants:
                self.initial_occupants[hub] = []
            self.initial_occupants[hub].append(i)

        self.committed_count: dict[Hub, int] = {}
        self.committed_moving_count: dict[tuple[Hub, Hub], int] = {}
        self.sleeping_count: dict[Hub, int] = {
            hub: len(agents) for hub, agents in self.initial_occupants.items()
        }

        self.restricted_incoming: dict[Hub, int] = {}

    def compute_next_config(self) -> Optional[Config]:
        """
        Process agents by priority to compute the next valid step.

        Returns:
            The resolved configuration or None, and failing agent ID.
        """
        priorities: list[tuple[float, int]] = []

        for agent_index in range(self.num_agents):
            if agent_index in self.low_level_node.constraints:
                priorities.append((-float("inf"), agent_index))
            else:
                dist = self.distance.get(
                    agent_index,
                    self.high_level_node.config[agent_index],
                    default=float("inf"),
                )
                priorities.append((-dist, agent_index))

        priorities.sort()

        for _, a in priorities:
            if self.config_new[a] is None:
                if not self._assign_move_to_agent(a, 0):
                    return None

        return tuple(cast(Config, self.config_new))

    def _assign_move_to_agent(self, agent_index: int, depth: int = 0) -> bool:
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

        if self.active_agents[agent_index]:
            return False

        self.active_agents[agent_index] = True
        hub_from = self.high_level_node.config[agent_index]

        moves = self._get_moves(agent_index, hub_from, can_wait=(depth == 0))

        for hub_to, link in moves:
            is_waiting = hub_from == hub_to

            if hub_to.zone == HubZoneType.BLOCKED:
                continue

            # hub_to has capacity?
            if (not is_waiting and
                    self.committed_count.get(hub_to, 0) >= hub_to.max_drones):
                continue

            edge = (hub_from, hub_to)

            # link has capacity?
            if link is not None:
                if (not is_waiting and self.committed_moving_count.get(edge, 0)
                        >= link.max_link_capacity):
                    continue

            # swap collision conflict?
            has_swap_conflict = False
            if not is_waiting:
                for ak in self.initial_occupants.get(hub_to, []):
                    if self.config_new[ak] == hub_from:
                        has_swap_conflict = True
                        break
            if has_swap_conflict:
                continue

            restricted_at_t2: Optional[Hub] = None
            if hub_to.is_dummy:
                restricted_hub = hub_to.connections[0][0]

                # link capacity (A -> Dummy -> Restricted) full?
                if link is not None:
                    dummy_count = (
                        self.sleeping_count.get(hub_to, 0) +
                        self.committed_count.get(hub_to, 0) +
                        self.committed_moving_count.get(
                            (hub_to, restricted_hub), 0
                        )
                    )
                    if dummy_count >= link.max_link_capacity:
                        continue

                # restricted has capacity at T+2?
                if not is_waiting:
                    restricted_at_t2 = restricted_hub
                    if (self.restricted_incoming.get(restricted_at_t2, 0)
                            >= restricted_at_t2.max_drones):
                        continue

            # commit move
            self.config_new[agent_index] = hub_to
            self.committed_count[hub_to] = (
                self.committed_count.get(hub_to, 0) + 1
            )
            self.sleeping_count[hub_from] -= 1

            if not is_waiting:
                self.committed_moving_count[edge] = (
                    self.committed_moving_count.get(edge, 0) + 1
                )
            if restricted_at_t2 is not None:
                self.restricted_incoming[restricted_at_t2] = (
                    self.restricted_incoming.get(restricted_at_t2, 0) + 1
                )

            # resoving conflict
            resolved = True
            projected_count = self.committed_count.get(
                hub_to, 0
            ) + self.sleeping_count.get(hub_to, 0)

            if projected_count > hub_to.max_drones:
                resolved = False
                for ak in self.initial_occupants.get(hub_to, []):
                    if projected_count <= hub_to.max_drones:
                        resolved = True
                        break

                    if self.config_new[ak] is None:
                        if self._assign_move_to_agent(ak, depth + 1):
                            projected_count = self.committed_count.get(
                                hub_to, 0
                            ) + self.sleeping_count.get(hub_to, 0)
                            if projected_count <= hub_to.max_drones:
                                resolved = True
                        else:
                            resolved = False
                            # break

                if projected_count > hub_to.max_drones:
                    resolved = False

            if resolved:
                self.active_agents[agent_index] = False
                return True

            # rollback move if move is impossible
            self.config_new[agent_index] = None
            self.committed_count[hub_to] -= 1
            self.sleeping_count[hub_from] += 1

            if not is_waiting:
                self.committed_moving_count[edge] -= 1
            if restricted_at_t2 is not None:
                self.restricted_incoming[restricted_at_t2] -= 1

        self.active_agents[agent_index] = False
        return False

    def _get_moves(
        self,
        agent_index: int,
        hub_from: Hub,
        can_wait: bool,
    ) -> list[GraphItem]:
        """
        Retrieve valid potential moves for a given agent.

        Args:
            agent_index: ID of the agent.
            hub_from: The starting hub of the agent.
            can_wait: True if the agent is allowed to wait.

        Returns:
            A list of tuples containing the destination hub and link.
        """
        all_moves = Utils.get_moves(
            self.graph, self.distance, agent_index, hub_from, can_wait
        )
        if agent_index in self.low_level_node.constraints:
            constraint_hub = self.low_level_node.constraints[agent_index]
            return [constraint_hub] if constraint_hub in all_moves else []
        return all_moves
