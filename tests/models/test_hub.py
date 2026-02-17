import pytest
from pydantic import ValidationError

from flyin.exceptions.hub import HubSelfConnectionError
from flyin.models.hub import Hub, HubColorType, HubZoneType
from flyin.models.link import Link


@pytest.fixture
def valid_hub_data() -> dict:
    """Provide a dictionary of valid baseline attributes for a Hub instance."""
    return {"name": "DroneAlpha1", "x": 10, "y": 20}


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


def test_hub_supports_both_enum_color_assignment_and_null_color_value(
    valid_hub_data,
):
    """Validate color attribute handling for Enum members and null values."""
    hub = Hub(**valid_hub_data, color=HubColorType.BLUE)
    assert hub.color == HubColorType.BLUE

    hub.color = None
    assert Hub(**valid_hub_data, color=None).color is None


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "1Hub",
        "_hub",
        " hub",
    ],
)
def test_hub_creation_fails_for_names_violating_naming_conventions(
    valid_hub_data, invalid_name
):
    """
    Ensure Hub rejection of names violating length or pattern constraints.
    """
    valid_hub_data["name"] = invalid_name
    with pytest.raises(ValidationError) as excinfo:
        Hub(**valid_hub_data)

    assert "name" in str(excinfo.value)


@pytest.mark.parametrize("invalid_max", [-1, -200])
def test_hub_prevents_negative_values_for_maximum_drone_capacity(
    valid_hub_data, invalid_max
):
    """
    Verify that non-positive drone capacity values trigger validation errors.
    """
    with pytest.raises(ValidationError):
        Hub(**valid_hub_data, max_drones=invalid_max)


def test_hub_automatically_converts_numeric_strings_to_integers(
    valid_hub_data,
):
    """
    Confirm Pydantic automatic conversion of compatible types to integers.
    """
    data = {**valid_hub_data, "x": "10", "y": "20"}
    hub = Hub(**data)  # type: ignore
    assert isinstance(hub.x, int)
    assert hub.x == 10


def test_hub_initializes_with_an_empty_links_list_by_default(valid_hub_data):
    """
    Verify that the links collection is
        initialized as an empty list by default.
    """
    hub = Hub(**valid_hub_data)
    assert hub.links == []
    assert isinstance(hub.links, list)


def test_hub_successfully_registers_valid_peer_hub_connections(valid_hub_data):
    """
    Confirm successful registration of a peer connection
        between two distinct hub instances.
    """
    hub_a = Hub(**valid_hub_data)
    hub_b = Hub(name="DroneBeta", x=30, y=40)

    hub_a.links.append((hub_b, Link()))

    assert len(hub_a.links) == 1
    target_hub, connection = hub_a.links[0]
    assert target_hub.name == "DroneBeta"
    assert connection.max_link_capacity == 1


def test_hub_validates_strict_structural_types_for_link_entries(
    valid_hub_data,
):
    """
    Ensure that malformed data structures within the
        links list trigger validation failures.
    """
    with pytest.raises(ValidationError):
        Hub(
            **valid_hub_data,
            links=[("pas_un_hub", "pas_un_link")],  # type: ignore
        )

    valid_hub = Hub(**valid_hub_data)
    valid_hub.name = "Hub_valid"
    with pytest.raises(ValidationError):
        Hub(
            **valid_hub_data,
            links=[(valid_hub, "pas_un_link")],  # type: ignore
        )

    with pytest.raises(ValidationError):
        Hub(
            **valid_hub_data,
            links=[("invalid_hub", Link())],  # type: ignore
        )


def test_hub_prevents_self_connection_within_the_links_collection(
    valid_hub_data,
):
    """Verify that a hub cannot be registered as its own peer in links."""
    hub_a = Hub(**valid_hub_data)

    with pytest.raises(HubSelfConnectionError):
        Hub(**valid_hub_data, links=[(hub_a, Link())])
