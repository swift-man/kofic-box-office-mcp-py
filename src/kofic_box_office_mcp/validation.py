from __future__ import annotations

from typing import Optional, Sequence

from .exceptions import CultureOpenApiError


def require_text(name: str, value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise CultureOpenApiError(f"{name} must not be blank.")
    return normalized


def validate_positive_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CultureOpenApiError(f"{name} must be an integer.")
    if value < 1:
        raise CultureOpenApiError(f"{name} must be greater than or equal to 1.")


def validate_optional_positive_int(name: str, value: Optional[int]) -> Optional[int]:
    if value is None:
        return None

    validate_positive_int(name, value)
    return value


def normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None


def validate_choice(name: str, value: str, allowed_values: Sequence[str]) -> str:
    if value not in allowed_values:
        formatted_values = ", ".join(allowed_values)
        raise CultureOpenApiError(f"{name} must be one of: {formatted_values}.")
    return value
