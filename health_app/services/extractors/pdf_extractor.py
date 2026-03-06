from typing import List, Dict, Any

import pdfplumber

from .normalizer import normalize_table


def extract_from_pdf(path: str) -> List[Dict[str, Any]]:
    artifacts: List[Dict[str, Any]] = []
    try:
        with pdfplumber.open(path) as pdf:
            for pi, page in enumerate(pdf.pages):
                try:
                    tables = page.extract_tables() or []
                except Exception:
                    tables = []
                for ti, tbl in enumerate(tables):
                    if not tbl or not any(any(c for c in row) for row in tbl):
                        continue
                    header, data_rows = _split_header(tbl)
                    columns = header or [f"Col {i+1}" for i in range(len(tbl[0]))]
                    if not data_rows:
                        data_rows = tbl
                    rows = [[(c or "").strip() if isinstance(c, str) else c for c in row] for row in data_rows]
                    artifacts.append(
                        normalize_table(
                            title=f"Page {pi+1} Table {ti+1}",
                            columns=columns,
                            rows=rows,
                            source={"type": "file", "name": path, "page": pi + 1},
                        )
                    )
    except Exception:
        return []
    return artifacts


def _split_header(table_rows: List[List[Any]]) -> tuple[list[str], List[List[Any]]]:
    if not table_rows:
        return [], table_rows
    first_row = table_rows[0]
    cleaned = [cell.strip() if isinstance(cell, str) else cell for cell in first_row]
    if all(isinstance(cell, str) and cell for cell in cleaned):
        unique = len(set(cleaned)) == len(cleaned)
        if unique:
            return [str(cell) for cell in cleaned], table_rows[1:]
    return [], table_rows
