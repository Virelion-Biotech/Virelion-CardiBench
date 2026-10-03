"""Command-line interface for CardiBench integrity and intelligence workflows."""
from __future__ import annotations
import argparse,json
from datetime import date
from pathlib import Path
from .catalog import BENCHMARK_FAMILIES
from .discovery import SOURCE_NAMES,run_discovery
from .intelligence_store import build_catalog,load_catalog,save_discovery_batch
from .manifest import assert_valid_manifest
from .release import audit_repository_paths
from .result_history import BenchmarkResultObservation,append_result,filter_results,load_result_history
from .search import search_catalog

def _load_json(path:Path):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:raise SystemExit(f"Cannot read {path}: {exc}") from exc
def _validate_manifest(path:Path)->bool:
    try:assert_valid_manifest(_load_json(path))
    except (SystemExit,ValueError) as exc:print(f"INVALID: {path}: {exc}"); return False
    print(f"valid: {path}"); return True
def _source_list(value:str):
    items=[i.strip().lower() for i in value.split(",") if i.strip()]; unknown=sorted(set(items)-set(SOURCE_NAMES))
    if unknown:raise argparse.ArgumentTypeError(f"unknown sources: {', '.join(unknown)}")
    return items

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(prog="cardibench"); sub=p.add_subparsers(dest="command",required=True)
    x=sub.add_parser("validate-manifest"); x.add_argument("path",type=Path)
    x=sub.add_parser("validate-all-manifests"); x.add_argument("root",nargs="?",type=Path,default=Path("benchmarks/manifests"))
    x=sub.add_parser("list-benchmarks"); x.add_argument("--json",action="store_true",dest="as_json")
    x=sub.add_parser("audit"); x.add_argument("root",nargs="?",type=Path,default=Path(".")); x.add_argument("--strict",action="store_true")
    x=sub.add_parser("discover"); x.add_argument("--query"); x.add_argument("--sources",type=_source_list,default=list(SOURCE_NAMES)); x.add_argument("--limit",type=int,default=25); x.add_argument("--lookback-days",type=int,default=30); x.add_argument("--output",type=Path,default=Path("data/intelligence/snapshots")/f"{date.today().isoformat()}.json")
    x=sub.add_parser("build-catalog"); x.add_argument("--snapshots-dir",type=Path,default=Path("data/intelligence/snapshots")); x.add_argument("--output",type=Path,default=Path("data/intelligence/catalog.json")); x.add_argument("--overrides",type=Path)
    x=sub.add_parser("search"); x.add_argument("query"); x.add_argument("--catalog",type=Path,default=Path("data/intelligence/catalog.json")); x.add_argument("--limit",type=int,default=20); x.add_argument("--json",action="store_true",dest="as_json")
    x=sub.add_parser("record-result"); x.add_argument("path",type=Path); x.add_argument("--store",type=Path,default=Path("data/intelligence/results.json"))
    x=sub.add_parser("list-results"); x.add_argument("--store",type=Path,default=Path("data/intelligence/results.json")); x.add_argument("--benchmark-id"); x.add_argument("--model-id"); x.add_argument("--split"); x.add_argument("--comparability-key"); x.add_argument("--json",action="store_true",dest="as_json")
    a=p.parse_args(argv)
    if a.command=="validate-manifest":return 0 if _validate_manifest(a.path) else 1
    if a.command=="validate-all-manifests":
        paths=sorted(a.root.glob("*.json")); return 0 if paths and all(_validate_manifest(q) for q in paths) else 1
    if a.command=="list-benchmarks":
        rows=[{"id":f.benchmark_id,"task":f.task,"group":f.preferred_group_key,"metrics":list(f.primary_metrics)} for f in BENCHMARK_FAMILIES]
        print(json.dumps(rows,indent=2) if a.as_json else "\n".join(f"{r['id']}: {r['task']} [{r['group']}]" for r in rows)); return 0
    if a.command=="audit":
        result=audit_repository_paths([str(q.relative_to(a.root)) for q in a.root.rglob("*") if q.is_file()]); [print(f"ERROR: {e}") for e in result.errors]; [print(f"WARNING: {w}") for w in result.warnings]; passed=result.passed and (not a.strict or not result.warnings); print("AUDIT PASS" if passed else "AUDIT FAIL"); return 0 if passed else 1
    if a.command=="discover":
        batch=run_discovery(query=a.query,sources=a.sources,limit=a.limit,lookback_days=a.lookback_days); save_discovery_batch(a.output,batch); print(json.dumps({"output":str(a.output),"observations":len(batch.observations),"healthy_sources":batch.healthy_sources,"sources":[r.to_dict() for r in batch.source_runs]},indent=2)); return 0 if batch.healthy_sources else 1
    if a.command=="build-catalog":
        snaps=sorted(a.snapshots_dir.glob("*.json"));
        if not snaps: print(f"No discovery snapshots found under {a.snapshots_dir}"); return 1
        overrides=None
        if a.overrides:
            raw=_load_json(a.overrides); overrides=dict(raw.get("record_for_observation",raw))
        catalog=build_catalog(snaps,output=a.output,overrides=overrides); print(json.dumps({"output":str(a.output),"records":len(catalog.records),"links":len(catalog.links)},indent=2)); return 0
    if a.command=="search":
        result=search_catalog(load_catalog(a.catalog).records,a.query,limit=a.limit); print(json.dumps(result,indent=2) if a.as_json else "\n".join(f"{h['record']['record_id']}\t{h['retrieval_score']:.4f}\t{h['record']['canonical_name']}" for h in result["results"])); return 0
    if a.command=="record-result":
        result=BenchmarkResultObservation.from_dict(_load_json(a.path)); added=append_result(a.store,result); print(json.dumps({"store":str(a.store),"added":added,"result_id":result.result_id},indent=2)); return 0
    if a.command=="list-results":
        items=filter_results(load_result_history(a.store),benchmark_id=a.benchmark_id,model_id=a.model_id,split=a.split,comparability_key=a.comparability_key); print(json.dumps([i.to_dict() for i in items],indent=2) if a.as_json else "\n".join(f"{i.result_id}\t{i.benchmark_id}\t{i.model_id}" for i in items)); return 0
    return 2
if __name__=="__main__":raise SystemExit(main())
