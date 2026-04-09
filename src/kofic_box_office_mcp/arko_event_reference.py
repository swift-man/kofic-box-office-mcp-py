from __future__ import annotations

from .arko_event_constants import (
    ARKO_EVENT_ENDPOINT,
    ARKO_EVENT_OUTPUT_FIELDS,
    ARKO_EVENT_SEARCH_FIELDS,
    ARKO_EVENT_SORT_FIELDS,
    ARKO_EVENT_SUMMARY_FIELDS,
    ARKO_EVENT_DATASET_NAME,
    ARKO_EVENT_DATASET_URL,
)
from .constants import BOX_OFFICE_SORT_ORDERS


def build_arko_event_reference_payload() -> dict:
    return {
        "dataset": ARKO_EVENT_DATASET_NAME,
        "dataset_url": ARKO_EVENT_DATASET_URL,
        "api_endpoint": ARKO_EVENT_ENDPOINT,
        "transport": "streamable-http",
        "tools": [
            {
                "name": "get_arko_events",
                "description": "Fetch an ARKO event page and optionally apply local filtering, sorting, and limiting.",
                "inputs": {
                    "page_no": {"type": "integer", "default": 1, "minimum": 1},
                    "num_of_rows": {"type": "integer", "default": 10, "minimum": 1},
                    "query": {"type": "string", "required": False},
                    "creator": {"type": "string", "required": False},
                    "spatial": {"type": "string", "required": False},
                    "subject_keyword": {"type": "string", "required": False},
                    "limit": {"type": "integer", "required": False, "minimum": 1},
                    "sort_by": {"type": "string", "required": False, "enum": list(ARKO_EVENT_SORT_FIELDS)},
                    "sort_order": {"type": "string", "required": False, "enum": list(BOX_OFFICE_SORT_ORDERS)},
                },
                "notes": [
                    "query, creator, spatial, subject_keyword, limit, sort_by, and sort_order are applied by this MCP server after fetching the upstream page."
                ],
            },
            {
                "name": "search_arko_events",
                "description": "Search within a fetched ARKO event page and return compact summaries.",
                "inputs": {
                    "query": {"type": "string", "required": True},
                    "page_no": {"type": "integer", "default": 1, "minimum": 1},
                    "num_of_rows": {"type": "integer", "default": 10, "minimum": 1},
                    "limit": {"type": "integer", "default": 5, "minimum": 1},
                },
            },
            {
                "name": "list_arko_event_titles",
                "description": "Return a compact list of titles from a fetched ARKO event page.",
                "inputs": {
                    "page_no": {"type": "integer", "default": 1, "minimum": 1},
                    "num_of_rows": {"type": "integer", "default": 10, "minimum": 1},
                    "limit": {"type": "integer", "default": 10, "minimum": 1},
                },
            },
        ],
        "output_fields": list(ARKO_EVENT_OUTPUT_FIELDS),
        "search_fields": list(ARKO_EVENT_SEARCH_FIELDS),
        "summary_fields": list(ARKO_EVENT_SUMMARY_FIELDS),
        "sort_fields": list(ARKO_EVENT_SORT_FIELDS),
        "message_codes": {
            "0000": "정상 처리",
            "F2013": "서비스 주소 호출 실패",
            "9999": "서비스 점검중(내부 서비스 호출 장애)",
        },
    }
