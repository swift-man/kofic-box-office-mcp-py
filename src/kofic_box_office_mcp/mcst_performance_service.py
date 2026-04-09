from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Protocol

from .constants import BOX_OFFICE_SORT_ORDERS, DEFAULT_NUM_OF_ROWS, DEFAULT_PAGE_NO
from .exceptions import McstPerformanceError
from .mcst_performance_constants import (
    DEFAULT_MCST_PERFORMANCE_LIST_LIMIT,
    DEFAULT_MCST_PERFORMANCE_SEARCH_LIMIT,
    MCST_PERFORMANCE_DTYPE_CHOICES,
    MCST_PERFORMANCE_ENDPOINT,
    MCST_PERFORMANCE_SEARCH_FIELDS,
    MCST_PERFORMANCE_SORT_FIELDS,
    MCST_PERFORMANCE_SUMMARY_FIELDS,
)
from .mcst_performance_gateway import McstPerformanceGateway
from .validation import normalize_optional_text, require_text, validate_choice, validate_optional_positive_int, validate_positive_int


@dataclass(frozen=True)
class McstPerformanceQueryOptions:
    event_site: Optional[str] = None
    period: Optional[str] = None
    limit: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None

    @classmethod
    def from_inputs(
        cls,
        *,
        event_site: Optional[str] = None,
        period: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> "McstPerformanceQueryOptions":
        normalized_sort_by = normalize_optional_text(sort_by)
        normalized_sort_order = normalize_optional_text(sort_order)

        if normalized_sort_order and not normalized_sort_by:
            raise McstPerformanceError("sort_order can only be used when sort_by is also provided.")

        if normalized_sort_by:
            validate_choice("sort_by", normalized_sort_by, MCST_PERFORMANCE_SORT_FIELDS)
            normalized_sort_order = normalized_sort_order or "asc"

        if normalized_sort_order:
            validate_choice("sort_order", normalized_sort_order, BOX_OFFICE_SORT_ORDERS)

        return cls(
            event_site=normalize_optional_text(event_site),
            period=normalize_optional_text(period),
            limit=validate_optional_positive_int("limit", limit),
            sort_by=normalized_sort_by,
            sort_order=normalized_sort_order,
        )


class McstPerformanceServiceProtocol(Protocol):
    def get_mcst_performances(
        self,
        dtype: str,
        title: str,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        event_site: Optional[str] = None,
        period: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict[str, Any]:
        ...

    def search_mcst_performances(
        self,
        dtype: str,
        title: str,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        limit: int = DEFAULT_MCST_PERFORMANCE_SEARCH_LIMIT,
    ) -> Dict[str, Any]:
        ...

    def list_mcst_performance_titles(
        self,
        dtype: str,
        title: str,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        limit: int = DEFAULT_MCST_PERFORMANCE_LIST_LIMIT,
    ) -> Dict[str, Any]:
        ...


@dataclass(frozen=True)
class McstPerformanceService:
    gateway: McstPerformanceGateway

    def get_mcst_performances(
        self,
        dtype: str,
        title: str,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        event_site: Optional[str] = None,
        period: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict[str, Any]:
        validate_positive_int("page_no", page_no)
        validate_positive_int("num_of_rows", num_of_rows)

        dtype_value = require_text("dtype", dtype)
        validate_choice("dtype", dtype_value, MCST_PERFORMANCE_DTYPE_CHOICES)
        title_value = require_text("title", title)
        if len(title_value) < 2:
            raise McstPerformanceError("title must be at least 2 characters long.")

        options = McstPerformanceQueryOptions.from_inputs(
            event_site=event_site,
            period=period,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        response = self.gateway.request(
            MCST_PERFORMANCE_ENDPOINT,
            {
                "dtype": dtype_value,
                "title": title_value,
                "pageNo": page_no,
                "numOfRows": num_of_rows,
            },
        )
        return self._shape_result(response, options)

    def search_mcst_performances(
        self,
        dtype: str,
        title: str,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        limit: int = DEFAULT_MCST_PERFORMANCE_SEARCH_LIMIT,
    ) -> Dict[str, Any]:
        result = self.get_mcst_performances(
            dtype=dtype,
            title=title,
            page_no=page_no,
            num_of_rows=num_of_rows,
            limit=limit,
        )
        return self._build_summary_view(
            result,
            tool_name="search_mcst_performances",
            dtype=dtype,
            title=title,
            match_fields=MCST_PERFORMANCE_SEARCH_FIELDS,
        )

    def list_mcst_performance_titles(
        self,
        dtype: str,
        title: str,
        page_no: int = DEFAULT_PAGE_NO,
        num_of_rows: int = DEFAULT_NUM_OF_ROWS,
        limit: int = DEFAULT_MCST_PERFORMANCE_LIST_LIMIT,
    ) -> Dict[str, Any]:
        result = self.get_mcst_performances(
            dtype=dtype,
            title=title,
            page_no=page_no,
            num_of_rows=num_of_rows,
            limit=limit,
        )
        return self._build_summary_view(
            result,
            tool_name="list_mcst_performance_titles",
            dtype=dtype,
            title=title,
            summary_fields=MCST_PERFORMANCE_SUMMARY_FIELDS,
        )

    def _shape_result(self, response: Mapping[str, Any], options: McstPerformanceQueryOptions) -> Dict[str, Any]:
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
            {"by": options.sort_by, "order": options.sort_order} if options.sort_by else None
        )
        result["applied_limit"] = options.limit
        return result

    def _build_summary_view(
        self,
        result: Mapping[str, Any],
        *,
        tool_name: str,
        dtype: str,
        title: str,
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
            "dtype": dtype,
            "title": title,
            "items": [self._summarize_item(item) for item in self._coerce_items(result.get("items"))],
        }
        if match_fields is not None:
            summary["match_fields"] = list(match_fields)
        if summary_fields is not None:
            summary["summary_fields"] = list(summary_fields)
        return summary

    def _filter_items(
        self,
        items: list[Dict[str, Any]],
        options: McstPerformanceQueryOptions,
    ) -> list[Dict[str, Any]]:
        filtered_items = []
        for item in items:
            if options.event_site and not self._matches_text(item.get("eventSite"), options.event_site):
                continue
            if options.period and not self._matches_text(item.get("period"), options.period):
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

    def _build_filter_summary(self, options: McstPerformanceQueryOptions) -> Dict[str, Any]:
        filters: Dict[str, Any] = {}
        if options.event_site is not None:
            filters["event_site"] = options.event_site
        if options.period is not None:
            filters["period"] = options.period
        return filters

    def _summarize_item(self, item: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            field_name: item.get(field_name)
            for field_name in MCST_PERFORMANCE_SUMMARY_FIELDS
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

    def _matches_text(self, value: Any, expected: str) -> bool:
        return expected.casefold() in self._stringify(value).casefold()

    def _stringify(self, value: Any) -> str:
        if value in (None, "", [], {}):
            return ""
        if isinstance(value, Mapping):
            return " ".join(self._stringify(nested_value) for nested_value in value.values())
        if isinstance(value, list):
            return " ".join(self._stringify(item) for item in value)
        return str(value)
