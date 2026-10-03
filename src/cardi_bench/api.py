"""Stable JSON-shaped API consumed by HeartTwin."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any,Iterable,Mapping
from .admission import assess_admission
from .discovery import SOURCE_NAMES,run_discovery
from .evidence import CatalogRecord
from .intelligence_store import load_catalog
from .materialize import materialize
from .registry import Sample
from .result_history import BenchmarkResultObservation,append_result,filter_results,load_result_history
from .search import search_catalog

class CardiBenchAPI:
    contract_version="1.0"
    def invoke(self,capability:str,payload:Mapping[str,Any]|None=None)->dict[str,Any]:
        data=dict(payload or {}); dispatch={"benchmark.health":self.health,"benchmark.resolve":self.resolve,"benchmark.search":self.search,"benchmark.catalog":self.catalog,"benchmark.discover":self.discover,"benchmark.admission.assess":self.admission_assess,"benchmark.result.record":self.record_result,"benchmark.results":self.results}
        if capability not in dispatch: raise ValueError(f"CardiBench does not support {capability}")
        return dispatch[capability](data)
    @staticmethod
    def _catalog_path(payload):
        raw=payload.get("catalog_path") or os.getenv("CARDIBENCH_CATALOG"); return Path(str(raw)).expanduser() if raw else None
    @staticmethod
    def _result_path(payload):
        raw=payload.get("result_store") or os.getenv("CARDIBENCH_RESULTS"); return Path(str(raw)).expanduser() if raw else None
    def _records(self,payload):
        inline=payload.get("records")
        if inline is not None:
            if not isinstance(inline,list): raise ValueError("records must be an array")
            return [item if isinstance(item,CatalogRecord) else CatalogRecord.from_dict(item) for item in inline]
        path=self._catalog_path(payload)
        if path is None:return []
        if not path.is_file(): raise ValueError(f"CardiBench catalog does not exist: {path}")
        return list(load_catalog(path).records)
    def health(self,payload=None):
        payload=dict(payload or {}); cp=self._catalog_path(payload); rp=self._result_path(payload)
        return {"contract_version":self.contract_version,"status":"ok","capabilities":["benchmark.health","benchmark.resolve","benchmark.search","benchmark.catalog","benchmark.discover","benchmark.admission.assess","benchmark.result.record","benchmark.results"],"catalog":{"configured":cp is not None,"exists":bool(cp and cp.is_file()),"path":str(cp) if cp else None},"results":{"configured":rp is not None,"exists":bool(rp and rp.is_file()),"path":str(rp) if rp else None}}
    def resolve(self,payload):
        raw_samples=payload.get("samples") or []
        if not isinstance(raw_samples,list): raise ValueError("samples must be an array")
        samples=[Sample(sample_id=str(i["sample_id"]),group_id=str(i["group_id"]),study_id=str(i["study_id"]),label=str(i["label"]),technical_group=i.get("technical_group"),organism=i.get("organism"),timepoint=i.get("timepoint"),cell_context=i.get("cell_context"),region=i.get("region")) for i in raw_samples]
        result=materialize(samples,benchmark_id=str(payload.get("benchmark_id","hearttwin-e2e")),version=str(payload.get("version","1.0")),policy=str(payload.get("policy","subject_heldout")),test_values={str(i) for i in payload.get("test_values",[])},validation_values={str(i) for i in payload.get("validation_values",[])},seed=int(payload.get("seed",0)))
        data=result.to_dict(); data.pop("label_counts",None); return {"contract_version":self.contract_version,**data,"samples":raw_samples}
    def search(self,payload):
        query=str(payload.get("query") or "").strip()
        if not query: raise ValueError("query is required")
        return {"contract_version":self.contract_version,**search_catalog(self._records(payload),query,limit=int(payload.get("limit",20)))}
    def catalog(self,payload):
        records=self._records(payload); rt=payload.get("record_type"); source=payload.get("source")
        if rt: records=[i for i in records if i.record_type==str(rt)]
        if source: records=[i for i in records if str(source).lower() in i.sources]
        limit=int(payload.get("limit",100))
        if limit<0 or limit>10000: raise ValueError("limit must be between 0 and 10000")
        return {"contract_version":self.contract_version,"count":len(records),"records":[i.to_dict() for i in records[:limit]]}
    def discover(self,payload):
        raw=payload.get("sources")
        if raw is None:sources=SOURCE_NAMES
        elif isinstance(raw,str):sources=[i.strip() for i in raw.split(",") if i.strip()]
        elif isinstance(raw,list):sources=[str(i) for i in raw]
        else:raise ValueError("sources must be an array or comma-separated string")
        batch=run_discovery(query=str(payload["query"]) if payload.get("query") else None,sources=sources,limit=int(payload.get("limit",25)),lookback_days=int(payload.get("lookback_days",30)))
        return {"contract_version":self.contract_version,**batch.to_dict()}
    def admission_assess(self,payload):
        raw=payload.get("samples") or []
        if not isinstance(raw,list):raise ValueError("samples must be an array")
        report=assess_admission(raw,policy=str(payload.get("policy","subject_heldout")),benchmark_id=str(payload.get("benchmark_id","candidate")),version=str(payload.get("version","1.0")),test_values=payload.get("test_values") or [],validation_values=payload.get("validation_values") or [],seed=int(payload.get("seed",0)))
        return {"contract_version":self.contract_version,**report.to_dict()}
    def record_result(self,payload):
        data=dict(payload); data.pop("entity_id",None); store=data.pop("result_store",None); raw_metrics=data.get("metrics")
        if isinstance(raw_metrics,list):
            data["metrics"]={str(i["name"]):float(i["value"]) for i in raw_metrics if isinstance(i,Mapping) and "name" in i and "value" in i}
        if "benchmark_provenance_sha256" not in data and data.get("benchmark_sha256"): data["benchmark_provenance_sha256"]=data.pop("benchmark_sha256")
        evaluator_version=data.pop("evaluator_version",None); data.setdefault("model_version","unknown"); data.setdefault("protocol_id",str(data.pop("task_id","default") or "default")); data.setdefault("source",f"CardiEval/{evaluator_version}" if evaluator_version else "CardiEval")
        if "sample_count" not in data and isinstance(raw_metrics,list):
            counts=[int(i["n"]) for i in raw_metrics if isinstance(i,Mapping) and i.get("n") is not None]
            if counts:data["sample_count"]=max(counts)
        allowed={"benchmark_id","benchmark_version","model_id","model_version","split","metrics","sample_count","benchmark_provenance_sha256","protocol_id","source","artifact_uri","recorded_at","notes","result_id"}; result=BenchmarkResultObservation.from_dict({k:v for k,v in data.items() if k in allowed}); path=Path(str(store)).expanduser() if store else self._result_path(payload); persisted=append_result(path,result) if path is not None else False
        return {"contract_version":self.contract_version,"persisted":persisted,"result":result.to_dict()}
    def results(self,payload):
        inline=payload.get("results")
        if inline is not None:
            if not isinstance(inline,list): raise ValueError("results must be an array")
            items=[BenchmarkResultObservation.from_dict(i) for i in inline]
        else:
            path=self._result_path(payload); items=load_result_history(path) if path is not None else []
        filtered=filter_results(items,benchmark_id=str(payload["benchmark_id"]) if payload.get("benchmark_id") else None,model_id=str(payload["model_id"]) if payload.get("model_id") else None,split=str(payload["split"]) if payload.get("split") else None,comparability_key=str(payload["comparability_key"]) if payload.get("comparability_key") else None); limit=int(payload.get("limit",100))
        if limit<0 or limit>10000: raise ValueError("limit must be between 0 and 10000")
        return {"contract_version":self.contract_version,"count":len(filtered),"results":[i.to_dict() for i in filtered[:limit]]}
