from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol

from .constants import BOX_OFFICE_ENDPOINT, DEFAULT_NUM_OF_ROWS, DEFAULT_PAGE_NO
from .gateway import KoficBoxOfficeGateway
from .validation import validate_positive_int


class KoficBoxOfficeServiceProtocol(Protocol):
    def get_kofic_box_office(
        self,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
    ) -> Dict[str, Any]:
        ...


@dataclass(frozen=True)
class KoficBoxOfficeService:
    gateway: KoficBoxOfficeGateway

    def get_kofic_box_office(
        self,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
    ) -> Dict[str, Any]:
        validate_positive_int("page_no", page_no)
        validate_positive_int("num_of_rows", num_of_rows)
        return self.gateway.request(
            BOX_OFFICE_ENDPOINT,
            {
                "pageNo": page_no,
                "numOfRows": num_of_rows,
            },
        )
