"""Filesystem persistence for CardiBench discovery/catalog products."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Iterable
from .discovery import DiscoveryBatch
from .evidence import ResolvedCatalog, SourceObservation
from .identity import resolve_observations

def _atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8"); tmp.replace(path)
def save_discovery_batch(path:str|Path,batch:DiscoveryBatch)->None: _atomic_json(Path(path),batch.to_dict())
def load_discovery_batch(path:str|Path)->DiscoveryBatch: return DiscoveryBatch.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
def load_observations(paths:Iterable[str|Path])->list[SourceObservation]:
    observations={}
    for raw_path in paths:
        for item in load_discovery_batch(raw_path).observations: observations[item.observation_id]=item
    return sorted(observations.values(),key=lambda item:item.observation_id)
def save_catalog(path:str|Path,catalog:ResolvedCatalog)->None: _atomic_json(Path(path),catalog.to_dict())
def load_catalog(path:str|Path)->ResolvedCatalog: return ResolvedCatalog.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
def build_catalog(snapshot_paths:Iterable[str|Path],*,output:str|Path|None=None,overrides:dict[str,str]|None=None)->ResolvedCatalog:
    catalog=resolve_observations(load_observations(snapshot_paths),overrides=overrides)
    if output is not None: save_catalog(output,catalog)
    return catalog
