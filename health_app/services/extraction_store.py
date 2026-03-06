import json
import os
import threading
import time
from typing import Any, Dict, List, Optional

from django.conf import settings


_lock = threading.Lock()
_STORE_PATH = os.path.join(settings.BASE_DIR, "extracted_artifacts.json")


def _load_store() -> Dict[str, Any]:
    if not os.path.exists(_STORE_PATH):
        return {"artifacts": {}}
    try:
        with open(_STORE_PATH, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, dict) and "artifacts" in data:
                return data
    except json.JSONDecodeError:
        pass
    return {"artifacts": {}}


def _save_store(payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(_STORE_PATH), exist_ok=True)
    with open(_STORE_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def add_artifacts(session_id: str, artifacts: List[Dict[str, Any]]) -> None:
    if not artifacts:
        return
    with _lock:
        store = _load_store()
        art_index = store.setdefault("artifacts", {})
        timestamp = time.time()
        for artifact in artifacts:
            artifact_id = artifact.get("id")
            if not artifact_id:
                continue
            copy = json.loads(json.dumps(artifact))  # ensure primitives only
            copy["session_id"] = session_id
            copy["timestamp"] = timestamp
            art_index[artifact_id] = copy
        _save_store(store)


def get_artifact(artifact_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        art_index = _load_store().get("artifacts", {})
        return art_index.get(artifact_id)


def get_tables(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    with _lock:
        art_index = _load_store().get("artifacts", {})
        tables = [a for a in art_index.values() if a.get("type") == "table"]
        tables.sort(key=lambda a: a.get("timestamp", 0), reverse=True)
        if limit:
            return tables[:limit]
        return tables


def get_latest_table_with_column(column: str) -> Optional[Dict[str, Any]]:
    column_lower = column.lower()
    for table in get_tables():
        cols = [c.lower() for c in table.get("columns", [])]
        if column_lower in cols:
            return table
    return None

