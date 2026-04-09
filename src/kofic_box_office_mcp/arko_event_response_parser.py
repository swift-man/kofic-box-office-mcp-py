from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Protocol

from .arko_event_constants import ARKO_EVENT_DATASET_NAME, ARKO_EVENT_DATASET_URL, ARKO_EVENT_OPERATION_PATH
from .constants import KNOWN_RESULT_MESSAGES, SUCCESS_RESULT_CODES
from .exceptions import ArkoEventError


class ArkoEventResponseParserProtocol(Protocol):
    def parse(
        self,
        *,
        operation: str,
        query_params: Mapping[str, Any],
        status_code: int,
        raw_body: str,
        content_type: str,
    ) -> Dict[str, Any]:
        """Parse and normalize an ARKO event API response."""


@dataclass(frozen=True)
class ArkoEventResponseParser:
    def parse(
        self,
        *,
        operation: str,
        query_params: Mapping[str, Any],
        status_code: int,
        raw_body: str,
        content_type: str,
    ) -> Dict[str, Any]:
        payload = parse_payload(raw_body=raw_body, content_type=content_type)
        return normalize_api_payload(
            operation=operation,
            query_params=query_params,
            status_code=status_code,
            payload=payload,
        )


def default_arko_event_response_parser() -> ArkoEventResponseParserProtocol:
    return ArkoEventResponseParser()


def parse_payload(*, raw_body: str, content_type: str) -> Dict[str, Any]:
    content_type_lower = content_type.lower()

    if "json" in content_type_lower:
        return _parse_json(raw_body)

    if "xml" in content_type_lower:
        return _parse_xml(raw_body)

    stripped = raw_body.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return _parse_json(raw_body)
    if stripped.startswith("<"):
        return _parse_xml(raw_body)

    raise ArkoEventError("Expected JSON or XML from the ARKO event API but received a different payload.")


def normalize_api_payload(
    *,
    operation: str,
    query_params: Mapping[str, Any],
    status_code: int,
    payload: Mapping[str, Any],
) -> Dict[str, Any]:
    plain_payload = to_plain_data(payload)
    response = _as_mapping(plain_payload.get("response"))
    header = _as_mapping(response.get("header"))
    body = _as_mapping(response.get("body"))

    result_code = str(header.get("resultCode", "")).strip()
    result_message = str(header.get("resultMsg", "")).strip()
    if result_code and result_code not in SUCCESS_RESULT_CODES:
        friendly_message = result_message or KNOWN_RESULT_MESSAGES.get(result_code) or "Unknown API error"
        raise ArkoEventError(f"ARKO event API error {result_code}: {friendly_message}")

    normalized_body = normalize_response_body(body)

    return {
        "dataset": ARKO_EVENT_DATASET_NAME,
        "dataset_url": ARKO_EVENT_DATASET_URL,
        "operation": operation,
        "operation_path": ARKO_EVENT_OPERATION_PATH if not operation else operation,
        "http_status": status_code,
        "request_params": dict(query_params),
        "result": {
            "code": result_code or None,
            "message": result_message or KNOWN_RESULT_MESSAGES.get(result_code),
        },
        "response_header": header,
        "response_body": normalized_body,
        "page_no": _coerce_optional_int(body.get("pageNo")),
        "num_of_rows": _coerce_optional_int(body.get("numOfRows")),
        "total_count": _coerce_optional_int(body.get("totalCount")),
        "items": normalized_body.get("items", []),
        "api_payload": plain_payload,
    }


def normalize_response_body(body: Mapping[str, Any]) -> Dict[str, Any]:
    normalized_body = dict(body)
    normalized_body["items"] = normalize_items(body.get("items"))
    return normalized_body


def normalize_items(items: Any) -> list[Any]:
    if items in (None, "", {}):
        return []
    if isinstance(items, list):
        return items
    if isinstance(items, dict):
        nested = items.get("item")
        if nested is None:
            return [items]
        if isinstance(nested, list):
            return nested
        if nested in (None, "", {}):
            return []
        return [nested]
    return [items]


def to_plain_data(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: to_plain_data(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [to_plain_data(item) for item in value]
    return value


def _parse_json(raw_body: str) -> Dict[str, Any]:
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise ArkoEventError("Failed to decode JSON returned by the ARKO event API.") from exc

    if not isinstance(payload, dict):
        raise ArkoEventError("Expected a JSON object from the ARKO event API.")
    return payload


def _parse_xml(raw_body: str) -> Dict[str, Any]:
    try:
        root = ET.fromstring(raw_body)
    except ET.ParseError as exc:
        raise ArkoEventError("Failed to decode XML returned by the ARKO event API.") from exc

    return {root.tag: _xml_element_to_data(root)}


def _xml_element_to_data(element: ET.Element) -> Any:
    children = list(element)
    if not children:
        return (element.text or "").strip()

    grouped: dict[str, list[Any]] = {}
    for child in children:
        grouped.setdefault(child.tag, []).append(_xml_element_to_data(child))

    result: dict[str, Any] = {}
    for key, values in grouped.items():
        result[key] = values[0] if len(values) == 1 else values
    return result


def _as_mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _coerce_optional_int(value: Any) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
