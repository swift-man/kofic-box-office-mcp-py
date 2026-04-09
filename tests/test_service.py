import unittest

from kofic_box_office_mcp.constants import BOX_OFFICE_ENDPOINT
from kofic_box_office_mcp.exceptions import KoficBoxOfficeError
from kofic_box_office_mcp.reference import build_reference_payload
from kofic_box_office_mcp.service import KoficBoxOfficeService


class FakeGateway:
    def __init__(self):
        self.calls = []

    def request(self, operation, params):
        self.calls.append((operation, params))
        return {"operation": operation, "request_params": params, "items": []}


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

    def test_get_kofic_box_office_rejects_invalid_page(self):
        with self.assertRaises(KoficBoxOfficeError):
            self.service.get_kofic_box_office(page_no=0)

    def test_reference_payload_lists_supported_tool(self):
        payload = build_reference_payload()

        self.assertEqual("영화진흥위원회_박스오피스", payload["dataset"])
        self.assertEqual("get_kofic_box_office", payload["tools"][0]["name"])
        self.assertEqual(19, len(payload["output_fields"]))


if __name__ == "__main__":
    unittest.main()
