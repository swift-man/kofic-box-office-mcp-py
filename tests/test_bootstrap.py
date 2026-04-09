import unittest

from kofic_box_office_mcp.bootstrap import create_arko_event_service, create_kofic_box_office_service
from kofic_box_office_mcp.arko_event_response_parser import ArkoEventResponseParser
from kofic_box_office_mcp.arko_event_service import ArkoEventService
from kofic_box_office_mcp.response_parser import KoficBoxOfficeResponseParser
from kofic_box_office_mcp.service import KoficBoxOfficeService
from kofic_box_office_mcp.settings import ArkoEventSettings, KoficBoxOfficeSettings, ServiceKeyConfig


class BootstrapTests(unittest.TestCase):
    def test_create_kofic_box_office_service_uses_gateway_factory(self):
        observed = {}

        def gateway_factory(settings, response_parser):
            observed["settings"] = settings
            observed["response_parser"] = response_parser

            class FakeGateway:
                def request(self, operation, params):
                    return {"operation": operation, "request_params": params}

            return FakeGateway()

        settings = KoficBoxOfficeSettings(service_key=ServiceKeyConfig(raw_key="secret"))
        service = create_kofic_box_office_service(settings=settings, gateway_factory=gateway_factory)

        self.assertIsInstance(service, KoficBoxOfficeService)
        self.assertIs(observed["settings"], settings)
        self.assertIsInstance(observed["response_parser"], KoficBoxOfficeResponseParser)

    def test_create_arko_event_service_uses_gateway_factory(self):
        observed = {}

        def gateway_factory(settings, response_parser):
            observed["settings"] = settings
            observed["response_parser"] = response_parser

            class FakeGateway:
                def request(self, operation, params):
                    return {"operation": operation, "request_params": params}

            return FakeGateway()

        settings = ArkoEventSettings(service_key=ServiceKeyConfig(raw_key="secret"))
        service = create_arko_event_service(settings=settings, gateway_factory=gateway_factory)

        self.assertIsInstance(service, ArkoEventService)
        self.assertIs(observed["settings"], settings)
        self.assertIsInstance(observed["response_parser"], ArkoEventResponseParser)


if __name__ == "__main__":
    unittest.main()
