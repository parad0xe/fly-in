from __future__ import annotations

import heapq
from typing import Optional, cast

from flyin.models.graph import Graph
from flyin.models.hub import Hub, HubZoneType
from flyin.models.link import Link
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
        self.priorities: list[tuple[float, int]] = []
        self.active_agents: set[int] = set()

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

    def compute_next_config(self) -> tuple[Optional[Config], Optional[int]]:
        """
        Process agents by priority to compute the next valid step.

        Returns:
            The resolved configuration or None, and failing agent ID.
        """
        self._compute_priorities()

        while len(self.priorities) > 0:
            _, a = heapq.heappop(self.priorities)
            if (a is not None and self.config_new[a] is None and
                    not self._assign_agent(a)):
                return None, a

        return (tuple(cast(Config, self.config_new)), None)

    def _compute_priorities(self) -> None:
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

    def _assign_agent(self, agent_index: int, depth: int = 0) -> bool:
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
        moves = self._get_moves(agent_index, hub_from, can_wait=depth == 0)

        for hub_to, link in moves:
            is_waiting = hub_from == hub_to

            if hub_to.zone == HubZoneType.BLOCKED:
                continue

            # hub_to has potential capacity?
            if not self._has_available_capacity(
                    hub_from,
                    hub_to,
                    link,
                    is_waiting,
            ):
                continue

            # swap collision conflict?
            if not self._validate_no_swap_conflict(
                    hub_from,
                    hub_to,
                    is_waiting,
            ):
                continue

            # link capacity (A -> Dummy -> Restricted) full?
            if hub_to.is_dummy and not self._restricted_has_link_capacity(
                    hub_to,
                    link,
            ):
                continue

            # restricted has capacity at T+2?
            restricted_at_t2: Optional[Hub] = None
            if hub_to.is_dummy:
                restricted_at_t2, has_capacity = (
                    self._check_future_capacity_of_restricted(
                        hub_to, is_waiting
                    )
                )
                if not has_capacity:
                    continue

            self._commit_move(
                agent_index,
                hub_from,
                hub_to,
                is_waiting,
                restricted_at_t2,
            )

            if self._resolve_conflict(hub_to, depth):
                self.active_agents.remove(agent_index)
                return True

            self._rollback_move(
                agent_index,
                hub_from,
                hub_to,
                is_waiting,
                restricted_at_t2,
            )

        self.active_agents.remove(agent_index)
        return False

    def _commit_move(
        self,
        agent_index: int,
        hub_from: Hub,
        hub_to: Hub,
        is_waiting: bool,
        restricted_at_t2: Hub | None,
    ) -> None:
        """
        Apply state changes for a committed move.

        Args:
            agent_index: ID of the agent.
            hub_from: The starting hub.
            hub_to: The destination hub.
            is_waiting: True if the agent waits at its current hub.
            restricted_at_t2: Restricted hub at T+2, if applicable.
        """
        self.config_new[agent_index] = hub_to
        self.committed_count[hub_to] = self.committed_count.get(hub_to, 0) + 1
        self.sleeping_count[hub_from] -= 1

        if not is_waiting:
            current_moving = self.committed_moving_count.get(
                (hub_from, hub_to), 0
            )
            self.committed_moving_count[(hub_from, hub_to)] = (
                current_moving + 1
            )

        if restricted_at_t2 is not None:
            self.restricted_incoming[restricted_at_t2] = (
                self.restricted_incoming.get(restricted_at_t2, 0) + 1
            )

    def _rollback_move(
        self,
        agent_index: int,
        hub_from: Hub,
        hub_to: Hub,
        is_waiting: bool,
        restricted_at_t2: Hub | None,
    ) -> None:
        """
        Revert state changes for a rolled-back move.

        Args:
            agent_index: ID of the agent.
            hub_from: The starting hub.
            hub_to: The destination hub.
            is_waiting: True if the agent waits at its current hub.
            restricted_at_t2: Restricted hub at T+2, if applicable.
        """
        self.config_new[agent_index] = None
        self.committed_count[hub_to] -= 1
        self.sleeping_count[hub_from] += 1

        if not is_waiting:
            self.committed_moving_count[(hub_from, hub_to)] -= 1

        if restricted_at_t2 is not None:
            self.restricted_incoming[restricted_at_t2] -= 1

    def _resolve_conflict(self, hub_to: Hub, depth: int) -> bool:
        """
        Resolve capacity conflicts using priority inheritance.

        Args:
            hub_to: The destination hub causing potential conflict.
            depth: Current recursion depth for PIBT.

        Returns:
            True if all conflicts are resolved, False otherwise.
        """
        projected_count = self.committed_count.get(
            hub_to, 0
        ) + self.sleeping_count.get(hub_to, 0)

        if projected_count <= hub_to.max_drones:
            return True

        for ak in self.initial_occupants.get(hub_to, []):
            if projected_count <= hub_to.max_drones:
                break

            if self.config_new[ak] is None:
                if self._assign_agent(ak, depth + 1):
                    projected_count = self.committed_count.get(
                        hub_to, 0
                    ) + self.sleeping_count.get(hub_to, 0)
                else:
                    return False

        return projected_count <= hub_to.max_drones

    def _get_moves(self, agent_index: int, hub_from: Hub, can_wait: bool):
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

    def _has_available_capacity(
        self,
        hub_from: Hub,
        hub_to: Hub,
        link: Optional[Link],
        is_waiting: bool,
    ) -> bool:
        """
        Check if target hub and link have enough capacity.

        Args:
            hub_from: The starting hub.
            hub_to: The destination hub.
            link: The link connecting the hubs (if any).
            is_waiting: True if the agent waits at its current hub.

        Returns:
            True if there is sufficient capacity, False otherwise.
        """
        if (not is_waiting and
                self.committed_count.get(hub_to, 0) >= hub_to.max_drones):
            return False

        if link is not None:
            commited_count = self.committed_moving_count.get(
                (hub_from, hub_to), 0
            )
            if not is_waiting and commited_count >= link.max_link_capacity:
                return False
        return True

    def _validate_no_swap_conflict(
        self,
        hub_from: Hub,
        hub_to: Hub,
        is_waiting: bool,
    ) -> bool:
        """
        Check for swap conflicts between two moving agents.

        Args:
            hub_from: The starting hub of the current agent.
            hub_to: The intended destination hub.
            is_waiting: True if the agent is waiting.

        Returns:
            False if swap collision is detected, else True.
        """
        has_swap_conflict = False
        if not is_waiting:
            for ak in self.initial_occupants.get(hub_to, []):
                if self.config_new[ak] == hub_from:
                    has_swap_conflict = True
                    break
        if has_swap_conflict:
            return False
        return True

    def _check_future_capacity_of_restricted(
        self,
        hub_to: Hub,
        is_waiting: bool,
    ) -> tuple[Optional[Hub], bool]:
        """
        Validate T+2 restricted hub capacity via a dummy hub.

        Args:
            hub_from: The starting hub.
            hub_to: The destination dummy hub.
            is_waiting: True if the agent is waiting.

        Returns:
            Tuple of T+2 restricted hub and a capacity validity bool.
        """
        if is_waiting or not hub_to.is_dummy:
            return None, True

        restricted_at_t2, _ = hub_to.connections[0]

        incoming_count = self.restricted_incoming.get(restricted_at_t2, 0)
        if incoming_count >= restricted_at_t2.max_drones:
            return None, False

        return restricted_at_t2, True

    def _restricted_has_link_capacity(
        self,
        hub_to: Hub,
        link: Optional[Link],
    ) -> bool:
        """
        Check if dummy hub move respects link capacity limits.

        Args:
            hub_to: The destination hub (potentially a dummy hub).
            link: The link connecting to the destination.

        Returns:
            True if the move to the dummy hub is valid, else False.
        """
        if link is None:
            return True

        if hub_to.is_dummy:
            dummy: Hub = hub_to
            restricted: Hub = hub_to.connections[0][0]

            dummy_count = self.sleeping_count.get(dummy, 0)
            dummy_count += self.committed_count.get(dummy, 0)
            dummy_count += self.committed_moving_count.get(
                (dummy, restricted),
                0,
            )

            return dummy_count < link.max_link_capacity
        return True
