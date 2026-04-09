from __future__ import annotations

DATASET_NAME = "영화진흥위원회_박스오피스"
DATASET_URL = "https://www.culture.go.kr/data/openapi/openapiView.do?id=203"
API_BASE = "https://api.kcisa.kr/openapi/service/rest/meta5"
BOX_OFFICE_ENDPOINT = "getKFCC0502"
DEFAULT_TIMEOUT_SECONDS = 15.0
DEFAULT_NUM_OF_ROWS = 10
DEFAULT_PAGE_NO = 1

SUCCESS_RESULT_CODES = {"0000", "00"}
KNOWN_RESULT_MESSAGES = {
    "0000": "정상 처리",
    "F2013": "서비스 주소 호출 실패",
    "9999": "서비스 점검중(내부 서비스 호출 장애)",
}

BOX_OFFICE_OUTPUT_FIELDS = [
    {"name": "title", "description": "자원의 명칭"},
    {"name": "alternativeTitle", "description": "대체 제목"},
    {"name": "creator", "description": "주된 책임을 진 개체"},
    {"name": "regDate", "description": "등록일"},
    {"name": "collectionDb", "description": "소속(통제) DB"},
    {"name": "subjectCategory", "description": "기관별 주제 분류 체계"},
    {"name": "subjectKeyword", "description": "핵심 주제어"},
    {"name": "extent", "description": "자원의 크기나 재생시간"},
    {"name": "description", "description": "내용"},
    {"name": "spatialCoverage", "description": "관련 장소"},
    {"name": "temporal", "description": "시간적 범위"},
    {"name": "person", "description": "사람"},
    {"name": "language", "description": "언어"},
    {"name": "sourceTitle", "description": "참조 자원 제목"},
    {"name": "referenceIdentifier", "description": "참조 식별 정보(썸네일 이미지)"},
    {"name": "rights", "description": "자원에 대한 권리"},
    {"name": "copyrightOthers", "description": "저작권"},
    {"name": "url", "description": "지식정보 자원 위치 정보"},
    {"name": "contributor", "description": "기여자"},
]
