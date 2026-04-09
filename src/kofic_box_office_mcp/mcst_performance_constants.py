from __future__ import annotations

MCST_PERFORMANCE_DATASET_NAME = "문화체육관광부_문화예술공연(통합)"
MCST_PERFORMANCE_DATASET_URL = (
    "https://www.culture.go.kr/data/openapi/openapiView.do?id=580&category=A&orderBy=rdfCnt&gubun=A"
)
MCST_PERFORMANCE_API_BASE = "https://api.kcisa.kr/openapi/CNV_060"
MCST_PERFORMANCE_ENDPOINT = "request"
MCST_PERFORMANCE_OPERATION_PATH = "CNV_060/request"
DEFAULT_MCST_PERFORMANCE_SEARCH_LIMIT = 5
DEFAULT_MCST_PERFORMANCE_LIST_LIMIT = 10

MCST_PERFORMANCE_DTYPE_CHOICES = (
    "연극",
    "뮤지컬",
    "오페라",
    "음악",
    "콘서트",
    "국악",
    "무용",
    "전시",
    "기타",
)

MCST_PERFORMANCE_OUTPUT_FIELDS = [
    {"name": "title", "description": "제목"},
    {"name": "type", "description": "분야"},
    {"name": "period", "description": "기간"},
    {"name": "eventPeriod", "description": "시간"},
    {"name": "eventSite", "description": "장소"},
    {"name": "charge", "description": "금액"},
    {"name": "contactPoint", "description": "문의안내"},
    {"name": "url", "description": "URL"},
    {"name": "imageObject", "description": "이미지(썸네일)"},
    {"name": "description", "description": "설명"},
    {"name": "viewCount", "description": "조회수"},
]

MCST_PERFORMANCE_SEARCH_FIELDS = (
    "title",
    "type",
    "period",
    "eventPeriod",
    "eventSite",
    "charge",
    "contactPoint",
    "description",
)

MCST_PERFORMANCE_SUMMARY_FIELDS = (
    "title",
    "type",
    "period",
    "eventPeriod",
    "eventSite",
    "charge",
    "url",
    "imageObject",
    "viewCount",
)

MCST_PERFORMANCE_SORT_FIELDS = (
    "title",
    "type",
    "period",
    "eventPeriod",
    "eventSite",
    "charge",
    "viewCount",
)
