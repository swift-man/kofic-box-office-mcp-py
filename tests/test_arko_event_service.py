import unittest

from kofic_box_office_mcp.arko_event_constants import ARKO_EVENT_ENDPOINT
from kofic_box_office_mcp.arko_event_reference import build_arko_event_reference_payload
from kofic_box_office_mcp.arko_event_service import ArkoEventService
from kofic_box_office_mcp.exceptions import ArkoEventError, CultureOpenApiError


class FakeArkoGateway:
    def __init__(self):
        self.calls = []

    def request(self, operation, params):
        self.calls.append((operation, params))
        return {
            "dataset": "한국문화예술위원회_행사정보",
            "dataset_url": "https://www.culture.go.kr/data/openapi/openapiView.do?id=72&category=C&orderBy=rdfCnt&gubun=A",
            "operation": operation,
            "operation_path": operation,
            "request_params": params,
            "page_no": params["pageNo"],
            "num_of_rows": params["numOfRows"],
            "total_count": 3,
            "items": [
                {
                    "title": "예술 행사 A",
                    "alternativeTitle": "Event A",
                    "creator": "한국문화예술위원회",
                    "regDate": "2024-05-02",
                    "spatial": "서울",
                    "temporalCoverage": "2024-05",
                    "subjectKeyword": "전시",
                    "url": "https://example.com/a",
                    "uci": "uci-a",
                },
                {
                    "title": "예술 행사 B",
                    "creator": "지역문화재단",
                    "regDate": "2023-08-14",
                    "spatial": "부산",
                    "temporalCoverage": "2023-08",
                    "subjectKeyword": "공연",
                    "url": "https://example.com/b",
                    "uci": "uci-b",
                },
                {
                    "title": "예술 행사 C",
                    "creator": "한국문화예술위원회",
                    "regDate": "2024-01-11",
                    "spatial": "서울",
                    "temporalCoverage": "2024-01",
                    "subjectKeyword": "지원사업설명회",
                    "url": "https://example.com/c",
                    "uci": "uci-c",
                },
            ],
        }


class ArkoEventServiceTests(unittest.TestCase):
    def setUp(self):
        self.gateway = FakeArkoGateway()
        self.service = ArkoEventService(gateway=self.gateway)

    def test_get_arko_events_delegates_to_gateway(self):
        result = self.service.get_arko_events(page_no=2, num_of_rows=25)

        self.assertEqual(ARKO_EVENT_ENDPOINT, result["operation"])
        self.assertEqual(
            {
                "pageNo": 2,
                "numOfRows": 25,
            },
            result["request_params"],
        )
        self.assertEqual(3, result["returned_count"])

    def test_get_arko_events_rejects_invalid_page(self):
        with self.assertRaises(CultureOpenApiError):
            self.service.get_arko_events(page_no=0)

    def test_get_arko_events_filters_and_sorts_items(self):
        result = self.service.get_arko_events(
            spatial="서울",
            creator="한국문화예술",
            sort_by="regDate",
            sort_order="desc",
            limit=1,
        )

        self.assertEqual(3, result["source_item_count"])
        self.assertEqual(1, result["returned_count"])
        self.assertEqual("예술 행사 A", result["items"][0]["title"])
        self.assertEqual({"creator": "한국문화예술", "spatial": "서울"}, result["applied_filters"])
        self.assertEqual({"by": "regDate", "order": "desc"}, result["applied_sort"])

    def test_search_arko_events_requires_query(self):
        with self.assertRaises(CultureOpenApiError):
            self.service.search_arko_events("  ")

    def test_search_arko_events_returns_compact_summaries(self):
        result = self.service.search_arko_events("행사", limit=2)

        self.assertEqual("search_arko_events", result["tool"])
        self.assertEqual("행사", result["query"])
        self.assertEqual(2, result["returned_count"])
        self.assertEqual("예술 행사 A", result["items"][0]["title"])
        self.assertIn("title", result["match_fields"])

    def test_list_arko_event_titles_returns_summary_fields(self):
        result = self.service.list_arko_event_titles(limit=2)

        self.assertEqual("list_arko_event_titles", result["tool"])
        self.assertEqual(2, result["returned_count"])
        self.assertEqual("예술 행사 A", result["items"][0]["title"])
        self.assertIn("uci", result["summary_fields"])

    def test_reference_payload_lists_supported_tool(self):
        payload = build_arko_event_reference_payload()

        self.assertEqual("한국문화예술위원회_행사정보", payload["dataset"])
        self.assertEqual(
            [
                "get_arko_events",
                "search_arko_events",
                "list_arko_event_titles",
            ],
            [tool["name"] for tool in payload["tools"]],
        )
        self.assertEqual(20, len(payload["output_fields"]))


if __name__ == "__main__":
    unittest.main()
