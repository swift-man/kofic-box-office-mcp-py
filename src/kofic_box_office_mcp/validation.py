from __future__ import annotations

from .exceptions import KoficBoxOfficeError


def require_text(name: str, value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise KoficBoxOfficeError(f"{name} must not be blank.")
    return normalized


def validate_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int):
        raise KoficBoxOfficeError(f"{name} must be an integer.")
    if value < 1:
        raise KoficBoxOfficeError(f"{name} must be greater than or equal to 1.")
