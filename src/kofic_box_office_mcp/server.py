from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from .arko_event_reference import build_arko_event_reference_payload
from .arko_event_service import ArkoEventServiceProtocol
from .bootstrap import create_arko_event_service, create_kofic_box_office_service
from .exceptions import CultureOpenApiError
from .reference import build_reference_payload
from .runtime import RuntimeConfig, apply_runtime_config
from .service import KoficBoxOfficeServiceProtocol

mcp = FastMCP("Culture Data", stateless_http=True, json_response=True)


@lru_cache(maxsize=1)
def get_service() -> KoficBoxOfficeServiceProtocol:
    return create_kofic_box_office_service()


@lru_cache(maxsize=1)
def get_arko_event_service() -> ArkoEventServiceProtocol:
    return create_arko_event_service()


@mcp.resource("kofic-box-office://reference")
def reference() -> dict:
    """Reference data for the supported KOFIC box-office dataset."""
    return build_reference_payload()


@mcp.resource("arko-events://reference")
def arko_event_reference() -> dict:
    """Reference data for the supported ARKO event dataset."""
    return build_arko_event_reference_payload()


@mcp.tool()
def get_kofic_box_office(
    page_no: int = 1,
    num_of_rows: int = 10,
    query: str | None = None,
    creator: str | None = None,
    collection_db: str | None = None,
    subject_keyword: str | None = None,
    limit: int | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
) -> dict:
    """Fetch a KOFIC box-office page and optionally apply local filtering and sorting."""
    return get_service().get_kofic_box_office(
        page_no=page_no,
        num_of_rows=num_of_rows,
        query=query,
        creator=creator,
        collection_db=collection_db,
        subject_keyword=subject_keyword,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@mcp.tool()
def search_kofic_box_office(query: str, page_no: int = 1, num_of_rows: int = 10, limit: int = 5) -> dict:
    """Search within a fetched KOFIC box-office page and return compact summaries."""
    return get_service().search_kofic_box_office(
        query=query,
        page_no=page_no,
        num_of_rows=num_of_rows,
        limit=limit,
    )


@mcp.tool()
def list_kofic_box_office_titles(page_no: int = 1, num_of_rows: int = 10, limit: int = 10) -> dict:
    """Return a compact list of titles from a fetched KOFIC box-office page."""
    return get_service().list_kofic_box_office_titles(
        page_no=page_no,
        num_of_rows=num_of_rows,
        limit=limit,
    )


@mcp.tool()
def get_arko_events(
    page_no: int = 1,
    num_of_rows: int = 10,
    query: str | None = None,
    creator: str | None = None,
    spatial: str | None = None,
    subject_keyword: str | None = None,
    limit: int | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
) -> dict:
    """Fetch an ARKO event page and optionally apply local filtering and sorting."""
    return get_arko_event_service().get_arko_events(
        page_no=page_no,
        num_of_rows=num_of_rows,
        query=query,
        creator=creator,
        spatial=spatial,
        subject_keyword=subject_keyword,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@mcp.tool()
def search_arko_events(query: str, page_no: int = 1, num_of_rows: int = 10, limit: int = 5) -> dict:
    """Search within a fetched ARKO event page and return compact summaries."""
    return get_arko_event_service().search_arko_events(
        query=query,
        page_no=page_no,
        num_of_rows=num_of_rows,
        limit=limit,
    )


@mcp.tool()
def list_arko_event_titles(page_no: int = 1, num_of_rows: int = 10, limit: int = 10) -> dict:
    """Return a compact list of titles from a fetched ARKO event page."""
    return get_arko_event_service().list_arko_event_titles(
        page_no=page_no,
        num_of_rows=num_of_rows,
        limit=limit,
    )


def main() -> None:
    try:
        runtime_config = RuntimeConfig.from_env()
        apply_runtime_config(mcp, runtime_config)
        mcp.run(transport="streamable-http")
    except CultureOpenApiError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
