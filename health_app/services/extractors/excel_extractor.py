import os
from typing import List, Dict, Any

import pandas as pd

from .normalizer import normalize_table


def extract_from_excel(path: str) -> List[Dict[str, Any]]:
    artifacts: List[Dict[str, Any]] = []
    try:
        extension = os.path.splitext(path)[1].lower()
        if extension == ".csv":
            df = pd.read_csv(path)
            _append_dataframe(artifacts, df, sheet="CSV", source_path=path)
        else:
            xls = pd.ExcelFile(path)
            for sheet in xls.sheet_names:
                try:
                    df = pd.read_excel(path, sheet_name=sheet)
                    _append_dataframe(artifacts, df, sheet=sheet, source_path=path)
                except Exception:
                    continue
    except Exception:
        return []
    return artifacts


def _append_dataframe(artifacts: List[Dict[str, Any]], df: pd.DataFrame, sheet: str, source_path: str) -> None:
    if df is None or df.empty:
        return
    df = df.dropna(how="all")
    if df.empty:
        return
    df = df.loc[:, ~df.columns.duplicated()]
    columns = [str(c) if c is not None else f"Column {idx+1}" for idx, c in enumerate(df.columns.tolist())]
    rows = df.where(pd.notnull(df), None).values.tolist()
    artifacts.append(
        normalize_table(
            title=f"{sheet}",
            columns=columns,
            rows=rows,
            source={"type": "file", "name": source_path, "sheet": sheet},
        )
    )
