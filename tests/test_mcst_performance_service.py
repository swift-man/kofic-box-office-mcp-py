import unittest

from kofic_box_office_mcp.exceptions import CultureOpenApiError, McstPerformanceError
from kofic_box_office_mcp.mcst_performance_constants import MCST_PERFORMANCE_ENDPOINT
from kofic_box_office_mcp.mcst_performance_reference import build_mcst_performance_reference_payload
from kofic_box_office_mcp.mcst_performance_service import McstPerformanceService


class FakeMcstPerformanceGateway:
    def __init__(self):
        self.calls = []

    def request(self, operation, params):
        self.calls.append((operation, params))
        return {
            "dataset": "문화체육관광부_문화예술공연(통합)",
            "dataset_url": "https://www.culture.go.kr/data/openapi/openapiView.do?id=580&category=A&orderBy=rdfCnt&gubun=A",
            "operation": operation,
            "operation_path": "CNV_060/request",
            "request_params": params,
            "page_no": params["pageNo"],
            "num_of_rows": params["numOfRows"],
            "total_count": 3,
            "items": [
                {
                    "title": "전시 A",
                    "type": "전시",
                    "period": "2026-04-01~2026-05-01",
                    "eventPeriod": "10:00~18:00",
                    "eventSite": "서울미술관",
                    "charge": "10000",
                    "contactPoint": "02-111-2222",
                    "url": "https://example.com/a",
                    "imageObject": "https://example.com/a.jpg",
                    "description": "서울 전시",
                    "viewCount": "300",
                },
                {
                    "title": "전시 B",
                    "type": "전시",
                    "period": "2026-03-01~2026-03-15",
                    "eventPeriod": "09:00~17:00",
                    "eventSite": "부산전시관",
                    "charge": "무료",
                    "contactPoint": "051-111-2222",
                    "url": "https://example.com/b",
                    "imageObject": "https://example.com/b.jpg",
                    "description": "부산 전시",
                    "viewCount": "150",
                },
                {
                    "title": "전시 C",
                    "type": "전시",
                    "period": "2026-06-01~2026-06-30",
                    "eventPeriod": "11:00~19:00",
                    "eventSite": "서울갤러리",
                    "charge": "12000",
                    "contactPoint": "02-333-4444",
                    "url": "https://example.com/c",
                    "imageObject": "https://example.com/c.jpg",
                    "description": "서울 현대미술 전시",
                    "viewCount": "420",
                },
            ],
        }


class McstPerformanceServiceTests(unittest.TestCase):
    def setUp(self):
        self.gateway = FakeMcstPerformanceGateway()
        self.service = McstPerformanceService(gateway=self.gateway)

    def test_get_mcst_performances_delegates_to_gateway(self):
        result = self.service.get_mcst_performances(dtype="전시", title="전시", page_no=2, num_of_rows=25)

        self.assertEqual(MCST_PERFORMANCE_ENDPOINT, result["operation"])
        self.assertEqual(
            {
                "dtype": "전시",
                "title": "전시",
                "pageNo": 2,
                "numOfRows": 25,
            },
            result["request_params"],
        )
        self.assertEqual(3, result["returned_count"])

    def test_get_mcst_performances_rejects_invalid_title(self):
        with self.assertRaises(McstPerformanceError):
            self.service.get_mcst_performances(dtype="전시", title="가")

    def test_get_mcst_performances_rejects_invalid_page(self):
        with self.assertRaises(CultureOpenApiError):
            self.service.get_mcst_performances(dtype="전시", title="전시", page_no=0)

    def test_get_mcst_performances_filters_and_sorts_items(self):
        result = self.service.get_mcst_performances(
            dtype="전시",
            title="전시",
            event_site="서울",
            sort_by="viewCount",
            sort_order="desc",
            limit=1,
        )

        self.assertEqual(3, result["source_item_count"])
        self.assertEqual(1, result["returned_count"])
        self.assertEqual("전시 C", result["items"][0]["title"])
        self.assertEqual({"event_site": "서울"}, result["applied_filters"])
        self.assertEqual({"by": "viewCount", "order": "desc"}, result["applied_sort"])

    def test_search_mcst_performances_returns_compact_summaries(self):
        result = self.service.search_mcst_performances(dtype="전시", title="전시", limit=2)

        self.assertEqual("search_mcst_performances", result["tool"])
        self.assertEqual("전시", result["dtype"])
        self.assertEqual("전시", result["title"])
        self.assertEqual(2, result["returned_count"])
        self.assertEqual("전시 A", result["items"][0]["title"])
        self.assertIn("eventSite", result["match_fields"])

    def test_list_mcst_performance_titles_returns_summary_fields(self):
        result = self.service.list_mcst_performance_titles(dtype="전시", title="전시", limit=2)

        self.assertEqual("list_mcst_performance_titles", result["tool"])
        self.assertEqual(2, result["returned_count"])
        self.assertEqual("전시 A", result["items"][0]["title"])
        self.assertIn("imageObject", result["summary_fields"])

    def test_reference_payload_lists_supported_tools(self):
        payload = build_mcst_performance_reference_payload()

        self.assertEqual("문화체육관광부_문화예술공연(통합)", payload["dataset"])
        self.assertEqual(
            [
                "get_mcst_performances",
                "search_mcst_performances",
                "list_mcst_performance_titles",
            ],
            [tool["name"] for tool in payload["tools"]],
        )
        self.assertEqual(11, len(payload["output_fields"]))


if __name__ == "__main__":
    unittest.main()
