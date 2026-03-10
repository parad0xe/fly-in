import pytest
from pydantic import ValidationError

from flyin.models.link import Link


def test_link_initializes_with_default_values():
    """Verify that a Link starts with zero drones and capacity of one."""
    link = Link()
    assert link.drones == 0
    assert link.max_link_capacity == 1


@pytest.mark.parametrize("field", ["drones", "max_link_capacity"])
def test_link_prevents_negative_values(field):
    """Ensure that drone count and capacity cannot be negative."""
    with pytest.raises(ValidationError):
        Link(**{field: -1})


def test_link_forbids_extra_fields():
    """Confirm that unknown attributes trigger a validation error."""
    with pytest.raises(ValidationError):
        Link(unknown_field="invalid")  # type: ignore


@pytest.mark.parametrize("capacity", [0, 100])
def test_link_accepts_valid_capacities(capacity):
    """Confirm that valid non-negative integers are accepted."""
    link = Link(max_link_capacity=capacity)
    assert link.max_link_capacity == capacity


def test_link_coerces_strings_to_integers():
    """Verify that Pydantic converts numeric strings to integers."""
    link = Link(max_link_capacity="10")  # type: ignore
    assert isinstance(link.drones, int)
    assert link.max_link_capacity == 10
