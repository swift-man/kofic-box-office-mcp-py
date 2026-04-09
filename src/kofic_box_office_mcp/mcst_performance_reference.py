from __future__ import annotations

from .constants import BOX_OFFICE_SORT_ORDERS
from .mcst_performance_constants import (
    MCST_PERFORMANCE_DATASET_NAME,
    MCST_PERFORMANCE_DATASET_URL,
    MCST_PERFORMANCE_DTYPE_CHOICES,
    MCST_PERFORMANCE_ENDPOINT,
    MCST_PERFORMANCE_OUTPUT_FIELDS,
    MCST_PERFORMANCE_SEARCH_FIELDS,
    MCST_PERFORMANCE_SORT_FIELDS,
    MCST_PERFORMANCE_SUMMARY_FIELDS,
)


def build_mcst_performance_reference_payload() -> dict:
    return {
        "dataset": MCST_PERFORMANCE_DATASET_NAME,
        "dataset_url": MCST_PERFORMANCE_DATASET_URL,
        "api_endpoint": MCST_PERFORMANCE_ENDPOINT,
        "transport": "streamable-http",
        "tools": [
            {
                "name": "get_mcst_performances",
                "description": "Fetch MCST culture-art performance records and optionally apply local filtering, sorting, and limiting.",
                "inputs": {
                    "dtype": {"type": "string", "required": True, "enum": list(MCST_PERFORMANCE_DTYPE_CHOICES)},
                    "title": {"type": "string", "required": True, "minLength": 2},
                    "page_no": {"type": "integer", "default": 1, "minimum": 1},
                    "num_of_rows": {"type": "integer", "default": 10, "minimum": 1},
                    "event_site": {"type": "string", "required": False},
                    "period": {"type": "string", "required": False},
                    "limit": {"type": "integer", "required": False, "minimum": 1},
                    "sort_by": {"type": "string", "required": False, "enum": list(MCST_PERFORMANCE_SORT_FIELDS)},
                    "sort_order": {"type": "string", "required": False, "enum": list(BOX_OFFICE_SORT_ORDERS)},
                },
                "notes": [
                    "dtype and title are sent to the upstream API. event_site, period, limit, sort_by, and sort_order are applied by this MCP server after fetching the upstream page."
                ],
            },
            {
                "name": "search_mcst_performances",
                "description": "Search MCST culture-art performances with dtype and title, then return compact summaries.",
                "inputs": {
                    "dtype": {"type": "string", "required": True, "enum": list(MCST_PERFORMANCE_DTYPE_CHOICES)},
                    "title": {"type": "string", "required": True, "minLength": 2},
                    "page_no": {"type": "integer", "default": 1, "minimum": 1},
                    "num_of_rows": {"type": "integer", "default": 10, "minimum": 1},
                    "limit": {"type": "integer", "default": 5, "minimum": 1},
                },
            },
            {
                "name": "list_mcst_performance_titles",
                "description": "Return a compact list of titles from a fetched MCST culture-art performance result page.",
                "inputs": {
                    "dtype": {"type": "string", "required": True, "enum": list(MCST_PERFORMANCE_DTYPE_CHOICES)},
                    "title": {"type": "string", "required": True, "minLength": 2},
                    "page_no": {"type": "integer", "default": 1, "minimum": 1},
                    "num_of_rows": {"type": "integer", "default": 10, "minimum": 1},
                    "limit": {"type": "integer", "default": 10, "minimum": 1},
                },
            },
        ],
        "output_fields": list(MCST_PERFORMANCE_OUTPUT_FIELDS),
        "search_fields": list(MCST_PERFORMANCE_SEARCH_FIELDS),
        "summary_fields": list(MCST_PERFORMANCE_SUMMARY_FIELDS),
        "sort_fields": list(MCST_PERFORMANCE_SORT_FIELDS),
        "dtype_choices": list(MCST_PERFORMANCE_DTYPE_CHOICES),
        "message_codes": {
            "0000": "정상 처리",
            "F2013": "서비스 주소 호출 실패",
            "9999": "서비스 점검중(내부 서비스 호출 장애)",
        },
    }
