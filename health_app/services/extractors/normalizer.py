import hashlib
from typing import Any, Dict, List, Optional


def _is_number(value: Any) -> bool:
    try:
        if value is None or value == "":
            return False
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def _make_id(seed: str) -> str:
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]


def normalize_table(title: str, columns: List[str], rows: List[List[Any]], source: Dict[str, Any]) -> Dict[str, Any]:
    tid = _make_id(title + "|" + ",".join(columns) + "|" + str(len(rows)))
    return {
        "type": "table",
        "id": tid,
        "title": title or source.get("name") or "Table",
        "columns": [str(c) for c in columns],
        "rows": [[None if r is None else r for r in row] for row in rows],
        "source": source,
    }


def normalize_chart(chart_type: str, categories: List[str], series: List[Dict[str, Any]], source: Dict[str, Any], title: Optional[str] = None) -> Dict[str, Any]:
    seed = (title or "chart") + chart_type + ",".join(categories)
    cid = _make_id(seed)
    return {
        "type": "chart",
        "id": cid,
        "title": title or "Chart",
        "chart_type": chart_type,
        "categories": categories,
        "series": series,
        "source": source,
    }


def derive_basic_charts(table: Dict[str, Any]) -> List[Dict[str, Any]]:
    columns = table.get("columns", [])
    rows = table.get("rows", [])
    if len(columns) < 2 or len(rows) == 0:
        return []

    first_col = columns[0]
    categories: List[str] = []
    numeric_series: List[int] = []
    for idx, _ in enumerate(columns[1:], start=1):
        column_values = [row[idx] if idx < len(row) else None for row in rows]
        if column_values and all((v is None or _is_number(v)) for v in column_values):
            numeric_series.append(idx)

    if not numeric_series:
        return []

    for row in rows:
        value = row[0] if row else None
        if value is None:
            categories.append("(missing)")
        else:
            categories.append(str(value))

    # If categories look like dates, prefer line chart
    chart_type = "line" if _looks_like_dates(categories) else "bar"

    artifacts = []
    series_payload: List[Dict[str, Any]] = []
    for idx in numeric_series:
        data_points = []
        for row in rows:
            value = row[idx] if idx < len(row) else None
            data_points.append(float(value) if _is_number(value) else None)
        series_payload.append(
            {
                "name": str(columns[idx]),
                "data": data_points,
            }
        )

    # Limit categories for usability
    trimmed_categories = categories[:50]
    trimmed_series = []
    for serie in series_payload:
        trimmed_series.append({"name": serie["name"], "data": serie["data"][:50]})

    artifacts.append(
        normalize_chart(
            chart_type=chart_type,
            categories=trimmed_categories,
            series=trimmed_series,
            source=table.get("source", {}),
            title=f"Visual: {table.get('title', 'Table')}",
        )
    )

    return artifacts


def _looks_like_dates(values: List[str]) -> bool:
    if not values:
        return False
    import re

    date_patterns = [
        re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$"),
        re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$"),
        re.compile(r"^[A-Za-z]{3,9}\s+\d{4}$"),
    ]
    hits = 0
    for value in values[:10]:
        if not isinstance(value, str):
            continue
        for pattern in date_patterns:
            if pattern.match(value.strip()):
                hits += 1
                break
    return hits >= max(2, len(values[:10]) // 2)
