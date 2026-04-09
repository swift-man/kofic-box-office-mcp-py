from __future__ import annotations

from .constants import BOX_OFFICE_ENDPOINT, BOX_OFFICE_OUTPUT_FIELDS, DATASET_NAME, DATASET_URL


def build_reference_payload() -> dict:
    return {
        "dataset": DATASET_NAME,
        "dataset_url": DATASET_URL,
        "api_endpoint": BOX_OFFICE_ENDPOINT,
        "transport": "streamable-http",
        "tools": [
            {
                "name": "get_kofic_box_office",
                "description": "Fetch KOFIC box-office records from the KOFIC box-office API.",
                "inputs": {
                    "page_no": {"type": "integer", "default": 1, "minimum": 1},
                    "num_of_rows": {"type": "integer", "default": 10, "minimum": 1},
                },
            }
        ],
        "output_fields": list(BOX_OFFICE_OUTPUT_FIELDS),
        "message_codes": {
            "0000": "정상 처리",
            "F2013": "서비스 주소 호출 실패",
            "9999": "서비스 점검중(내부 서비스 호출 장애)",
        },
    }
