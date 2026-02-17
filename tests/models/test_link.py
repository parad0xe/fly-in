import pytest
from pydantic import ValidationError

from flyin.models.link import Link


@pytest.mark.parametrize(
    "max_link_capacity",
    [1, 1506486106840656004],
)
def test_link_initialization_sets_attributes_correctly_given_valid_input(
    max_link_capacity,
):
    """Verify that a valid link can be created."""
    link = Link(max_link_capacity=max_link_capacity)
    assert link.max_link_capacity == max_link_capacity


def test_link_capacity_defaults_to_one_when_not_specified():
    """Ensure the default link capacity is set to 1."""
    link = Link()
    assert link.max_link_capacity == 1


@pytest.mark.parametrize("capacity", [-1, -100])
def test_link_enforces_non_negative_capacity_constraint(capacity):
    """Ensure that negative link capacities are rejected."""
    with pytest.raises(ValidationError):
        Link(max_link_capacity=capacity)


def test_link_accepts_exactly_zero_as_minimum_capacity():
    """Confirm that a capacity of zero is valid according to ge=0."""
    link = Link(max_link_capacity=0)
    assert link.max_link_capacity == 0
