from __future__ import annotations

ARKO_EVENT_DATASET_NAME = "한국문화예술위원회_행사정보"
ARKO_EVENT_DATASET_URL = "https://www.culture.go.kr/data/openapi/openapiView.do?id=72&category=C&orderBy=rdfCnt&gubun=A"
ARKO_EVENT_API_BASE = "https://api.kcisa.kr/openapi/service/rest/meta"
ARKO_EVENT_ENDPOINT = "ARKeven"
ARKO_EVENT_OPERATION_PATH = "meta/ARKeven"
DEFAULT_ARKO_EVENT_SEARCH_LIMIT = 5
DEFAULT_ARKO_EVENT_LIST_LIMIT = 10

ARKO_EVENT_OUTPUT_FIELDS = [
    {"name": "title", "description": "자원의 명칭"},
    {"name": "alternativeTitle", "description": "대체 제목"},
    {"name": "creator", "description": "주된 책임을 진 개체"},
    {"name": "regDate", "description": "등록일"},
    {"name": "collectionDb", "description": "소속(통제) DB"},
    {"name": "subjectCategory", "description": "기관별 주제 분류 체계"},
    {"name": "subjectKeyword", "description": "핵심 주제어"},
    {"name": "extent", "description": "자원의 크기나 재생시간"},
    {"name": "description", "description": "내용"},
    {"name": "spatial", "description": "공간"},
    {"name": "temporalCoverage", "description": "해당 시간대"},
    {"name": "person", "description": "사람"},
    {"name": "language", "description": "언어"},
    {"name": "sourceTitle", "description": "참조 자원 제목"},
    {"name": "referenceIdentifier", "description": "참조 식별 정보(썸네일 이미지)"},
    {"name": "rights", "description": "자원에 대한 권리"},
    {"name": "copyrightOthers", "description": "저작권"},
    {"name": "url", "description": "지식정보 자원 위치 정보"},
    {"name": "uci", "description": "지식정보자원식별체계"},
    {"name": "contributor", "description": "기여자"},
]

ARKO_EVENT_SEARCH_FIELDS = (
    "title",
    "alternativeTitle",
    "creator",
    "subjectKeyword",
    "description",
    "spatial",
    "temporalCoverage",
    "sourceTitle",
    "contributor",
)

ARKO_EVENT_SUMMARY_FIELDS = (
    "title",
    "alternativeTitle",
    "creator",
    "regDate",
    "spatial",
    "temporalCoverage",
    "subjectKeyword",
    "url",
    "uci",
)

ARKO_EVENT_SORT_FIELDS = (
    "title",
    "creator",
    "regDate",
    "spatial",
    "temporalCoverage",
    "subjectKeyword",
)
