from typing import List, Dict, Any, Optional

from docx import Document

from .normalizer import normalize_table


def extract_from_docx(path: str) -> List[Dict[str, Any]]:
    artifacts: List[Dict[str, Any]] = []
    try:
        doc = Document(path)
        tcount = 0
        for t in doc.tables:
            rows = []
            for row in t.rows:
                rows.append([cell.text.strip() for cell in row.cells])
            if not rows:
                continue
            columns = _infer_docx_columns(rows)
            data_rows = rows if columns is None else rows[1:]
            final_columns = columns or [f"Col {i+1}" for i in range(len(rows[0]))]
            if not data_rows:
                data_rows = rows
            artifacts.append(
                normalize_table(
                    title=f"Table {tcount+1}",
                    columns=final_columns,
                    rows=data_rows,
                    source={"type": "file", "name": path},
                )
            )
            tcount += 1
    except Exception:
        return []
    return artifacts


from typing import Optional


def _infer_docx_columns(rows: List[List[str]]) -> Optional[List[str]]:
    if not rows:
        return None
    header = rows[0]
    header_clean = [cell.strip() for cell in header]
    unique = len(set(h for h in header_clean if h)) == len([h for h in header_clean if h])
    if unique and all(len(cell) <= 64 for cell in header_clean):
        return [cell or f"Col {idx+1}" for idx, cell in enumerate(header_clean)]
    return None
