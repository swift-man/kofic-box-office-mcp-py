from __future__ import annotations

from typing import Callable, Optional

from .arko_event_gateway import ArkoEventGateway, UrllibArkoEventGateway, default_gateway_response_parser
from .arko_event_response_parser import ArkoEventResponseParserProtocol
from .arko_event_service import ArkoEventService, ArkoEventServiceProtocol
from .gateway import KoficBoxOfficeGateway, UrllibKoficBoxOfficeGateway, default_response_parser
from .response_parser import ResponseParser
from .service import KoficBoxOfficeService, KoficBoxOfficeServiceProtocol
from .settings import ArkoEventSettings, KoficBoxOfficeSettings

GatewayFactory = Callable[[KoficBoxOfficeSettings, ResponseParser], KoficBoxOfficeGateway]
ArkoGatewayFactory = Callable[[ArkoEventSettings, ArkoEventResponseParserProtocol], ArkoEventGateway]


def create_gateway(settings: KoficBoxOfficeSettings, response_parser: ResponseParser) -> KoficBoxOfficeGateway:
    return UrllibKoficBoxOfficeGateway(settings=settings, response_parser=response_parser)


def create_kofic_box_office_service(
    settings: Optional[KoficBoxOfficeSettings] = None,
    gateway_factory: GatewayFactory = create_gateway,
    response_parser: Optional[ResponseParser] = None,
) -> KoficBoxOfficeServiceProtocol:
    resolved_settings = settings or KoficBoxOfficeSettings.from_env()
    resolved_response_parser = response_parser or default_response_parser()
    gateway = gateway_factory(resolved_settings, resolved_response_parser)
    return KoficBoxOfficeService(gateway=gateway)


def create_arko_event_gateway(
    settings: ArkoEventSettings,
    response_parser: ArkoEventResponseParserProtocol,
) -> ArkoEventGateway:
    return UrllibArkoEventGateway(settings=settings, response_parser=response_parser)


def create_arko_event_service(
    settings: Optional[ArkoEventSettings] = None,
    gateway_factory: ArkoGatewayFactory = create_arko_event_gateway,
    response_parser: Optional[ArkoEventResponseParserProtocol] = None,
) -> ArkoEventServiceProtocol:
    resolved_settings = settings or ArkoEventSettings.from_env()
    resolved_response_parser = response_parser or default_gateway_response_parser()
    gateway = gateway_factory(resolved_settings, resolved_response_parser)
    return ArkoEventService(gateway=gateway)
