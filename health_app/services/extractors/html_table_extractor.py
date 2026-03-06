from typing import List, Dict, Any
import pandas as pd
from .normalizer import normalize_table


def extract_from_html(html: str, source_name: str = "web") -> List[Dict[str, Any]]:
    artifacts: List[Dict[str, Any]] = []
    try:
        tables = pd.read_html(html)
        for idx, df in enumerate(tables):
            if df.empty:
                continue
            df = df.dropna(how="all")
            df = df.loc[:, ~df.columns.duplicated()]
            columns = [str(c) for c in df.columns.tolist()]
            rows = df.where(pd.notnull(df), None).values.tolist()
            artifacts.append(
                normalize_table(
                    title=f"Table {idx+1}",
                    columns=columns,
                    rows=rows,
                    source={"type": "url", "name": source_name},
                )
            )
    except Exception:
        return []
    return artifacts

