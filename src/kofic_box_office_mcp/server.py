from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from .bootstrap import create_kofic_box_office_service
from .exceptions import KoficBoxOfficeError
from .reference import build_reference_payload
from .runtime import RuntimeConfig, apply_runtime_config
from .service import KoficBoxOfficeServiceProtocol

mcp = FastMCP("KOFIC Box Office", stateless_http=True, json_response=True)


@lru_cache(maxsize=1)
def get_service() -> KoficBoxOfficeServiceProtocol:
    return create_kofic_box_office_service()


@mcp.resource("kofic-box-office://reference")
def reference() -> dict:
    """Reference data for the supported KOFIC box-office dataset."""
    return build_reference_payload()


@mcp.tool()
def get_kofic_box_office(page_no: int = 1, num_of_rows: int = 10) -> dict:
    """Fetch KOFIC box-office records from the KOFIC box-office API."""
    return get_service().get_kofic_box_office(page_no=page_no, num_of_rows=num_of_rows)


def main() -> None:
    try:
        runtime_config = RuntimeConfig.from_env()
        apply_runtime_config(mcp, runtime_config)
        mcp.run(transport="streamable-http")
    except KoficBoxOfficeError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
