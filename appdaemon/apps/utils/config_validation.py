"""Define methods to validate configuration for voluptuous."""

import datetime
from typing import Any, Sequence, TypeVar, Union

import voluptuous as vol

T = TypeVar("T")  # pylint: disable=invalid-name


def ensure_list(value: Union[T, Sequence[T]]) -> Sequence[T]:
    """Validate if a given object is a list."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def entity_id(value: Any) -> str:
    """Validate if a given object is an entity ID."""
    value = str(value).lower()
    if "." in value:
        return value

    raise vol.Invalid("Invalid entity ID: {0}".format(value))


def valid_date(value: Any) -> datetime.date:
    """Validate if a given object is a date."""
    try:
        return datetime.datetime.strptime(value, "%d.%m.%Y")
    except ValueError:
        raise vol.Invalid(f"Invalid Date: {value}")


def valid_time(value: Any) -> datetime.datetime:
    """Validate if a given object is a time."""
    try:
        return datetime.datetime.strptime(value, "%H:%M:%S")
    except ValueError:
        raise vol.Invalid(f"Invalid Time: {value}")

