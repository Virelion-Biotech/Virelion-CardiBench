"""Versioned result observations for CardiBench benchmark history.

A result observation is evidence about one concrete evaluation run. Results are
never averaged or ranked across incompatible benchmark fingerprints/protocols.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

VALID_SPLITS={"validation","test","external"}

def _now_iso()->str: return datetime.now(timezone.utc).isoformat()
def _digest(value:Any)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

@dataclass(frozen=True)
class BenchmarkResultObservation:
    benchmark_id:str; benchmark_version:str; model_id:str; model_version:str; split:str; metrics:Mapping[str,float]; sample_count:int; benchmark_provenance_sha256:str
    protocol_id:str="default"; source:str="CardiEval"; artifact_uri:str|None=None; recorded_at:str=field(default_factory=_now_iso); notes:str=""; result_id:str=""
    def __post_init__(self)->None:
        for label,value in (("benchmark_id",self.benchmark_id),("benchmark_version",self.benchmark_version),("model_id",self.model_id),("model_version",self.model_version),("protocol_id",self.protocol_id),("source",self.source)):
            if not str(value).strip(): raise ValueError(f"{label} is required")
        if self.split not in VALID_SPLITS: raise ValueError(f"split must be one of {sorted(VALID_SPLITS)}")
        if self.sample_count<1: raise ValueError("sample_count must be positive")
        digest=self.benchmark_provenance_sha256.lower()
        if len(digest)!=64 or any(ch not in "0123456789abcdef" for ch in digest): raise ValueError("benchmark_provenance_sha256 must be a lowercase SHA-256 digest")
        cleaned={}
        for raw_name,raw_value in dict(self.metrics).items():
            name=str(raw_name).strip(); value=float(raw_value)
            if not name: raise ValueError("metric names must not be empty")
            if not math.isfinite(value): raise ValueError(f"metric {name} must be finite")
            cleaned[name]=value
        if not cleaned: raise ValueError("at least one metric is required")
        object.__setattr__(self,"metrics",dict(sorted(cleaned.items()))); object.__setattr__(self,"benchmark_provenance_sha256",digest)
        if not self.result_id:
            identity={"benchmark_id":self.benchmark_id,"benchmark_version":self.benchmark_version,"model_id":self.model_id,"model_version":self.model_version,"split":self.split,"metrics":cleaned,"sample_count":self.sample_count,"benchmark_provenance_sha256":digest,"protocol_id":self.protocol_id,"source":self.source,"artifact_uri":self.artifact_uri}
            object.__setattr__(self,"result_id",f"result-{_digest(identity)[:20]}")
    @property
    def comparability_key(self)->str:
        return "|".join((self.benchmark_id,self.benchmark_version,self.benchmark_provenance_sha256,self.split,self.protocol_id,self.source))
    def to_dict(self)->dict[str,Any]:
        value=asdict(self); value["metrics"]=dict(self.metrics); value["comparability_key"]=self.comparability_key; return value
    @classmethod
    def from_dict(cls,value:Mapping[str,Any])->"BenchmarkResultObservation":
        data=dict(value); data.pop("comparability_key",None); return cls(**data)

def load_result_history(path:str|Path)->list[BenchmarkResultObservation]:
    path=Path(path)
    if not path.exists(): return []
    raw=json.loads(path.read_text(encoding="utf-8")); raw=raw.get("results",[]) if isinstance(raw,dict) else raw
    if not isinstance(raw,list): raise ValueError("Result history must be a JSON array or {'results': [...]} object")
    return [BenchmarkResultObservation.from_dict(item) for item in raw]

def save_result_history(path:str|Path,results:Iterable[BenchmarkResultObservation])->None:
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); items=sorted(results,key=lambda item:(item.recorded_at,item.result_id)); payload={"schema_version":"1.0","results":[item.to_dict() for item in items]}; tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8"); tmp.replace(path)

def append_result(path:str|Path,result:BenchmarkResultObservation)->bool:
    items=load_result_history(path)
    if any(item.result_id==result.result_id for item in items): return False
    items.append(result); save_result_history(path,items); return True

def filter_results(results:Iterable[BenchmarkResultObservation],*,benchmark_id:str|None=None,model_id:str|None=None,split:str|None=None,comparability_key:str|None=None)->list[BenchmarkResultObservation]:
    out=list(results)
    if benchmark_id is not None: out=[item for item in out if item.benchmark_id==benchmark_id]
    if model_id is not None: out=[item for item in out if item.model_id==model_id]
    if split is not None: out=[item for item in out if item.split==split]
    if comparability_key is not None: out=[item for item in out if item.comparability_key==comparability_key]
    return sorted(out,key=lambda item:(item.recorded_at,item.result_id))

def metric_series(results:Iterable[BenchmarkResultObservation],metric:str,*,comparability_key:str)->list[dict[str,Any]]:
    return [{"result_id":item.result_id,"model_id":item.model_id,"model_version":item.model_version,"recorded_at":item.recorded_at,"metric":metric,"value":item.metrics[metric]} for item in filter_results(results,comparability_key=comparability_key) if metric in item.metrics]
