import unittest

from kofic_box_office_mcp.exceptions import KoficBoxOfficeError
from kofic_box_office_mcp.response_parser import KoficBoxOfficeResponseParser, normalize_api_payload


class ResponseParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = KoficBoxOfficeResponseParser()

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
                  "title": "영화 A",
                  "creator": "영화진흥위원회"
                }
              }
            }
          }
        }
        """

        result = self.parser.parse(
            operation="getKFCC0502",
            query_params={"pageNo": 1, "numOfRows": 10},
            status_code=200,
            raw_body=raw_body,
            content_type="application/json",
        )

        self.assertEqual("영화 A", result["items"][0]["title"])
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
                <title>영화 A</title>
              </item>
              <item>
                <title>영화 B</title>
              </item>
            </items>
          </body>
        </response>
        """

        result = self.parser.parse(
            operation="getKFCC0502",
            query_params={"pageNo": 1, "numOfRows": 10},
            status_code=200,
            raw_body=raw_body,
            content_type="application/xml",
        )

        self.assertEqual(2, len(result["items"]))
        self.assertEqual("영화 B", result["items"][1]["title"])
        self.assertEqual(2, result["total_count"])

    def test_normalize_api_payload_raises_for_api_error_code(self):
        with self.assertRaises(KoficBoxOfficeError) as context:
            normalize_api_payload(
                operation="getKFCC0502",
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
