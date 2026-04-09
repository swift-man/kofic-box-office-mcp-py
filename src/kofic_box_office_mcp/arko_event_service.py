from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Protocol

from .arko_event_constants import (
    ARKO_EVENT_ENDPOINT,
    ARKO_EVENT_SEARCH_FIELDS,
    ARKO_EVENT_SORT_FIELDS,
    ARKO_EVENT_SUMMARY_FIELDS,
    DEFAULT_ARKO_EVENT_LIST_LIMIT,
    DEFAULT_ARKO_EVENT_SEARCH_LIMIT,
)
from .constants import BOX_OFFICE_SORT_ORDERS, DEFAULT_NUM_OF_ROWS, DEFAULT_PAGE_NO
from .arko_event_gateway import ArkoEventGateway
from .exceptions import ArkoEventError
from .validation import (
    normalize_optional_text,
    require_text,
    validate_choice,
    validate_optional_positive_int,
    validate_positive_int,
)


@dataclass(frozen=True)
class ArkoEventQueryOptions:
    query: Optional[str] = None
    creator: Optional[str] = None
    spatial: Optional[str] = None
    subject_keyword: Optional[str] = None
    limit: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None

    @classmethod
    def from_inputs(
        cls,
        *,
        query: Optional[str] = None,
        creator: Optional[str] = None,
        spatial: Optional[str] = None,
        subject_keyword: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> "ArkoEventQueryOptions":
        normalized_sort_by = normalize_optional_text(sort_by)
        normalized_sort_order = normalize_optional_text(sort_order)

        if normalized_sort_order and not normalized_sort_by:
            raise ArkoEventError("sort_order can only be used when sort_by is also provided.")

        if normalized_sort_by:
            validate_choice("sort_by", normalized_sort_by, ARKO_EVENT_SORT_FIELDS)
            normalized_sort_order = normalized_sort_order or "asc"

        if normalized_sort_order:
            validate_choice("sort_order", normalized_sort_order, BOX_OFFICE_SORT_ORDERS)

        return cls(
            query=normalize_optional_text(query),
            creator=normalize_optional_text(creator),
            spatial=normalize_optional_text(spatial),
            subject_keyword=normalize_optional_text(subject_keyword),
            limit=validate_optional_positive_int("limit", limit),
            sort_by=normalized_sort_by,
            sort_order=normalized_sort_order,
        )


class ArkoEventServiceProtocol(Protocol):
    def get_arko_events(
        self,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        query: Optional[str] = None,
        creator: Optional[str] = None,
        spatial: Optional[str] = None,
        subject_keyword: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict[str, Any]:
        ...

    def search_arko_events(
        self,
        query: str,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        limit: int = DEFAULT_ARKO_EVENT_SEARCH_LIMIT,
    ) -> Dict[str, Any]:
        ...

    def list_arko_event_titles(
        self,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        limit: int = DEFAULT_ARKO_EVENT_LIST_LIMIT,
    ) -> Dict[str, Any]:
        ...


@dataclass(frozen=True)
class ArkoEventService:
    gateway: ArkoEventGateway

    def get_arko_events(
        self,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        query: Optional[str] = None,
        creator: Optional[str] = None,
        spatial: Optional[str] = None,
        subject_keyword: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict[str, Any]:
        validate_positive_int("page_no", page_no)
        validate_positive_int("num_of_rows", num_of_rows)

        options = ArkoEventQueryOptions.from_inputs(
            query=query,
            creator=creator,
            spatial=spatial,
            subject_keyword=subject_keyword,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        response = self.gateway.request(
            ARKO_EVENT_ENDPOINT,
            {
                "pageNo": page_no,
                "numOfRows": num_of_rows,
            },
        )
        return self._shape_result(response, options)

    def search_arko_events(
        self,
        query: str,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        limit: int = DEFAULT_ARKO_EVENT_SEARCH_LIMIT,
    ) -> Dict[str, Any]:
        search_query = require_text("query", query)
        result = self.get_arko_events(
            page_no=page_no,
            num_of_rows=num_of_rows,
            query=search_query,
            limit=limit,
        )
        return self._build_summary_view(
            result,
            tool_name="search_arko_events",
            query=search_query,
            match_fields=ARKO_EVENT_SEARCH_FIELDS,
        )

    def list_arko_event_titles(
        self,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        limit: int = DEFAULT_ARKO_EVENT_LIST_LIMIT,
    ) -> Dict[str, Any]:
        result = self.get_arko_events(
            page_no=page_no,
            num_of_rows=num_of_rows,
            limit=limit,
        )
        return self._build_summary_view(
            result,
            tool_name="list_arko_event_titles",
            summary_fields=ARKO_EVENT_SUMMARY_FIELDS,
        )

    def _shape_result(self, response: Mapping[str, Any], options: ArkoEventQueryOptions) -> Dict[str, Any]:
        result = dict(response)
        source_items = self._coerce_items(result.get("items"))
        filtered_items = self._filter_items(source_items, options)
        sorted_items = self._sort_items(filtered_items, options.sort_by, options.sort_order)

        if options.limit is not None:
            sorted_items = sorted_items[: options.limit]

        result["items"] = sorted_items
        result["source_item_count"] = len(source_items)
        result["returned_count"] = len(sorted_items)
        result["applied_filters"] = self._build_filter_summary(options)
        result["applied_sort"] = (
            {
                "by": options.sort_by,
                "order": options.sort_order,
            }
            if options.sort_by
            else None
        )
        result["applied_limit"] = options.limit
        return result

    def _build_summary_view(
        self,
        result: Mapping[str, Any],
        *,
        tool_name: str,
        query: Optional[str] = None,
        match_fields: Optional[tuple[str, ...]] = None,
        summary_fields: Optional[tuple[str, ...]] = None,
    ) -> Dict[str, Any]:
        summary = {
            "tool": tool_name,
            "dataset": result.get("dataset"),
            "dataset_url": result.get("dataset_url"),
            "operation": result.get("operation"),
            "operation_path": result.get("operation_path"),
            "request_params": result.get("request_params"),
            "page_no": result.get("page_no"),
            "num_of_rows": result.get("num_of_rows"),
            "total_count": result.get("total_count"),
            "source_item_count": result.get("source_item_count"),
            "returned_count": result.get("returned_count"),
            "applied_filters": result.get("applied_filters"),
            "applied_sort": result.get("applied_sort"),
            "applied_limit": result.get("applied_limit"),
            "items": [self._summarize_item(item) for item in self._coerce_items(result.get("items"))],
        }
        if query is not None:
            summary["query"] = query
        if match_fields is not None:
            summary["match_fields"] = list(match_fields)
        if summary_fields is not None:
            summary["summary_fields"] = list(summary_fields)
        return summary

    def _filter_items(self, items: list[Dict[str, Any]], options: ArkoEventQueryOptions) -> list[Dict[str, Any]]:
        filtered_items = []
        for item in items:
            if options.query and not self._matches_any_field(item, ARKO_EVENT_SEARCH_FIELDS, options.query):
                continue
            if options.creator and not self._matches_text(item.get("creator"), options.creator):
                continue
            if options.spatial and not self._matches_text(item.get("spatial"), options.spatial):
                continue
            if options.subject_keyword and not self._matches_text(item.get("subjectKeyword"), options.subject_keyword):
                continue
            filtered_items.append(item)
        return filtered_items

    def _sort_items(
        self,
        items: list[Dict[str, Any]],
        sort_by: Optional[str],
        sort_order: Optional[str],
    ) -> list[Dict[str, Any]]:
        if not sort_by:
            return list(items)

        populated_items = [item for item in items if self._stringify(item.get(sort_by))]
        empty_items = [item for item in items if not self._stringify(item.get(sort_by))]
        populated_items.sort(
            key=lambda item: self._stringify(item.get(sort_by)).casefold(),
            reverse=sort_order == "desc",
        )
        return populated_items + empty_items

    def _build_filter_summary(self, options: ArkoEventQueryOptions) -> Dict[str, Any]:
        filters: Dict[str, Any] = {}
        if options.query is not None:
            filters["query"] = options.query
        if options.creator is not None:
            filters["creator"] = options.creator
        if options.spatial is not None:
            filters["spatial"] = options.spatial
        if options.subject_keyword is not None:
            filters["subject_keyword"] = options.subject_keyword
        return filters

    def _matches_any_field(self, item: Mapping[str, Any], field_names: tuple[str, ...], expected: str) -> bool:
        return any(self._matches_text(item.get(field_name), expected) for field_name in field_names)

    def _matches_text(self, value: Any, expected: str) -> bool:
        return expected.casefold() in self._stringify(value).casefold()

    def _summarize_item(self, item: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            field_name: item.get(field_name)
            for field_name in ARKO_EVENT_SUMMARY_FIELDS
            if item.get(field_name) not in (None, "", [], {})
        }

    def _coerce_items(self, value: Any) -> list[Dict[str, Any]]:
        if not isinstance(value, list):
            return []

        items: list[Dict[str, Any]] = []
        for item in value:
            if isinstance(item, Mapping):
                items.append(dict(item))
        return items

    def _stringify(self, value: Any) -> str:
        if value in (None, "", [], {}):
            return ""
        if isinstance(value, Mapping):
            return " ".join(self._stringify(nested_value) for nested_value in value.values())
        if isinstance(value, list):
            return " ".join(self._stringify(item) for item in value)
        return str(value)
