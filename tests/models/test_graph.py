from typing import Callable, Optional

import pytest

from flyin.exceptions.graph import GraphInsufficientHubCapacityError
from flyin.models.graph import Graph
from flyin.models.hub import Hub
from flyin.models.link import Link

CallableGraphFactoryReturn = Callable[
    [
        Hub,
        Hub,
        list[Hub],
        Optional[list[Link]],
    ],
    Graph,
]


@pytest.fixture
def hubs() -> tuple[Hub, Hub, Hub]:
    """Provides a set of initialized Hub instances for testing."""
    h1 = Hub(name="Alpha", x=0, y=0)
    h2 = Hub(name="Beta", x=10, y=10)
    h3 = Hub(name="Gamma", x=20, y=20)
    return h1, h2, h3


@pytest.fixture
def graph_factory() -> CallableGraphFactoryReturn:
    """
    Provides a factory to create Graph instances with specific connections.
    """

    def _create_graph(
        start_hub: Hub,
        end_hub: Hub,
        custom_hubs: list[Hub],
        links: list[Link] | None = None,
    ) -> Graph:
        return Graph(
            hubs=custom_hubs,
            links=links or [],
            start_hub=start_hub,
            end_hub=end_hub,
        )

    return _create_graph


def test_graph_iter_unique_connections_with_no_links(
    hubs, graph_factory
) -> None:
    """Verify that an empty iterator is returned when no connections exist."""
    h1, h2, _ = hubs
    graph = graph_factory(h1, h2, [h1, h2])
    connections = list(graph.iter_unique_connections())
    assert len(connections) == 0


def test_graph_iter_unique_connections_preserves_uniqueness(
    hubs, graph_factory
) -> None:
    """
    Ensure each link is yielded exactly once despite bidirectional references.
    """
    h1, h2, _ = hubs
    shared_link = Link()

    h1.connect_both(h2, shared_link)

    graph = graph_factory(h1, h2, [h1, h2], [shared_link])

    iterator = graph.iter_unique_connections()
    result = next(iterator)

    with pytest.raises(StopIteration):
        next(iterator)

    _, _, link = result
    assert link.id == shared_link.id


@pytest.mark.parametrize(
    "topology, expected_count",
    [
        ("empty_graph", 0),
        ("linear_chain", 2),
        ("bidirectional_single_link", 1),
        ("loop", 3),
    ],
)
def test_graph_iter_unique_connections_topologies(
    hubs, graph_factory, topology, expected_count
):
    """Validate connection iteration across various graph structures."""
    h1, h2, h3 = hubs
    links = []

    if topology == "linear_chain":
        link_1, link_2 = Link(), Link()
        h1.connect_to(h2, link_1)
        h2.connect_to(h3, link_2)
        links = [link_1, link_2]
    elif topology == "bidirectional_single_link":
        link_1 = Link()
        h1.connect_both(h2, link_1)
        links = [link_1]
    elif topology == "loop":
        link_1, link_2, link_3 = Link(), Link(), Link()
        h1.connect_both(h2, link_1)
        h2.connect_both(h3, link_2)
        h3.connect_both(h1, link_3)
        links = [link_1, link_2, link_3]

    graph = graph_factory(h1, h2, [h1, h2, h3], links)
    assert len(list(graph.iter_unique_connections())) == expected_count


def test_graph_iter_unique_connections_yields_correct_triplets(
    hubs, graph_factory
) -> None:
    """Verify the structure and data of the yielded hub-hub-link triplets."""
    h1, h2, h3 = hubs
    link_a = Link()
    link_b = Link()

    h1.connect_to(h2, link_a)
    h2.connect_to(h3, link_b)

    graph = graph_factory(h1, h2, [h1, h2, h3], links=[link_a, link_b])
    iterator = graph.iter_unique_connections()
    result = list(iterator)

    assert len(result) == 2

    assert (h1, h2, link_a) in result
    assert (h2, h3, link_b) in result


def test_graph_iter_unique_connections_with_multiple_independent_links(
    hubs, graph_factory
) -> None:
    """Confirm all distinct links are found in a multi-node topology."""
    h1, h2, h3 = hubs
    link_1, link_2 = Link(), Link()

    h1.connect_to(h2, link_1)
    h1.connect_to(h3, link_2)

    graph = graph_factory(h1, h2, [h1, h2, h3], links=[link_1, link_2])
    ids_found = {conn[2].id for conn in graph.iter_unique_connections()}

    assert ids_found == {link_1.id, link_2.id}


def test_graph_fails_on_insufficient_end_capacity(graph_factory) -> None:
    """
    Verify that Graph construction fails if the end hub's capacity
    is lower than the number of drones starting at the start hub.
    """
    h1 = Hub(name="Start", x=0, y=0, drones=10, max_drones=10)
    h2 = Hub(name="End", x=10, y=10, drones=0, max_drones=5)

    with pytest.raises(GraphInsufficientHubCapacityError):
        graph_factory(h1, h2, [h1, h2])


def test_graph_succeeds_on_sufficient_end_capacity(graph_factory) -> None:
    """
    Ensure that a Graph is successfully instantiated when the end hub
    has enough capacity to receive all starting drones.
    """
    h1 = Hub(name="Start", x=0, y=0, drones=10, max_drones=10)
    h2 = Hub(name="End", x=10, y=10, drones=0, max_drones=10)

    graph = graph_factory(h1, h2, [h1, h2])
    assert isinstance(graph, Graph)
