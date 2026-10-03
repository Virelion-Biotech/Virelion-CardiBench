"""Deterministic intelligence release bundles."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .analytics import intelligence_summary
from .intelligence_store import load_catalog
from .result_history import load_result_history


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_release_bundle(
    catalog_path: str | Path,
    *,
    results_path: str | Path | None = None,
) -> dict[str, Any]:
    catalog_path = Path(catalog_path)
    catalog_raw = _read_json(catalog_path)
    catalog = load_catalog(catalog_path)

    result_raw: Any = {"schema_version": "1.0", "results": []}
    results = []
    result_path_obj: Path | None = None
    if results_path is not None:
        result_path_obj = Path(results_path)
        if result_path_obj.is_file():
            result_raw = _read_json(result_path_obj)
            results = load_result_history(result_path_obj)

    catalog_sha = _sha256(catalog_raw)
    results_sha = _sha256(result_raw)
    identity = {
        "schema_version": "1.0",
        "catalog_sha256": catalog_sha,
        "results_sha256": results_sha,
    }
    release_id = "cardibench-intelligence-" + _sha256(identity)[:20]
    return {
        **identity,
        "release_id": release_id,
        "catalog_generated_at": catalog.generated_at,
        "catalog_file": catalog_path.name,
        "results_file": result_path_obj.name if result_path_obj else None,
        "summary": intelligence_summary(catalog, results),
    }


def save_release_bundle(path: str | Path, bundle: dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)
