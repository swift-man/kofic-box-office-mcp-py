import unittest

from kofic_box_office_mcp.constants import BOX_OFFICE_ENDPOINT
from kofic_box_office_mcp.exceptions import CultureOpenApiError, KoficBoxOfficeError
from kofic_box_office_mcp.reference import build_reference_payload
from kofic_box_office_mcp.service import KoficBoxOfficeService


class FakeGateway:
    def __init__(self):
        self.calls = []

    def request(self, operation, params):
        self.calls.append((operation, params))
        return {
            "dataset": "영화진흥위원회_박스오피스",
            "dataset_url": "https://www.culture.go.kr/data/openapi/openapiView.do?id=203",
            "operation": operation,
            "operation_path": operation,
            "request_params": params,
            "page_no": params["pageNo"],
            "num_of_rows": params["numOfRows"],
            "total_count": 3,
            "items": [
                {
                    "title": "영화 A",
                    "alternativeTitle": "Movie A",
                    "creator": "영화진흥위원회",
                    "regDate": "2024-01-02",
                    "collectionDb": "kobis",
                    "subjectKeyword": "박스오피스",
                    "url": "https://example.com/a",
                },
                {
                    "title": "독립영화 B",
                    "creator": "테스트기관",
                    "regDate": "2023-11-10",
                    "collectionDb": "archive",
                    "subjectKeyword": "독립",
                    "url": "https://example.com/b",
                },
                {
                    "title": "영화 C",
                    "creator": "영화진흥위원회",
                    "regDate": "2024-03-15",
                    "collectionDb": "kobis",
                    "subjectKeyword": "흥행",
                    "url": "https://example.com/c",
                },
            ],
        }


class KoficBoxOfficeServiceTests(unittest.TestCase):
    def setUp(self):
        self.gateway = FakeGateway()
        self.service = KoficBoxOfficeService(gateway=self.gateway)

    def test_get_kofic_box_office_delegates_to_gateway(self):
        result = self.service.get_kofic_box_office(page_no=2, num_of_rows=25)

        self.assertEqual(BOX_OFFICE_ENDPOINT, result["operation"])
        self.assertEqual(
            {
                "pageNo": 2,
                "numOfRows": 25,
            },
            result["request_params"],
        )
        self.assertEqual(3, result["returned_count"])

    def test_get_kofic_box_office_rejects_invalid_page(self):
        with self.assertRaises(CultureOpenApiError):
            self.service.get_kofic_box_office(page_no=0)

    def test_get_kofic_box_office_filters_and_sorts_items(self):
        result = self.service.get_kofic_box_office(
            query="영화",
            creator="영화진흥",
            sort_by="regDate",
            sort_order="desc",
            limit=1,
        )

        self.assertEqual(3, result["source_item_count"])
        self.assertEqual(1, result["returned_count"])
        self.assertEqual("영화 C", result["items"][0]["title"])
        self.assertEqual({"query": "영화", "creator": "영화진흥"}, result["applied_filters"])
        self.assertEqual({"by": "regDate", "order": "desc"}, result["applied_sort"])

    def test_get_kofic_box_office_rejects_sort_order_without_sort_by(self):
        with self.assertRaises(KoficBoxOfficeError):
            self.service.get_kofic_box_office(sort_order="desc")

    def test_search_kofic_box_office_requires_query(self):
        with self.assertRaises(CultureOpenApiError):
            self.service.search_kofic_box_office("   ")

    def test_search_kofic_box_office_returns_compact_summaries(self):
        result = self.service.search_kofic_box_office("영화", limit=2)

        self.assertEqual("search_kofic_box_office", result["tool"])
        self.assertEqual("영화", result["query"])
        self.assertEqual(2, result["returned_count"])
        self.assertEqual("영화 A", result["items"][0]["title"])
        self.assertIn("title", result["match_fields"])

    def test_list_kofic_box_office_titles_returns_summary_fields(self):
        result = self.service.list_kofic_box_office_titles(limit=2)

        self.assertEqual("list_kofic_box_office_titles", result["tool"])
        self.assertEqual(2, result["returned_count"])
        self.assertEqual("영화 A", result["items"][0]["title"])
        self.assertIn("url", result["summary_fields"])

    def test_reference_payload_lists_supported_tool(self):
        payload = build_reference_payload()

        self.assertEqual("영화진흥위원회_박스오피스", payload["dataset"])
        self.assertEqual(
            [
                "get_kofic_box_office",
                "search_kofic_box_office",
                "list_kofic_box_office_titles",
            ],
            [tool["name"] for tool in payload["tools"]],
        )
        self.assertEqual(19, len(payload["output_fields"]))


if __name__ == "__main__":
    unittest.main()
