import pytest
from pydantic import ValidationError

from flyin.exceptions.hub import HubDuplicateLinkError, HubSelfConnectionError
from flyin.models.hub import Hub, HubColorType, HubZoneType
from flyin.models.link import Link


@pytest.fixture
def valid_hub_data() -> dict:
    """Provide a dictionary of valid baseline attributes for a Hub instance."""
    return {"name": "DroneAlpha1", "x": 10, "y": 20}


def test_hub_initializes_with_default_values(valid_hub_data):
    """Verify default values for zone, drones, and max_drones capacity."""
    hub = Hub(**valid_hub_data)
    assert hub.zone == HubZoneType.NORMAL
    assert hub.drones == 0
    assert hub.max_drones == 1
    assert hub.links == []
    assert hub.is_leaf is True


def test_hub_prevents_extra_fields(valid_hub_data):
    """Ensure that providing unknown fields triggers a validation error."""
    valid_hub_data["unknown_field"] = "data"
    with pytest.raises(ValidationError):
        Hub(**valid_hub_data)


@pytest.mark.parametrize("field", ["drones", "max_drones"])
def test_hub_prevents_negative_drone_counts(valid_hub_data, field):
    """Verify that drone-related counts cannot be negative."""
    with pytest.raises(ValidationError):
        Hub(**{**valid_hub_data, field: -1})


@pytest.mark.parametrize("zone", [None, *list(HubZoneType)])
def test_hub_instantiation_applies_specified_or_default_zones(
    valid_hub_data, zone
):
    """Verify Hub instantiation across all zone types and default values."""
    if zone:
        valid_hub_data["zone"] = zone

    hub = Hub(**valid_hub_data)

    expected_zone = zone if zone else HubZoneType.NORMAL
    assert hub.zone == expected_zone
    assert hub.max_drones == 1


def test_hub_supports_enum_and_null_colors(valid_hub_data):
    """Validate color handling for Enum members and null values."""
    hub = Hub(**valid_hub_data, color=HubColorType.BLUE)
    assert hub.color == HubColorType.BLUE

    hub.color = None
    assert Hub(**valid_hub_data, color=None).color is None


@pytest.mark.parametrize("name", ["", "1Hub", "_hub", " hub", "hub-a"])
def test_hub_rejects_invalid_naming_patterns(valid_hub_data, name):
    """Ensure hub names follow the required alphanumeric pattern."""
    valid_hub_data["name"] = name
    with pytest.raises(ValidationError):
        Hub(**valid_hub_data)


def test_hub_connect_to_registers_link(valid_hub_data):
    """Confirm the connect_to method correctly updates the links list."""
    hub_a = Hub(**valid_hub_data)
    hub_b = Hub(name="DroneBeta", x=30, y=40)
    link = Link(max_link_capacity=5)

    hub_a.connect_to(hub_b, link)

    assert len(hub_a.links) == 1
    assert hub_a.links[0] == (hub_b, link)
    assert len(hub_b.links) == 0


def test_hub_prevents_self_connection_on_instantiation(valid_hub_data):
    """Ensure self-connection is blocked during object creation."""
    hub_a = Hub(**valid_hub_data)
    with pytest.raises(HubSelfConnectionError):
        Hub(**valid_hub_data, links=[(hub_a, Link())])


def test_hub_connect_both_registers_mutual_links(valid_hub_data):
    """Verify connect_both establishes a bidirectional connection."""
    hub_a = Hub(**valid_hub_data)
    hub_b = Hub(name="DroneBeta", x=30, y=40)
    link = Link()

    hub_a.connect_both(hub_b, link)

    assert (hub_b, link) in hub_a.links
    assert (hub_a, link) in hub_b.links


def test_hub_add_link_prevents_self_connection(valid_hub_data):
    """Ensure the add_link method blocks connection to itself."""
    hub_a = Hub(**valid_hub_data)
    with pytest.raises(HubSelfConnectionError):
        hub_a.connect_to(hub_a, Link())


def test_hub_prevents_duplicate_links(valid_hub_data):
    """Ensure duplicate connections between hubs are prohibited."""
    hub_a = Hub(**valid_hub_data)
    hub_b = Hub(name="Beta", x=30, y=40)
    link = Link()
    hub_a.links = [(hub_b, link), (hub_b, link)]
    with pytest.raises(HubDuplicateLinkError):
        hub_a.ensure_integrity()

    hub_a = Hub(**valid_hub_data)
    hub_b = Hub(name="Beta", x=30, y=40)
    link_1 = Link()
    link_2 = Link()
    hub_a.links = [(hub_b, link_1), (hub_b, link_2)]
    with pytest.raises(HubDuplicateLinkError):
        hub_a.ensure_integrity()


def test_hub_connect_to_prevents_duplicates(valid_hub_data):
    """Ensure connect_to prevents creating redundant mutual connections."""
    hub_a = Hub(**valid_hub_data)
    hub_b = Hub(name="Beta", x=30, y=40)
    link = Link()

    hub_a.connect_to(hub_b, link)

    with pytest.raises(HubDuplicateLinkError):
        hub_a.connect_to(hub_b, link)


def test_hub_connect_both_prevents_duplicates(valid_hub_data):
    """Ensure connect_both prevents creating redundant mutual connections."""
    hub_a = Hub(**valid_hub_data)
    hub_b = Hub(name="Beta", x=30, y=40)
    link = Link()

    hub_a.connect_both(hub_b, link)

    with pytest.raises(HubDuplicateLinkError):
        hub_b.connect_both(hub_a, link)


def test_hub_updates_leaf_status(valid_hub_data):
    """Verify is_leaf becomes False when more than one links exist."""
    hub = Hub(**valid_hub_data)
    assert hub.is_leaf is True

    hubs = [Hub(name=f"Hub{i}", x=i, y=i) for i in range(3)]

    hub.connect_to(hubs[0], Link())
    assert hub.is_leaf is True
    assert hubs[0].is_leaf is True

    hub.connect_to(hubs[1], Link())
    assert hub.is_leaf is False
    assert hubs[0].is_leaf is True
    assert hubs[1].is_leaf is True

    hubs[0].connect_both(hubs[2], Link())
    assert hubs[0].is_leaf is True
    assert hubs[2].is_leaf is True

    hubs[0].connect_to(hubs[1], Link())
    assert hubs[0].is_leaf is False
    assert hubs[1].is_leaf is True


def test_hub_automatically_converts_numeric_strings(valid_hub_data):
    """Confirm Pydantic conversion of numeric strings to integers."""
    data = {**valid_hub_data, "x": "10", "y": "20"}
    hub = Hub(**data)  # type: ignore
    assert isinstance(hub.x, int)
    assert hub.x == 10
