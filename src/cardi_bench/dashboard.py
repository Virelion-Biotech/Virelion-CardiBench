"""Generate a dependency-free, read-only HTML dashboard for intelligence data."""
from __future__ import annotations

from html import escape
import json
from pathlib import Path
from typing import Any, Iterable

from .analytics import intelligence_summary
from .evidence import ResolvedCatalog
from .result_history import BenchmarkResultObservation


def _json_script(value: Any) -> str:
    return json.dumps(value, sort_keys=True).replace("</", "<\\/")


def render_dashboard(
    catalog: ResolvedCatalog,
    results: Iterable[BenchmarkResultObservation] = (),
    *,
    release: dict[str, Any] | None = None,
) -> str:
    result_items = list(results)
    summary = intelligence_summary(catalog, result_items)
    records = [item.to_dict() for item in catalog.records]
    result_rows = [item.to_dict() for item in result_items]
    release_id = str((release or {}).get("release_id") or "unreleased")

    record_html = "".join(
        "<tr data-search=\"" + escape(
            " ".join([
                item["canonical_name"],
                item["record_type"],
                " ".join(item.get("sources", [])),
                " ".join(str(v) for v in item.get("identifiers", {}).values()),
            ]).lower(),
            quote=True,
        ) + "\"><td>" + escape(item["canonical_name"]) + "</td><td>" +
        escape(item["record_type"]) + "</td><td>" +
        escape(", ".join(item.get("sources", []))) + "</td><td>" +
        escape(item.get("evidence_state", "unknown")) + "</td><td><code>" +
        escape(", ".join(f"{k}:{v}" for k, v in item.get("identifiers", {}).items())) +
        "</code></td></tr>"
        for item in records[:1000]
    )

    result_html = "".join(
        "<tr><td>" + escape(item["benchmark_id"]) + "</td><td>" +
        escape(item["model_id"]) + "</td><td>" + escape(item["split"]) +
        "</td><td>" + escape(item["source"]) + "</td><td><code>" +
        escape(", ".join(f"{k}={v:g}" for k, v in item["metrics"].items())) +
        "</code></td></tr>"
        for item in result_rows[:1000]
    )

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CardiBench Intelligence</title>
<style>
:root { color-scheme: light dark; font-family: Inter, system-ui, sans-serif; }
body { max-width: 1400px; margin: 0 auto; padding: 2rem; line-height: 1.45; }
header { display:flex; justify-content:space-between; gap:2rem; align-items:end; flex-wrap:wrap; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:1rem; margin:1.5rem 0; }
.card { border:1px solid #8886; border-radius:12px; padding:1rem; }
.card strong { display:block; font-size:1.8rem; }
input { width:min(100%,720px); padding:.75rem; margin:1rem 0; }
table { width:100%; border-collapse:collapse; font-size:.92rem; }
th,td { text-align:left; padding:.6rem; border-bottom:1px solid #8884; vertical-align:top; }
code { overflow-wrap:anywhere; }
.note { border-left:4px solid currentColor; padding:.75rem 1rem; opacity:.85; }
section { margin-top:2rem; overflow:auto; }
</style>
</head>
<body>
<header><div><h1>CardiBench Intelligence</h1><p>Read-only discovery, evidence, and protocol-scoped result view.</p></div>
<div><small>Release: <code>""" + escape(release_id) + """</code><br>Catalog generated: """ +
escape(str(catalog.generated_at)) + """</small></div></header>
<p class="note">Discovery evidence is not dataset admission, benchmark readiness, biological validity, or clinical validation. Search and dashboard views never mutate HeartTwin CardiacState.</p>
<div class="grid">
<div class="card"><span>Catalog records</span><strong>""" + str(summary["catalog"]["records"]) + """</strong></div>
<div class="card"><span>Evidence links</span><strong>""" + str(summary["catalog"]["links"]) + """</strong></div>
<div class="card"><span>Benchmark results</span><strong>""" + str(summary["results"]["results"]) + """</strong></div>
<div class="card"><span>Comparability groups</span><strong>""" + str(summary["results"]["comparability_groups"]) + """</strong></div>
</div>
<section><h2>Evidence catalog</h2>
<input id="filter" type="search" placeholder="Filter by title, type, source, or identifier">
<table><thead><tr><th>Name</th><th>Type</th><th>Sources</th><th>Evidence</th><th>Identifiers</th></tr></thead>
<tbody id="records">""" + record_html + """</tbody></table></section>
<section><h2>Result history</h2>
<table><thead><tr><th>Benchmark</th><th>Model</th><th>Split</th><th>Evaluator/source</th><th>Metrics</th></tr></thead>
<tbody>""" + result_html + """</tbody></table></section>
<script>
const input=document.getElementById("filter");
input.addEventListener("input",()=>{const q=input.value.toLowerCase();document.querySelectorAll("#records tr").forEach(row=>{row.hidden=!row.dataset.search.includes(q);});});
window.CARDIBENCH_SUMMARY=""" + _json_script(summary) + """;
</script>
</body></html>
"""


def write_dashboard(path: str | Path, html: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(html, encoding="utf-8")
    tmp.replace(path)
