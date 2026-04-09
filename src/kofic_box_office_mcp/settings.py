from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional
from urllib import parse

from .arko_event_constants import ARKO_EVENT_API_BASE
from .constants import API_BASE, DEFAULT_TIMEOUT_SECONDS
from .exceptions import CultureOpenApiError, KoficBoxOfficeError


@dataclass(frozen=True)
class ServiceKeyConfig:
    raw_key: Optional[str] = None
    encoded_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "ServiceKeyConfig":
        raw_key = os.getenv("CULTURE_OPEN_API_SERVICE_KEY") or os.getenv("KOFIC_BOX_OFFICE_SERVICE_KEY")
        encoded_key = os.getenv("CULTURE_OPEN_API_SERVICE_KEY_ENCODED") or os.getenv("KOFIC_BOX_OFFICE_SERVICE_KEY_ENCODED")
        if not raw_key and not encoded_key:
            raise CultureOpenApiError(
                "Set CULTURE_OPEN_API_SERVICE_KEY or CULTURE_OPEN_API_SERVICE_KEY_ENCODED before starting the server. "
                "The existing KOFIC_BOX_OFFICE_SERVICE_KEY aliases are also supported."
            )
        return cls(raw_key=raw_key, encoded_key=encoded_key)

    def to_query_segment(self) -> str:
        if self.encoded_key:
            return f"serviceKey={self.encoded_key}"

        assert self.raw_key is not None
        return f"serviceKey={parse.quote(self.raw_key, safe='')}"


@dataclass(frozen=True)
class KoficBoxOfficeSettings:
    service_key: ServiceKeyConfig
    api_base: str = API_BASE
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls) -> "KoficBoxOfficeSettings":
        api_base = os.getenv("KOFIC_BOX_OFFICE_API_BASE", API_BASE).rstrip("/")
        timeout_raw = os.getenv("KOFIC_BOX_OFFICE_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))

        try:
            timeout_seconds = float(timeout_raw)
        except ValueError as exc:
            raise KoficBoxOfficeError("KOFIC_BOX_OFFICE_TIMEOUT_SECONDS must be numeric.") from exc

        return cls(
            service_key=ServiceKeyConfig.from_env(),
            api_base=api_base,
            timeout_seconds=timeout_seconds,
        )


@dataclass(frozen=True)
class ArkoEventSettings:
    service_key: ServiceKeyConfig
    api_base: str = ARKO_EVENT_API_BASE
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls) -> "ArkoEventSettings":
        api_base = os.getenv("ARKO_EVENT_API_BASE", ARKO_EVENT_API_BASE).rstrip("/")
        timeout_raw = os.getenv("ARKO_EVENT_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))

        try:
            timeout_seconds = float(timeout_raw)
        except ValueError as exc:
            raise CultureOpenApiError("ARKO_EVENT_TIMEOUT_SECONDS must be numeric.") from exc

        return cls(
            service_key=ServiceKeyConfig.from_env(),
            api_base=api_base,
            timeout_seconds=timeout_seconds,
        )
