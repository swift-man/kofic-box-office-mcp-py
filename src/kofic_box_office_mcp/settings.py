from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional
from urllib import parse

from .arko_event_constants import ARKO_EVENT_API_BASE
from .constants import API_BASE, DEFAULT_TIMEOUT_SECONDS
from .exceptions import ArkoEventError, CultureOpenApiError, KoficBoxOfficeError, McstPerformanceError
from .mcst_performance_constants import MCST_PERFORMANCE_API_BASE


@dataclass(frozen=True)
class ServiceKeyConfig:
    raw_key: Optional[str] = None
    encoded_key: Optional[str] = None

    @classmethod
    def from_env(
        cls,
        *,
        raw_key_var: str,
        encoded_key_var: str,
        error_cls: type[CultureOpenApiError],
        dataset_label: str,
    ) -> "ServiceKeyConfig":
        raw_key = os.getenv(raw_key_var)
        encoded_key = os.getenv(encoded_key_var)
        if not raw_key and not encoded_key:
            raise error_cls(
                f"Set {raw_key_var} or {encoded_key_var} before using {dataset_label}."
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
            service_key=ServiceKeyConfig.from_env(
                raw_key_var="KOFIC_BOX_OFFICE_SERVICE_KEY",
                encoded_key_var="KOFIC_BOX_OFFICE_SERVICE_KEY_ENCODED",
                error_cls=KoficBoxOfficeError,
                dataset_label="the KOFIC box-office dataset",
            ),
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
            service_key=ServiceKeyConfig.from_env(
                raw_key_var="ARKO_EVENT_SERVICE_KEY",
                encoded_key_var="ARKO_EVENT_SERVICE_KEY_ENCODED",
                error_cls=ArkoEventError,
                dataset_label="the ARKO event dataset",
            ),
            api_base=api_base,
            timeout_seconds=timeout_seconds,
        )


@dataclass(frozen=True)
class McstPerformanceSettings:
    service_key: ServiceKeyConfig
    api_base: str = MCST_PERFORMANCE_API_BASE
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls) -> "McstPerformanceSettings":
        api_base = os.getenv("MCST_PERFORMANCE_API_BASE", MCST_PERFORMANCE_API_BASE).rstrip("/")
        timeout_raw = os.getenv("MCST_PERFORMANCE_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))

        try:
            timeout_seconds = float(timeout_raw)
        except ValueError as exc:
            raise McstPerformanceError("MCST_PERFORMANCE_TIMEOUT_SECONDS must be numeric.") from exc

        return cls(
            service_key=ServiceKeyConfig.from_env(
                raw_key_var="MCST_PERFORMANCE_SERVICE_KEY",
                encoded_key_var="MCST_PERFORMANCE_SERVICE_KEY_ENCODED",
                error_cls=McstPerformanceError,
                dataset_label="the MCST culture-art performance dataset",
            ),
            api_base=api_base,
            timeout_seconds=timeout_seconds,
        )
