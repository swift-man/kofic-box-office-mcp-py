import unittest

from kofic_box_office_mcp.arko_event_response_parser import ArkoEventResponseParser, normalize_api_payload
from kofic_box_office_mcp.exceptions import ArkoEventError


class ArkoEventResponseParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = ArkoEventResponseParser()

    def test_parse_json_payload_normalizes_items(self):
        raw_body = """
        {
          "response": {
            "header": {
              "resultCode": "0000",
              "resultMsg": "정상 처리"
            },
            "body": {
              "pageNo": "1",
              "numOfRows": "10",
              "totalCount": "1",
              "items": {
                "item": {
                  "title": "행사 A",
                  "spatial": "서울"
                }
              }
            }
          }
        }
        """

        result = self.parser.parse(
            operation="ARKeven",
            query_params={"pageNo": 1, "numOfRows": 10},
            status_code=200,
            raw_body=raw_body,
            content_type="application/json",
        )

        self.assertEqual("행사 A", result["items"][0]["title"])
        self.assertEqual(1, result["page_no"])
        self.assertEqual("0000", result["result"]["code"])

    def test_parse_xml_payload_normalizes_items(self):
        raw_body = """
        <response>
          <header>
            <resultCode>0000</resultCode>
            <resultMsg>정상 처리</resultMsg>
          </header>
          <body>
            <pageNo>1</pageNo>
            <numOfRows>10</numOfRows>
            <totalCount>2</totalCount>
            <items>
              <item>
                <title>행사 A</title>
              </item>
              <item>
                <title>행사 B</title>
              </item>
            </items>
          </body>
        </response>
        """

        result = self.parser.parse(
            operation="ARKeven",
            query_params={"pageNo": 1, "numOfRows": 10},
            status_code=200,
            raw_body=raw_body,
            content_type="application/xml",
        )

        self.assertEqual(2, len(result["items"]))
        self.assertEqual("행사 B", result["items"][1]["title"])
        self.assertEqual(2, result["total_count"])

    def test_normalize_api_payload_raises_for_api_error_code(self):
        with self.assertRaises(ArkoEventError) as context:
            normalize_api_payload(
                operation="ARKeven",
                query_params={"pageNo": 1, "numOfRows": 10},
                status_code=500,
                payload={
                    "response": {
                        "header": {
                            "resultCode": "9999",
                            "resultMsg": "서비스 점검중(내부 서비스 호출 장애)",
                        },
                        "body": {},
                    }
                },
            )

        self.assertIn("9999", str(context.exception))


if __name__ == "__main__":
    unittest.main()
