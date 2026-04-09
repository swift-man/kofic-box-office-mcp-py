from __future__ import annotations

from typing import Callable, Optional

from .gateway import KoficBoxOfficeGateway, UrllibKoficBoxOfficeGateway, default_response_parser
from .response_parser import ResponseParser
from .service import KoficBoxOfficeService, KoficBoxOfficeServiceProtocol
from .settings import KoficBoxOfficeSettings

GatewayFactory = Callable[[KoficBoxOfficeSettings, ResponseParser], KoficBoxOfficeGateway]


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
