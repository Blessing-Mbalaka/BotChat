from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from .extraction_store import get_artifact, get_latest_table_with_column, get_tables


class KPIService:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        metric_name = (payload.get("metric") or "KPI").strip()
        aggregation = (payload.get("aggregation") or "sum").lower()
        value_column = payload.get("value_column")
        if aggregation not in {"sum", "avg", "average", "min", "max", "count"}:
            raise ValueError("Unsupported aggregation. Use sum, avg, min, max, or count")
        if aggregation != "count" and not value_column:
            raise ValueError("value_column is required for numeric aggregations")

        table = self._select_table(payload, value_column)
        if not table:
            raise ValueError("No table available for KPI computation")

        rows_as_dict = self._rows_as_dict(table)
        filtered_rows = self._apply_filters(rows_as_dict, payload)
        if not filtered_rows:
            return {
                "kpis": [],
                "summary": "No rows matched the KPI filters.",
                "table": self._table_meta(table),
            }

        if aggregation in {"avg", "average"}:
            aggregation = "avg"

        if aggregation == "count":
            result_value = len(filtered_rows)
            numeric_values = []
        else:
            numeric_values = self._extract_numeric(filtered_rows, value_column)
            if not numeric_values:
                raise ValueError(f"Column '{value_column}' did not contain numeric values")
            if aggregation == "sum":
                result_value = sum(numeric_values)
            elif aggregation == "avg":
                result_value = sum(numeric_values) / len(numeric_values)
            elif aggregation == "min":
                result_value = min(numeric_values)
            elif aggregation == "max":
                result_value = max(numeric_values)
            else:
                raise ValueError("Unsupported aggregation")

        summary = self._build_summary(metric_name, aggregation, value_column, result_value, len(filtered_rows))

        unit = payload.get("unit")
        response = {
            "kpis": [
                {
                    "metric": metric_name,
                    "aggregation": aggregation,
                    "value": result_value,
                    "formatted_value": self._format_number(result_value),
                    "rows_matched": len(filtered_rows),
                    "value_column": value_column,
                    "unit": unit,
                    "table_id": table.get("id"),
                    "source": table.get("source"),
                }
            ],
            "summary": summary,
            "table": self._table_meta(table),
        }
        return response

    def _select_table(self, payload: Dict[str, Any], value_column: Optional[str]) -> Optional[Dict[str, Any]]:
        table_id = payload.get("table_id")
        if table_id:
            table = get_artifact(table_id)
            if table and table.get("type") == "table":
                return table
        if value_column:
            table = get_latest_table_with_column(value_column)
            if table:
                return table
        tables = get_tables(limit=1)
        return tables[0] if tables else None

    def _rows_as_dict(self, table: Dict[str, Any]) -> List[Dict[str, Any]]:
        columns = table.get("columns", [])
        rows = table.get("rows", [])
        return [
            {columns[idx]: row[idx] if idx < len(row) else None for idx in range(len(columns))}
            for row in rows
        ]

    def _apply_filters(self, rows: List[Dict[str, Any]], payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        filters = payload.get("filters") or []
        date_column = payload.get("date_column")
        date_from = self._parse_date(payload.get("date_from"))
        date_to = self._parse_date(payload.get("date_to"))

        def row_matches(row: Dict[str, Any]) -> bool:
            for f in filters:
                column = f.get("column")
                if not column or column not in row:
                    continue
                op = (f.get("op") or "eq").lower()
                target = f.get("value")
                value = row.get(column)
                if not self._match_filter(value, target, op):
                    return False
            if date_column and date_column in row and (date_from or date_to):
                cell_date = self._parse_date(row.get(date_column))
                if not cell_date:
                    return False
                if date_from and cell_date < date_from:
                    return False
                if date_to and cell_date > date_to:
                    return False
            return True

        return [row for row in rows if row_matches(row)]

    def _match_filter(self, value: Any, target: Any, op: str) -> bool:
        if op == "eq":
            return str(value).strip().lower() == str(target).strip().lower()
        if op == "ne":
            return str(value).strip().lower() != str(target).strip().lower()
        if op == "contains":
            return str(target).strip().lower() in str(value).strip().lower()
        if op in {"gt", "gte", "lt", "lte"}:
            value_num = self._to_float(value)
            target_num = self._to_float(target)
            if value_num is None or target_num is None:
                return False
            if op == "gt":
                return value_num > target_num
            if op == "gte":
                return value_num >= target_num
            if op == "lt":
                return value_num < target_num
            if op == "lte":
                return value_num <= target_num
        return False

    def _extract_numeric(self, rows: List[Dict[str, Any]], column: str) -> List[float]:
        values: List[float] = []
        for row in rows:
            number = self._to_float(row.get(column))
            if number is not None:
                values.append(number)
        return values

    def _to_float(self, value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)):
            if isinstance(value, bool):
                return float(value)
            return float(value)
        value_str = str(value).strip()
        if value_str.endswith('%'):
            try:
                return float(value_str.rstrip('%').replace(',', '')) / 100.0
            except ValueError:
                return None
        try:
            return float(value_str.replace(',', ''))
        except ValueError:
            return None

    def _parse_date(self, value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        value_str = str(value).strip()
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y",
            "%b %Y",
            "%B %Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(value_str, fmt)
            except ValueError:
                continue
        return None

    def _build_summary(self, metric: str, aggregation: str, value_column: Optional[str], value: Any, rows: int) -> str:
        agg_label = aggregation.upper()
        base = f"{agg_label} of"
        if value_column:
            base += f" {value_column}"
        formatted_value = self._format_number(value)
        return f"{metric}: {base} across {rows} rows = {formatted_value}"

    def _format_number(self, value: Any) -> Any:
        if isinstance(value, (int, float)):
            if isinstance(value, float) and math.isnan(value):
                return value
            if abs(value) >= 1000:
                return f"{value:,.2f}"
            return f"{value:.2f}"
        return value

    def _table_meta(self, table: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": table.get("id"),
            "title": table.get("title"),
            "columns": table.get("columns", []),
            "source": table.get("source", {}),
        }
