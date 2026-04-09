from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Protocol
from urllib import error, parse, request

from .exceptions import KoficBoxOfficeError
from .response_parser import KoficBoxOfficeResponseParser, ResponseParser
from .settings import KoficBoxOfficeSettings


class KoficBoxOfficeGateway(Protocol):
    def request(self, operation: str, params: Mapping[str, Any]) -> Dict[str, Any]:
        """Fetch normalized data from the KOFIC box-office API."""


@dataclass(frozen=True)
class UrllibKoficBoxOfficeGateway:
    settings: KoficBoxOfficeSettings
    response_parser: ResponseParser
    user_agent: str = "kofic-box-office-mcp/0.1.0"

    def request(self, operation: str, params: Mapping[str, Any]) -> Dict[str, Any]:
        query_params = {key: value for key, value in params.items() if value is not None}
        url = f"{self.settings.api_base}/{operation}?{self._build_query(query_params)}"
        http_request = request.Request(
            url,
            headers={
                "Accept": "application/json, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.1",
                "User-Agent": self.user_agent,
            },
        )

        try:
            with request.urlopen(http_request, timeout=self.settings.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8", "replace")
                status_code = response.status
                content_type = response.headers.get("Content-Type", "")
        except error.HTTPError as exc:
            raw_body = exc.read().decode("utf-8", "replace")
            message = raw_body.strip() or exc.reason
            raise KoficBoxOfficeError(f"KOFIC box-office API returned HTTP {exc.code}: {message}") from exc
        except error.URLError as exc:
            raise KoficBoxOfficeError(f"KOFIC box-office API request failed: {exc.reason}") from exc

        return self.response_parser.parse(
            operation=operation,
            query_params=query_params,
            status_code=status_code,
            raw_body=raw_body,
            content_type=content_type,
        )

    def _build_query(self, params: Mapping[str, Any]) -> str:
        segments = [self.settings.service_key.to_query_segment()]
        for key, value in params.items():
            encoded_key = parse.quote(str(key), safe="")
            encoded_value = parse.quote(str(value), safe="")
            segments.append(f"{encoded_key}={encoded_value}")
        return "&".join(segments)


def default_response_parser() -> ResponseParser:
    return KoficBoxOfficeResponseParser()
